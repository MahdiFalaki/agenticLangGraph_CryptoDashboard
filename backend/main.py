"""FastAPI entrypoint for market overview, Q&A, and background endpoints."""

import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .asset_history_rag import fetch_asset_background_docs
from .llm_graph import AgentState, agent
from .market_data import MarketDataError, fetch_crypto_history
from .news_data import fetch_symbol_news

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummaryRequest(BaseModel):
    """Common request body for date-bounded asset queries."""

    start_date: str
    end_date: str


class ChartPoint(BaseModel):
    """Single chart data point in ISO date + price format."""

    date: str
    price: float


class Indicators(BaseModel):
    """Core performance metrics computed from chart data."""

    start_price: float
    end_price: float
    return_pct: float
    max_drawdown_pct: float


class NewsItem(BaseModel):
    """Normalized news/source item returned to the frontend."""

    title: str
    snippet: str
    content: str
    url: str
    published_at: str
    image_url: str | None = None


class SummaryResponse(BaseModel):
    """Aggregated response used by the legacy overview endpoint."""

    start_date: str
    end_date: str
    chart: List[ChartPoint]
    indicators: Indicators
    news: List[NewsItem]
    summary: str


class MarketResponse(BaseModel):
    """Market-only payload for staged overview loading."""

    start_date: str
    end_date: str
    chart: List[ChartPoint]
    indicators: Indicators


class SummaryTextResponse(BaseModel):
    """Summary text payload for staged overview loading."""

    summary: str


class NewsResponse(BaseModel):
    """News payload for staged overview loading."""

    news: List[NewsItem]


class QARequest(BaseModel):
    """Request body for Q&A generation."""

    start_date: str
    end_date: str
    question: str


class QAResponse(BaseModel):
    """Q&A response with answer and supporting context."""

    indicators: Indicators
    news: List[NewsItem]
    answer: str


class HistoryRequest(BaseModel):
    """Request body for background brief generation."""

    start_date: str
    end_date: str


class HistoryResponse(BaseModel):
    """History response with chart, brief, and source list."""

    chart: List[ChartPoint]
    history_story: str
    news: List[NewsItem]


def _dependency_status() -> Dict[str, bool]:
    """Return boolean readiness for required external-service keys."""

    return {
        "openai_api_key": bool(os.getenv("OPENAI_API_KEY")),
        "coingecko_api_key": bool(os.getenv("COINGECKO_API_KEY")),
        "news_api_key": bool(os.getenv("NEWS_API_KEY")),
        "serpapi_key": bool(os.getenv("SERPAPI_KEY")),
    }


@app.on_event("startup")
def startup_diagnostics() -> None:
    """Log missing environment keys on startup for quick diagnostics."""

    deps = _dependency_status()
    missing = [k for k, ready in deps.items() if not ready]
    if missing:
        print(f"[WARN] Missing environment keys: {', '.join(missing)}")
    else:
        print("[INFO] All required environment keys are present.")


def _empty_state(mode: str) -> AgentState:
    """Return a safe initial graph state."""

    return {
        "mode": mode,
        "symbol": "",
        "start_date": "",
        "end_date": "",
        "indicators": {},
        "chart": [],
        "news": [],
        "docs": [],
        "question": "",
    }


def _summarize_price_action_with_graph(
    symbol: str,
    start_date: str,
    end_date: str,
    indicators: Dict[str, float],
    chart: List[Dict[str, Any]],
) -> str:
    """Run overview graph branch and return generated summary text."""

    state: AgentState = _empty_state(mode="overview")
    state["symbol"] = symbol
    state["start_date"] = start_date
    state["end_date"] = end_date
    state["indicators"] = indicators
    state["chart"] = chart

    result = agent.invoke(state)
    return result["answer"]


def _answer_price_question_with_graph(
    symbol: str,
    indicators: Dict[str, float],
    news: List[Dict[str, Any]],
    question: str,
) -> str:
    """Run Q&A graph branch and return generated answer text."""

    state: AgentState = _empty_state(mode="ask_AI")
    state["symbol"] = symbol
    state["indicators"] = indicators
    state["news"] = news
    state["question"] = question

    result = agent.invoke(state)
    return result["answer"]


def _generate_asset_background_with_graph(
    symbol: str,
    docs: List[Dict[str, str]],
) -> str:
    """Run history graph branch and return generated background text."""

    state: AgentState = _empty_state(mode="history")
    state["symbol"] = symbol
    state["docs"] = docs

    result = agent.invoke(state)
    return result["answer"]


@app.get("/health")
def health_check():
    """Liveness probe."""

    return {"status": "ok"}


@app.get("/health/deps")
def health_dependency_check():
    """Dependency key readiness probe."""

    deps = _dependency_status()
    return {
        "status": "ok" if all(deps.values()) else "degraded",
        "dependencies": deps,
    }


