# backend/asset_history_rag.py
"""
Simple RAG helper for asset background histories.

- Uses SerpAPI to search the web.
- Returns results shaped like NewsItem so the existing frontend can display them.
"""

import os
import requests
from typing import List, Dict

import urllib.parse

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_URL = "https://serpapi.com/search.json"

WIKIPEDIA_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"


def fetch_wikipedia_doc(symbol: str) -> Dict | None:
    """
    Try to fetch a Wikipedia page summary for the asset.
    Returns a NewsItem-shaped dict or None if nothing useful was found.
    """

    # You can tune this query – this version biases toward crypto pages.
    search_query = f"{symbol} (cryptocurrency)"

    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": search_query,
        "format": "json",
        "srlimit": 1,
    }

    try:
        search_resp = requests.get(WIKIPEDIA_SEARCH_URL, params=search_params, timeout=10)
        search_resp.raise_for_status()
        search_data = search_resp.json()

        search_results = search_data.get("query", {}).get("search", [])
        if not search_results:
            return None

        top_title = search_results[0]["title"]
        encoded_title = urllib.parse.quote(top_title.replace(" ", "_"))

        summary_resp = requests.get(
            WIKIPEDIA_SUMMARY_URL.format(encoded_title),
            timeout=10,
        )
        summary_resp.raise_for_status()
        summary_data = summary_resp.json()

        snippet = summary_data.get("extract") or ""
        url = (
            summary_data.get("content_urls", {})
            .get("desktop", {})
            .get("page")
            or f"https://en.wikipedia.org/wiki/{encoded_title}"
        )

        return {
            "title": f"Wikipedia: {top_title}",
            "snippet": snippet,
            "content": snippet,
            "url": url,
            "published_at": "",  # Wikipedia doesn't give a single 'published' date
            "image_url": None,
        }

    except Exception as e:
        print(f"[WARN] fetch_wikipedia_doc failed for {symbol}: {e}")
        return None


def fetch_asset_background_docs(symbol: str, max_results: int = 5) -> List[Dict]:
    """
    Use SerpAPI (Google engine) and Wikipedia to fetch web results about a crypto asset.

    Returns a list of dicts with keys:
    - title
    - snippet
    - url
    - published_at

    These match the NewsItem model so the frontend can reuse the "Supporting News" UI.
    Wikipedia (if found) is placed first and treated as the most important doc.
    """

    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY is not set in the environment (.env).")

    docs: List[Dict] = []

    # 1) Wikipedia doc first
    wiki_doc = fetch_wikipedia_doc(symbol)
    if wiki_doc:
        docs.append(wiki_doc)

    # 2) SerpAPI Google search for additional background
    query = (
        f"{symbol} cryptocurrency history, launch date, whitepaper, "
        "important protocol upgrades, forks, controversies, major events"
    )

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": max_results,
    }

    resp = requests.get(SERPAPI_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    seen_urls = {d["url"] for d in docs if d.get("url")}

    for item in data.get("organic_results", []):
        if len(docs) >= max_results:
            break

        title = item.get("title", "Untitled result")
        snippet = item.get("snippet", "")  # short description
        url = item.get("link", "")
        published_at = item.get("date", "") or ""

        if url and url in seen_urls:
            continue

        docs.append(
            {
                "title": title,
                "snippet": snippet,
                "content": snippet,
                "url": url,
                "published_at": published_at,
                "image_url": None,
            }
        )
        if url:
            seen_urls.add(url)

    return docs
