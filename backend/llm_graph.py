"""LangGraph workflow for overview, Q&A, and background brief generation."""

import math
import os
from typing import List, Dict, Any, TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from openai import OpenAI

load_dotenv()


class AgentState(TypedDict, total=False):
    """Shared state container passed across graph nodes."""
    mode: str

    symbol: str

    start_date: str
    end_date: str

    indicators: Dict[str, float]

    chart: List[Dict[str, float | str]]

    news: List[Dict[str, Any]]

    docs: List[Dict[str, str]]

    question: str

    chart_text: str
    news_text: str
    context_text: str

    answer: str


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def router(state: AgentState) -> str:
    """Route state to the correct graph branch."""
    mode = state.get("mode")

    if mode == "overview":
        return "overview"
    elif mode == "ask_AI":
        return "ask_AI"
    elif mode == "history":
        return "history"
    raise ValueError(f"Unsupported agent mode: {mode}")


def chart_compression(state: AgentState) -> AgentState:
    """Compress chart points into a concise text block for prompting."""
    chart = state["chart"].copy()

    if not chart:
        if state.get("mode") == "overview":
            print("chart is empty!")
        return state

    if len(chart) > 20:
        step = math.ceil(len(chart) / 20)
        chart = chart[::step]

    chart_text = "".join(
        f'{i["date"]}: {i["price"]:.2f} \n'
        for i in chart
    )

    state["chart_text"] = chart_text

    return state


def fetch_news(state: AgentState) -> AgentState:
    """Convert news items to prompt text."""
    news = state["news"].copy()
    if not news:
        # Warn only for Q&A flow where news is expected.
        if state.get("mode") == "ask_AI":
            print(
                "No relevant news articles were available for this period "
                "or the NewsAPI may not have returned results."
            )
        return state

    news_text = "".join(f'published at: {i["published_at"]} \n '
                        f'title: {i["title"]} \n'
                        f'content: {i["content"]} \n'
                        f'URL: {i["url"]} \n'
                        for i in news)

    state["news_text"] = news_text

    return state


def build_context(state: AgentState) -> AgentState:
    """Convert source docs to a single context text block."""
    symbol = state["symbol"]
    docs = state["docs"].copy()

    if not docs:
        state["context_text"] = (f'This is supposed to be a historical overview of {symbol}, '
                                 f'but no background documents were available from the search engine.')
        return state

    docs_text = "".join(
        f'[Source {idx+1}] \n'
        f'title: {d.get("title", "")} \n'
        f'content: {d.get("content") or d.get("snippet", "")} \n'
        f'url: {d.get("url", "")} \n'
        f'published_at: {d.get("published_at", "")} \n'
        for idx, d in enumerate(docs)
    )

    state["context_text"] = docs_text

    return state


def overview(state: AgentState) -> AgentState:
    """Generate a short market summary from price data."""
    symbol = state["symbol"]
    start_date = state["start_date"]
    end_date = state["end_date"]
    indicators = state["indicators"]
    chart_text = state["chart_text"]

    prompt = f"""
    You are a financial analyst.

    You are given price data for {symbol} between {start_date} and {end_date}.
    Summarize the important changes in price and overall trend in 3-5 sentences.
    Be concrete with numbers (approximate is fine) and DO NOT give any investment advice.

    Indicators:
    - Start price: {indicators['start_price']}
    - End price: {indicators['end_price']}
    - Return (%): {indicators['return_pct']}
    - Max drawdown (%): {indicators['max_drawdown_pct']}

    Sampled prices over time:
    {chart_text}

    Write a clear, human-friendly paragraph describing:
    - overall direction (up, down, sideways),
    - approximate magnitude of moves,
    - whether the path was smooth or volatile,
    - where major dips or peaks occurred (dates + approximate levels).
    """

    answer = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a concise, factual financial analyst."},
            {"role": "user", "content": prompt},
        ],
    )
    state["answer"] = answer.choices[0].message.content.strip()

    return state


