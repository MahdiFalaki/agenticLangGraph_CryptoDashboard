import math
import os
from typing import List, Dict, Any, TypedDict
from dotenv import load_dotenv
from IPython.display import Image, display

from langgraph.graph import StateGraph, START, END
from openai import OpenAI

load_dotenv()


# _____________________________________________State Section____________________________________________________
class AgentState(TypedDict, total=False):
    mode: str  # which task: "overview" | "ask_AI" | "history"

    symbol: str  # "BTC" / "ETH" / "AAPL", etc.

    start_date: str  # start of chart window (used in overview/history)
    end_date: str  # same as above

    indicators: Dict[str, float]  # start_price, end_price, return_pct, max_drawdown_pct

    chart: List[Dict[str, float | str]]

    news: List[Dict[str, Any]]  # list of news items (title, snippet, published_at, url)

    docs: List[Dict[str, str]]  # list of search docs for background mode

    question: str  # user question (Ask-AI mode only)

    chart_text: str  # preprocessed string from compress_chart_node
    news_text: str  # preprocessed string from format_news_node
    context_text: str  # preprocessed string from build_context_node

    answer: str  # final output from the LLM task node


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# _____________________________________________Nodes____________________________________________________
def router(state: AgentState) -> str:
    """Router function based on mode."""
    mode = state.get("mode")

    if mode == "overview":
        return "overview"
    elif mode == "ask_AI":
        return "ask_AI"
    elif mode == "history":
        return "history"


def chart_compression(state: AgentState) -> AgentState:
    """This node is for returning a good-sized chart in form of string
    for llm. If chart is too long  it will return compressed version. """
    chart = state["chart"].copy()

    if not chart:
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

    # # test-only
    # print(state["chart_text"])

    return state


def fetch_news(state: AgentState) -> AgentState:
    """This node is for getting the news and writing it in a string format, so we can feed it to llm."""
    news = state["news"].copy()
    if not news:
        # Only warn when we're actually in Ask AI mode
        if state.get("mode") == "ask_AI":
            print(
                "No relevant news articles were available for this period "
                "or the NewsAPI may not have returned results."
            )
        return state

    news_text = "".join(f'published at: {i["published_at"]} \n '
                        f'title: {i["title"]} \n'
                        f'snippet: {i["snippet"]} \n'
                        f'URL: {i["url"]} \n'
                        for i in news)

    state["news_text"] = news_text

    # # test-only
    # print(state["news_text"])

    return state


def build_context(state: AgentState) -> AgentState:
    """This node is for getting all the docs for a single symbol and returning a context
    text for the llm to work in the history part or probably the askAI part."""
    symbol = state["symbol"]
    docs = state["docs"].copy()

    if not docs:
        state["context_text"] = (f'This is supposed to be a historical overview of {symbol}, '
                                 f'but no background documents were available from the search engine.')
        return state

    docs_text = "".join(f'[Source {idx+1}] \n'
                        f'title: {d["title"]} \n'
                        f'snippet: {d["snippet"]} \n'
                        f'url: {d["url"]} \n'
                        f'published_at: {d["published_at"]} \n'
                        for idx, d in enumerate(docs))

    state["context_text"] = docs_text

    # # test-only
    # print(state["context_text"])

    return state


