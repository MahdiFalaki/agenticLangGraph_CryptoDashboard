import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")  # make sure this is set in your .env

if not API_KEY:
    raise RuntimeError("NEWS_API_KEY not set in .env")

def test_news(symbol: str, q_override: str | None = None):
    # Map symbols to a more realistic query term
    symbol_to_query = {
        "BTC": "bitcoin OR \"bitcoin price\"",
        "ETH": "ethereum OR \"ether price\"",
        "AAPL": "Apple Inc OR AAPL",
        "TSLA": "Tesla Inc OR TSLA",
    }

    q = q_override or symbol_to_query.get(symbol.upper(), symbol)

    # Use a small recent window to avoid API limits
    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days=7)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "language": "en",
        "sortBy": "relevancy",   # or 'publishedAt'
        "pageSize": 10,
    }
    headers = {"X-Api-Key": API_KEY}

    print("Requesting:", url)
    print("Params:", params)

    resp = requests.get(url, params=params, headers=headers, timeout=15)
    print("Status code:", resp.status_code)

    try:
        data = resp.json()
    except Exception:
        print("Non-JSON response:", resp.text[:500])
        return

    print("Raw response keys:", list(data.keys()))
    print("totalResults:", data.get("totalResults"))
    articles = data.get("articles", [])
    print(f"Number of articles: {len(articles)}")
    for i, art in enumerate(articles[:5], start=1):
        print(f"\nArticle {i}:")
        print("  title     :", art.get("title"))
        print("  published :", art.get("publishedAt"))
        print("  url       :", art.get("url"))


if __name__ == "__main__":
    # Try BTC by default
    test_news("BTC")
