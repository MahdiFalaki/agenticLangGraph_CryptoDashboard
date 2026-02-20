# Crypto Analysis Dashboard v2

![version](https://img.shields.io/badge/version-v2-blue)
![backend](https://img.shields.io/badge/backend-FastAPI%20%2B%20LangGraph-green)
![frontend](https://img.shields.io/badge/frontend-React%20%2B%20MUI-informational)
![status](https://img.shields.io/badge/status-active-success)

A full-stack crypto insights application with staged market loading, grounded question answering, and background brief generation.

## Stack

- Backend: FastAPI, LangGraph, OpenAI Python SDK
- Data Providers: CoinGecko, NewsAPI, SerpAPI, Wikipedia
- Frontend: React, Vite, MUI, Recharts

## Architecture Overview

### Backend flows

- Overview
  - Market data from CoinGecko
  - Summary generation via graph
  - News fetch from NewsAPI
- Q&A
  - Indicators + news grounding
  - Draft and grounded rewrite pass
- History
  - Source retrieval (SerpAPI + Wikipedia)
  - Background brief generation

### Frontend flows

- Overview tab
  - Apply filters, then staged rendering (metrics -> chart -> notes -> news)
- Q&A tab
  - Ask question and get grounded response with source list
- History tab
  - Generate background brief with supporting references

## Project Structure

```text
crypto_agenticAI/
|-- backend/
|   |-- main.py
|   |-- llm_graph.py
|   |-- market_data.py
|   |-- news_data.py
|   |-- asset_history_rag.py
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- App.jsx
|   |   `-- components/
|   |-- package.json
|   `-- vite.config.js
|-- environment.yml
`-- README.md
```

## Environment Variables

Create a root `.env` file:

```env
COINGECKO_API_KEY=
NEWS_API_KEY=
SERPAPI_KEY=
OPENAI_API_KEY=
```

For local frontend->backend routing, set in `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Local Setup

### Backend

```bash
conda activate cryptoProj_env_win
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## API Reference

### Health

- `GET /health`
- `GET /health/deps`

### Overview

- `POST /api/asset/{symbol}/summary` (legacy combined payload)
- `POST /api/asset/{symbol}/market`
- `POST /api/asset/{symbol}/summary_text`
- `POST /api/asset/{symbol}/news`

### Q&A and History

- `POST /api/asset/{symbol}/qa`
- `POST /api/asset/{symbol}/history`

## Frontend Features

- Dashboard-style layout with responsive cards and charts
- Per-tab onboarding popovers (shown once per tab)
- Date validation and range enforcement before API requests
- Graceful loading/error states and backward compatibility fallback

## Notes

- CoinGecko free tier has historical data window limits.
- First request can be slower due to external API latency.
- If endpoints change, restart both backend and frontend dev servers.

