# backend/llm_client.py

import os
from typing import List, Dict, Any

from openai import OpenAI

# Create a single OpenAI client using the API key from .env
# Make sure you have OPENAI_API_KEY set in your environment.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ---------------------------------------------------------------------
# 1) OVERVIEW TAB – summarize price action only
# ---------------------------------------------------------------------
def summarize_price_action(
    symbol: str,
    start_date: str,
    end_date: str,
    indicators: Dict[str, float],
    chart: List[Dict[str, Any]],
) -> str:
    """
    Use the LLM to generate a short natural-language summary of price action
    in the selected date range, based ONLY on price data (no news).
    """

    # Compress chart if it has too many points to avoid sending huge payloads
    if len(chart) > 60:
        step = max(1, len(chart) // 60)
        compressed_chart = chart[::step]
    else:
        compressed_chart = chart

    chart_lines = [f"{pt['date']}: {pt['price']:.2f}" for pt in compressed_chart]
    chart_text = "\n".join(chart_lines)

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

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a concise, factual financial analyst."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------
# 2) ASK AI TAB – answer custom question using indicators + news
# ---------------------------------------------------------------------
def answer_price_question(
    symbol: str,
    indicators: Dict[str, float],
    news: List[Dict[str, Any]],
    question: str,
) -> str:
    """
    Use the LLM to answer a user question about the asset's move,
    using both numeric indicators and a list of recent news articles.
    """

    # Turn news into a compact bullet list for the prompt
    if news:
        news_lines = []
        for i, item in enumerate(news, start=1):
            # Each item should have title, snippet, published_at, url
            news_lines.append(
                f"{i}. {item['published_at']}: {item['title']} — {item['snippet']} (URL: {item['url']})"
            )
        news_text = "\n".join(news_lines)
    else:
        news_text = "No relevant news articles were available for this period."

    prompt = f"""
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

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a concise, factual financial analyst."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()


# ---------------------------------------------------------------------
# 3) HISTORY TAB – narrative story using price path + news
# ---------------------------------------------------------------------
def generate_history_story(
    symbol: str,
    start_date: str,
    end_date: str,
    chart: List[Dict[str, Any]],
    news: List[Dict[str, Any]],
    indicators: Dict[str, float],
) -> str:
    """
    Generate a 'history story' for the deactivateselected period.

    This should:
    - describe the path of the price (peaks, dips, volatility),
    - connect important moves to specific news headlines when plausible,
    - stay factual and avoid investment advice.
    """

    # Compress chart as before to avoid huge prompts
    if len(chart) > 60:
        step = max(1, len(chart) // 60)
        compressed_chart = chart[::step]
    else:
        compressed_chart = chart

    chart_lines = [f"{pt['date']}: {pt['price']:.2f}" for pt in compressed_chart]
    chart_text = "\n".join(chart_lines)

    if news:
        news_lines = []
        for i, item in enumerate(news, start=1):
            news_lines.append(
                f"{i}. {item['published_at']}: {item['title']} — {item['snippet']}"
            )
        news_text = "\n".join(news_lines)
    else:
        news_text = "No major news headlines were captured for this period."

    prompt = f"""
You are a financial market historian.

Write a narrative 'history story' for {symbol} between {start_date} and {end_date}.
Use BOTH the price path and the news headlines below.

Goals:
- 1–3 short paragraphs.
- Describe the overall trend and major turning points (with approximate prices and dates).
- When it makes sense, explicitly connect price moves to specific news items
  (e.g. "Following the announcement about X on DATE, the price dropped from ~A to ~B").
- If the link is speculative, use cautious language like "may have contributed" or "likely related".
- Do NOT give any investment advice.

Indicators:
- Start price: {indicators['start_price']}
- End price: {indicators['end_price']}
- Return (%): {indicators['return_pct']}
- Max drawdown (%): {indicators['max_drawdown_pct']}

Sampled price path:
{chart_text}

Relevant news headlines:
{news_text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You write clear, factual market history narratives."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()


def generate_asset_background(symbol: str, docs: List[Dict[str, str]]) -> str:
    """
    RAG-style: given web search documents about an asset, generate a
    long-term history / background narrative.

    - symbol: "BTC", "ETH", etc.
    - docs: list of { title, snippet, url, published_at }
    """

    if not docs:
        # Fallback if search failed, so the endpoint still returns something.
        return (
            f"This is supposed to be a historical overview of {symbol}, "
            "but no background documents were available from the search engine."
        )

    # Build a compact context string to feed the model.
    # We include title, snippet, date, and URL for each document.
    context_blocks = []
    for idx, d in enumerate(docs, start=1):
        block = (
            f"[Source {idx}]\n"
            f"Title: {d.get('title', '')}\n"
            f"Snippet: {d.get('snippet', '')}\n"
            f"Date: {d.get('published_at', '')}\n"
            f"URL: {d.get('url', '')}\n"
        )
        context_blocks.append(block)

    context_text = "\n\n".join(context_blocks)

    prompt = f"""
You are a crypto historian.

Using ONLY the information in the sources below, write a concise but rich
background history for the asset {symbol} (a cryptocurrency).

Your answer MUST:
- Focus on long-term history, not just recent price moves.
- Cover: creation/launch, who created it (if known), what problem it tries to solve,
  key technical ideas (briefly), major protocol upgrades or forks,
  important historical events (bubbles, crashes, regulatory moments, hacks, etc.)
- Mention specific years / rough dates when you can.
- Stay factual and neutral. NO investment advice or price predictions.
- Optionally reference sources like "(Source 1)" when you use them.

Sources:
{context_text}

Now write 2–4 short paragraphs in clear language.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful, neutral crypto historian. "
                    "You only use the information provided in the context."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()
