# backend/market_data.py

import os
from datetime import datetime
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# -----------------------------------------
# Map UI symbols -> provider coin IDs
# Extend this list to support more cryptos.
# -----------------------------------------
SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    # add more here as needed
}

class MarketDataError(Exception):
    """Custom error for market data issues."""
    pass


def _iso_date_to_unix(date_str: str) -> int:
    """
    Convert YYYY-MM-DD to unix timestamp (seconds).
    """
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())


def fetch_crypto_history(symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Fetch historical prices for a crypto symbol between start_date and end_date (inclusive-ish).
    Returns a dict with:
        - chart: list of {date: 'YYYY-MM-DD', price: float}
        - indicators: {start_price, end_price, return_pct, max_drawdown_pct}

    Currently supports only symbols in SYMBOL_TO_ID (e.g. BTC, ETH).
    """
    symbol = symbol.upper()
    coin_id = SYMBOL_TO_ID.get(symbol)
    if not coin_id:
        raise MarketDataError(
            f"Unsupported symbol for crypto data: {symbol}. "
            f"Supported symbols: {', '.join(SYMBOL_TO_ID.keys())}"
        )

    if not COINGECKO_API_KEY:
        raise MarketDataError("COINGECKO_API_KEY is not set in environment")

    start_ts = _iso_date_to_unix(start_date)
    end_ts = _iso_date_to_unix(end_date)

    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart/range"

    headers = {
        "x-cg-demo-api-key": COINGECKO_API_KEY,
    }

    params = {
        "vs_currency": "usd",
        "from": start_ts,
        "to": end_ts,
    }

    resp = requests.get(url, headers=headers, params=params, timeout=10)
    if resp.status_code != 200:
        raise MarketDataError(
            f"CoinGecko API error {resp.status_code}: {resp.text[:200]}"
        )

    data = resp.json()
    prices = data.get("prices", [])

    if not prices:
        raise MarketDataError(
            f"No price data returned from CoinGecko for {symbol} between "
            f"{start_date} and {end_date}."
        )

    # Convert to chart points: [ [timestamp_ms, price], ... ]
    chart: List[Dict[str, Any]] = []
    for ts_ms, price in prices:
        dt = datetime.utcfromtimestamp(ts_ms / 1000.0)
        chart.append(
            {
                "date": dt.strftime("%Y-%m-%d"),
                "price": float(price),
            }
        )

    # Compute indicators on the chart
    start_price = chart[0]["price"]
    end_price = chart[-1]["price"]
    return_pct = ((end_price - start_price) / start_price) * 100.0

    # Max drawdown: worst drop from a previous peak
    peak = chart[0]["price"]
    max_drawdown_pct = 0.0
    for point in chart:
        price = point["price"]
        if price > peak:
            peak = price
        drawdown = (price - peak) / peak * 100.0  # negative if below peak
        if drawdown < max_drawdown_pct:
            max_drawdown_pct = drawdown

    indicators = {
        "start_price": round(start_price, 4),
        "end_price": round(end_price, 4),
        "return_pct": round(return_pct, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
    }

    return {
        "chart": chart,
        "indicators": indicators,
    }