@app.post("/api/asset/{symbol}/summary", response_model=SummaryResponse)
async def get_summary(
    symbol: str = Path(..., description="Asset symbol, e.g. BTC, ETH"),
    body: SummaryRequest = None,
):
    """Return full overview payload (market + summary + news)."""

    # Fetch market baseline first; all remaining data depends on it.
    try:
        market = fetch_crypto_history(symbol, body.start_date, body.end_date)
    except MarketDataError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # News failures are non-fatal; return empty list as fallback.
    try:
        news = fetch_symbol_news(
            symbol=symbol,
            start_date=body.start_date,
            end_date=body.end_date,
            max_articles=5,
        )
    except Exception as e:
        print(f"[WARN] fetch_symbol_news failed in /summary: {e}")
        news = []

    # Summary failure falls back to deterministic numeric description.
    try:
        summary_text = _summarize_price_action_with_graph(
            symbol=symbol,
            start_date=body.start_date,
            end_date=body.end_date,
            indicators=market["indicators"],
            chart=market["chart"],
        )
    except Exception as e:
        print(f"[ERROR] Graph/LLM call failed in /summary: {e}")
        summary_text = (
            f"Between {body.start_date} and {body.end_date}, {symbol} moved from "
            f"{market['indicators']['start_price']} to {market['indicators']['end_price']} USD "
            f"({market['indicators']['return_pct']}% return). "
            "A detailed summary is temporarily unavailable."
        )

    return {
        "start_date": body.start_date,
        "end_date": body.end_date,
        "chart": market["chart"],
        "indicators": market["indicators"],
        "news": news,
        "summary": summary_text,
    }


@app.post("/api/asset/{symbol}/market", response_model=MarketResponse)
async def get_market(
    symbol: str = Path(..., description="Asset symbol, e.g. BTC, ETH"),
    body: SummaryRequest = None,
):
    """Return market-only payload for staged UI rendering."""

    try:
        market = fetch_crypto_history(symbol, body.start_date, body.end_date)
    except MarketDataError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "start_date": body.start_date,
        "end_date": body.end_date,
        "chart": market["chart"],
        "indicators": market["indicators"],
    }


@app.post("/api/asset/{symbol}/summary_text", response_model=SummaryTextResponse)
async def get_summary_text(
    symbol: str = Path(..., description="Asset symbol, e.g. BTC, ETH"),
    body: SummaryRequest = None,
):
    """Return summary-only payload for staged UI rendering."""

    try:
        market = fetch_crypto_history(symbol, body.start_date, body.end_date)
    except MarketDataError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        summary_text = _summarize_price_action_with_graph(
            symbol=symbol,
            start_date=body.start_date,
            end_date=body.end_date,
            indicators=market["indicators"],
            chart=market["chart"],
        )
    except Exception as e:
        print(f"[ERROR] Graph/LLM call failed in /summary_text: {e}")
        summary_text = (
            f"Between {body.start_date} and {body.end_date}, {symbol} moved from "
            f"{market['indicators']['start_price']} to {market['indicators']['end_price']} USD "
            f"({market['indicators']['return_pct']}% return). "
            "A detailed summary is temporarily unavailable."
        )

    return {"summary": summary_text}


@app.post("/api/asset/{symbol}/news", response_model=NewsResponse)
async def get_news(
    symbol: str = Path(..., description="Asset symbol, e.g. BTC, ETH"),
    body: SummaryRequest = None,
):
    """Return news-only payload for staged UI rendering."""

    try:
        news = fetch_symbol_news(
            symbol=symbol,
            start_date=body.start_date,
            end_date=body.end_date,
            max_articles=5,
        )
    except Exception as e:
        print(f"[WARN] fetch_symbol_news failed in /news: {e}")
        news = []

    return {"news": news}


@app.post("/api/asset/{symbol}/qa", response_model=QAResponse)
async def get_qa(
    symbol: str = Path(..., description="Asset symbol, e.g. BTC, ETH, AAPL"),
    body: QARequest = None,
):
    """Return answer text grounded in indicators and recent news."""

    try:
        market = fetch_crypto_history(symbol, body.start_date, body.end_date)
    except MarketDataError as e:
        raise HTTPException(status_code=400, detail=str(e))

    indicators = market["indicators"]

    try:
        news = fetch_symbol_news(
            symbol=symbol,
            start_date=body.start_date,
            end_date=body.end_date,
            max_articles=5,
        )
    except Exception as e:
        print(f"[WARN] fetch_symbol_news failed: {e}")
        news = []

    try:
        answer = _answer_price_question_with_graph(
            symbol=symbol,
            indicators=indicators,
            news=news,
            question=body.question,
        )
    except Exception as e:
        print(f"[ERROR] Graph/LLM call failed in /qa: {e}")
        answer = (
            f"Between {body.start_date} and {body.end_date}, {symbol} moved from "
            f"{indicators['start_price']} to {indicators['end_price']} USD "
            f"({indicators['return_pct']}% return). "
            "A detailed explanation is temporarily unavailable."
        )

    return {
        "indicators": indicators,
        "news": news,
        "answer": answer,
    }


@app.post("/api/asset/{symbol}/history", response_model=HistoryResponse)
async def get_history(symbol: str, body: HistoryRequest):
    """Return chart, background brief, and supporting sources."""

    # Chart and docs are independent sources; keep graceful fallbacks.
    try:
        market = fetch_crypto_history(symbol, body.start_date, body.end_date)
        chart = market["chart"]
    except MarketDataError as e:
        print(f"[WARN] fetch_crypto_history failed in /history: {e}")
        chart = []

    try:
        docs = fetch_asset_background_docs(symbol, max_results=3)
    except Exception as e:
        print(f"[WARN] fetch_asset_background_docs failed: {e}")
        docs = []

    try:
        story = _generate_asset_background_with_graph(symbol=symbol, docs=docs)
    except Exception as e:
        print(f"[ERROR] Graph/LLM call failed in /history: {e}")
        story = (
            f"This is supposed to be a historical overview of {symbol}, "
            "but the summary component failed. Please try again later."
        )

    return {
        "chart": chart,
        "history_story": story,
        "news": docs,
    }
