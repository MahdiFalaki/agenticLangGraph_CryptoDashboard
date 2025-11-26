# backend/news_data.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not NEWS_API_KEY:
    raise RuntimeError("NEWS_API_KEY missing from .env")

SYMBOL_TO_NEWS_QUERY = {
    "BTC": "bitcoin OR \"bitcoin price\"",
    "ETH": "ethereum OR \"ethereum price\"",
    "AAPL": "Apple Inc OR AAPL OR \"Apple stock\"",
    "TSLA": "Tesla Inc OR TSLA OR \"Tesla stock\"",
}


def fetch_symbol_news(symbol: str, start_date: str, end_date: str, max_articles: int = 10):
    """
    Fetch recent news from NewsAPI for this symbol.

    IMPORTANT:
    - We IGNORE start_date / end_date because NewsAPI free/cheap plans
      only allow querying a limited recent window (e.g., last 30 days).
    - We let NewsAPI default to its allowed time range.
    """

    q = SYMBOL_TO_NEWS_QUERY.get(symbol.upper(), symbol)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": max_articles,
        # NO "from" / "to" here, so it uses the default recent window
    }
    headers = {"X-Api-Key": NEWS_API_KEY}

    resp = requests.get(url, params=params, headers=headers, timeout=15)

    if resp.status_code != 200:
        raise RuntimeError(f"NewsAPI error {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    articles = data.get("articles", [])

    result = []
    for a in articles:
        result.append(
            {
                "title": a.get("title"),
                "snippet": a.get("description") or a.get("content") or "",
                "url": a.get("url"),
                "published_at": a.get("publishedAt"),
            }
        )
    return result
