from fastapi import FastAPI, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from .market_data import fetch_crypto_history, MarketDataError
from .news_data import fetch_symbol_news
from .asset_history_rag import fetch_asset_background_docs
from .llm_graph import agent, AgentState  # <-- use LangGraph instead of llm_client

app = FastAPI()

# ----------- CORS CONFIG (DEV-FRIENDLY) ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # DEV: allow any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------- Pydantic MODELS ----------------
class SummaryRequest(BaseModel):
    start_date: str
    end_date: str


class ChartPoint(BaseModel):
    date: str
    price: float


class Indicators(BaseModel):
    start_price: float
    end_price: float
    return_pct: float
    max_drawdown_pct: float


class NewsItem(BaseModel):
    title: str
    snippet: str
    content: str
    url: str
    published_at: str
    image_url: str | None = None


class SummaryResponse(BaseModel):
    start_date: str
    end_date: str
    chart: List[ChartPoint]
    indicators: Indicators
    news: List[NewsItem]
    summary: str


class QARequest(BaseModel):
    start_date: str
    end_date: str
    question: str


class QAResponse(BaseModel):
    indicators: Indicators
    news: List[NewsItem]
    answer: str


class HistoryRequest(BaseModel):
    start_date: str
    end_date: str


class HistoryResponse(BaseModel):
    chart: List[ChartPoint]
    history_story: str
    news: List[NewsItem]


# ----------- Small helpers to call the graph ----------------

def _empty_state(mode: str) -> AgentState:
    """Base state with safe defaults so all nodes can run."""
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
    state: AgentState = _empty_state(mode="history")
    state["symbol"] = symbol
    state["docs"] = docs

    result = agent.invoke(state)
    return result["answer"]


# ----------- ENDPOINTS ----------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/asset/{symbol}/summary", response_model=SummaryResponse)
async def get_summary(
    symbol: str = Path(..., description="Asset symbol, e.g. BTC, ETH"),
    body: SummaryRequest = None,
):
    """
    Overview tab: returns chart + indicators + summary + latest news.
    Uses real market data via fetch_crypto_history and NewsAPI via fetch_symbol_news.
    """
    # 1) Price data
    try:
        market = fetch_crypto_history(symbol, body.start_date, body.end_date)
    except MarketDataError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2) News data (NEW)
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

    # 3) LLM summary from price data (we can ignore news here if you want)
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
            "A detailed AI summary is temporarily unavailable."
        )

    # 4) Return chart + indicators + news + summary
    return {
        "start_date": body.start_date,
        "end_date": body.end_date,
        "chart": market["chart"],
        "indicators": market["indicators"],
        "news": news,   # ⬅️ was [] before
        "summary": summary_text,
    }


@app.post("/api/asset/{symbol}/qa", response_model=QAResponse)
async def get_qa(
    symbol: str = Path(..., description="Asset symbol, e.g. BTC, ETH, AAPL"),
    body: QARequest = None,
):
    """
    Ask AI tab:
    - Get real price indicators
    - Get recent news
    - Ask the LLM to answer the question using both
    """

    # 1) Price data
    try:
        market = fetch_crypto_history(symbol, body.start_date, body.end_date)
    except MarketDataError as e:
        raise HTTPException(status_code=400, detail=str(e))

    indicators = market["indicators"]

    # 2) News data
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

    # 3) LLM answer via graph
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
            "A detailed AI explanation is temporarily unavailable."
        )

    return {
        "indicators": indicators,
        "news": news,
        "answer": answer,
    }


@app.post("/api/asset/{symbol}/history", response_model=HistoryResponse)
async def get_history(symbol: str, body: HistoryRequest):
    """
    History tab:

    - Uses price data only for the chart (visualization).
    - Uses web search (RAG) docs to build a long-term background story.
    """

    # 1) Chart for visualization
    try:
        market = fetch_crypto_history(symbol, body.start_date, body.end_date)
        chart = market["chart"]
    except MarketDataError as e:
        print(f"[WARN] fetch_crypto_history failed in /history: {e}")
        chart = []

    # 2) Retrieve background documents (RAG)
    try:
        docs = fetch_asset_background_docs(symbol, max_results=5)
    except Exception as e:
        print(f"[WARN] fetch_asset_background_docs failed: {e}")
        docs = []

    # 3) Generate background story via graph (history mode)
    try:
        story = _generate_asset_background_with_graph(symbol=symbol, docs=docs)
    except Exception as e:
        print(f"[ERROR] Graph/LLM call failed in /history: {e}")
        story = (
            f"This is supposed to be a historical overview of {symbol}, "
            "but the AI component failed. Please try again later."
        )

    # 4) Return chart + story + docs (docs show up on the right in the UI)
    return {
        "chart": chart,
        "history_story": story,
        "news": docs,  # same shape as NewsItem; frontend treats these as sources
    }