def overview(state: AgentState) -> AgentState:
    """ Use the LLM to generate a short natural-language summary of price
    action  in the selected date range, based ONLY on price data (no news)."""
    symbol = state["symbol"]
    start_date = state["start_date"]
    end_date = state["end_date"]
    indicators = state["indicators"]
    chart_text = state["chart_text"]

    prompt = f"""
    You are a financial analyst.

    You are given price data for {symbol} between {start_date} and {end_date}.
    Summarize the important changes in price and overall trend in 3–5 sentences.
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
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a concise, factual financial analyst."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    state["answer"] = answer.choices[0].message.content.strip()

    # # test-only
    # print(state["answer"])

    return state


def ask_AI(state: AgentState) -> AgentState:
    """Use the LLM to answer a user question using indicators + news, with a RAG-style grounding pass."""
    symbol = state["symbol"]
    indicators = state["indicators"]
    news_text = state.get("news_text", "No relevant news articles were available for this period.")
    question = state["question"]

    # ------------------ 1) Draft answer ------------------
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
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a concise, factual financial analyst."},
            {"role": "user", "content": draft_prompt},
        ],
        temperature=0.3,
    )
    draft_text = draft.choices[0].message.content.strip()

    # ------------------ 2) Verification / grounding pass ------------------
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
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a strict fact-checker. "
                                          "You only allow statements grounded in the given news and indicators."},
            {"role": "user", "content": verify_prompt},
        ],
        temperature=0.1,
    )

    state["answer"] = final.choices[0].message.content.strip()

    # # test-only
    # print(state["answer"])

    return state


def history(state: AgentState) -> AgentState:
    """Generate a background history that is explicitly grounded in docs via a 2-pass RAG process."""
    symbol = state["symbol"]
    context_text = state["context_text"]

    # ------------------ 1) Draft answer ------------------
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
    - Optionally reference sources like “(Source 1)” when you use them.

    Sources:
    {context_text}

    Now write 2–4 short paragraphs in clear, accessible language."""

    draft = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a careful, neutral crypto historian. "
                           "You only use the information provided in the context."
            },
            {"role": "user", "content": draft_prompt},
        ],
        temperature=0.3,
    )
    draft_text = draft.choices[0].message.content.strip()

    # ------------------ 2) Verification / grounding pass ------------------
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
    - Keep the final answer concise (2–4 short paragraphs).
    """

    final = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a strict fact-checker. You only allow statements that are "
                           "supported by the given sources."
            },
            {"role": "user", "content": verify_prompt},
        ],
        temperature=0.1,
    )

    state["answer"] = final.choices[0].message.content.strip()

    # # for test-only
    # print(state["answer"])

    return state


# _____________________________________________Graph Section____________________________________________________
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

# _____________________________________________Test Section____________________________________________________
# fake_docs = [
#     {
#         "title": "Bitcoin: A Peer-to-Peer Electronic Cash System",
#         "snippet": "Bitcoin was introduced in 2008 by the anonymous figure Satoshi Nakamoto...",
#         "url": "https://bitcoin.org/bitcoin.pdf",
#         "published_at": "2008-10-31",
#     },
#     {
#         "title": "Early Bitcoin Market Growth",
#         "snippet": "In its early years, Bitcoin was mainly used on niche internet forums...",
#         "url": "https://example.com/btc-history-2011",
#         "published_at": "2011-06-15",
#     },
#     {
#         "title": "The 2017 Crypto Bull Run",
#         "snippet": "Bitcoin reached nearly $20,000 amid unprecedented retail investor interest...",
#         "url": "https://example.com/btc-2017-bullrun",
#         "published_at": "2017-12-17",
#     },
#     {
#         "title": "Regulatory Developments in 2021",
#         "snippet": "Multiple countries announced new frameworks for digital asset oversight...",
#         "url": "https://example.com/btc-regulation-2021",
#         "published_at": "2021-06-30",
#     },
# ]
#
# fake_news = [
#     {
#         "published_at": "2024-01-05",
#         "title": "BTC jumps after ETF news",
#         "snippet": "Bitcoin rallied after reports of ETF approval...",
#         "url": "https://example.com/article-1",
#     },
#     {
#         "published_at": "2024-01-06",
#         "title": "Market cools down",
#         "snippet": "Crypto market saw mild profit-taking...",
#         "url": "https://example.com/article-2",
#     },
# ]
#
# chart = [
#     {"date": f"2024-01-{str(i).zfill(2)}", "price": 42000 + (i * 35) % 700 - (i * 12)}
#     for i in range(1, 31)
# ]
#
# test_state = {
#     "chart": chart,
#     "news": fake_news,
#     "docs": fake_docs,
#     "symbol": "BTC",
#     "start_date": "2024-01-01",
#     "end_date": "2024-01-31",
#     "indicators": {
#         "start_price": 42000.0,
#         "end_price": 44500.0,
#         "return_pct": 5.9,
#         "max_drawdown_pct": -3.2,
#     },
#     "question": "Why did BTC move the way it did during this period?",
# }
#
# agent.invoke(test_state)
#
# # # For visualizing the graph.
# # display(Image(agent.get_graph().draw_mermaid_png()))
#