def ask_AI(state: AgentState) -> AgentState:
    """Answer a market question using indicators and news."""
    symbol = state["symbol"]
    indicators = state["indicators"]
    news_text = state.get("news_text", "No relevant news articles were available for this period.")
    question = state["question"]

    # Draft response.
    draft_prompt = f""" 
    You are a financial analyst.

    A user is asking a question about {symbol}. Use the numeric indicators and
    the recent news headlines to answer. You are allowed to speculate about
    possible causes, but you must use cautious language like "likely", "may",
    or "could", and you must NOT give investment advice.

    Asset: {symbol}

    Indicators:
    - Start price: {indicators['start_price']}
    - End price: {indicators['end_price']}
    - Return (%): {indicators['return_pct']}
    - Max drawdown (%): {indicators['max_drawdown_pct']}

    Recent news:
    {news_text}

    User question:
    \"\"\"{question}\"\"\"

    Answer in a few concise paragraphs. Clearly explain how the price moved
    and how the news might relate to that move. Do not mention that you are an AI.
    """

    draft = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a concise, factual financial analyst."},
            {"role": "user", "content": draft_prompt},
        ],
    )
    draft_text = draft.choices[0].message.content.strip()

    # Grounded rewrite pass.
    verify_prompt = f"""
    You are verifying an answer about {symbol} against the available news and price indicators.

    Indicators:
    - Start price: {indicators['start_price']}
    - End price: {indicators['end_price']}
    - Return (%): {indicators['return_pct']}
    - Max drawdown (%): {indicators['max_drawdown_pct']}

    News:
    {news_text}

    Draft answer:
    \"\"\"{draft_text}\"\"\"

    Task:
    - Rewrite the answer so that every factual claim is clearly supported by the news and/or indicators.
    - Remove or soften any claims that are not clearly grounded in the news or indicators.
    - If the user's question cannot be directly answered from these news articles and indicators,
      explicitly say that the available news and price data do not directly answer the question.
    - Do NOT introduce any new facts beyond what appears in the news text or indicators.
    - It is OK to explain uncertainty, but do not fabricate unseen events or news.
    """

    final = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a strict fact-checker. "
                                          "You only allow statements grounded in the given news and indicators."},
            {"role": "user", "content": verify_prompt},
        ],
    )

    state["answer"] = final.choices[0].message.content.strip()

    return state


def history(state: AgentState) -> AgentState:
    """Generate a grounded background brief from source docs."""
    symbol = state["symbol"]
    context_text = state["context_text"]

    # Draft response.
    draft_prompt = f"""You are a crypto historian. Using ONLY the information in the sources below, 
    write a concise but rich background history for the asset {symbol} (a cryptocurrency).

    Your draft must:
    - Focus on long-term history, not just recent price moves.
    - Cover, when possible:
      * its creation or launch,
      * who created it (if known),
      * what problem it tries to solve,
      * key technical ideas (briefly),
      * major protocol upgrades or forks,
      * important historical events (bubbles, crashes, regulatory moments, hacks, etc.).
    - Mention specific years or rough dates when you can.
    - Stay factual and neutral. No investment advice or price predictions.
    - Optionally reference sources like "(Source 1)" when you use them.

    Sources:
    {context_text}

    Now write 2-4 short paragraphs in clear, accessible language."""

    draft = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {
                "role": "system",
                "content": "You are a careful, neutral crypto historian. "
                           "You only use the information provided in the context."
            },
            {"role": "user", "content": draft_prompt},
        ],
    )
    draft_text = draft.choices[0].message.content.strip()

    # Grounded rewrite pass.
    verify_prompt = f"""
    You are verifying a draft historical summary about {symbol} against the sources.

    Sources:
    {context_text}

    Draft summary:
    \"\"\"{draft_text}\"\"\"

    Task:
    - Rewrite the summary so that EVERY factual claim is directly supported by the sources.
    - Remove or soften any claims that are not clearly grounded in the sources.
    - If specific details (dates, names, events) are not in the sources, do NOT invent them.
    - If some part of the requested history is not covered by the sources, explicitly say
      that the sources do not provide that information.
    - Do NOT add any new facts beyond what appears in the Sources.
    - Keep the final answer concise (2-4 short paragraphs).
    """

    final = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {
                "role": "system",
                "content": "You are a strict fact-checker. You only allow statements that are "
                           "supported by the given sources."
            },
            {"role": "user", "content": verify_prompt},
        ],
    )

    state["answer"] = final.choices[0].message.content.strip()

    return state


graph = StateGraph(AgentState)

graph.add_node("router", lambda state: state)
graph.add_node("chart_compression", chart_compression)
graph.add_node("fetch_news", fetch_news)
graph.add_node("build_context", build_context)
graph.add_node("overview", overview)
graph.add_node("ask_AI", ask_AI)
graph.add_node("history", history)

graph.add_edge(START, "chart_compression")
graph.add_edge("chart_compression", "fetch_news")
graph.add_edge("fetch_news", "build_context")
graph.add_edge("build_context", "router")
graph.add_conditional_edges("router",
                            router,
                            {
                                "overview": "overview",
                                "ask_AI": "ask_AI",
                                "history": "history"
                            }
                            )
graph.add_edge("overview", END)
graph.add_edge("ask_AI", END)
graph.add_edge("history", END)

agent = graph.compile()

