# Crypto Analysis Dashboard 

![version](https://img.shields.io/badge/version-v2-blue)
![frontend](https://img.shields.io/badge/frontend-React%20%2B%20MUI-informational)
![backend](https://img.shields.io/badge/backend-FastAPI%20%2B%20LangGraph-green)
![deployment](https://img.shields.io/badge/deployment-AWS-orange)

Crypto Analysis Dashboard v2 is a production crypto intelligence web app focused on fast market awareness and clear decision support.

It brings price action, indicators, news context, Q&A, and historical background into one interface so analysis can happen in a single flow instead of across multiple tools.

Typical usage:

- Select a symbol and date window
- Review indicators and chart movement
- Read short market notes and current news context
- Ask targeted questions
- Generate a background brief with source references

## Live Deployment

- Website (CloudFront): [https://d3db91zo0jyf9c.cloudfront.net](https://d3db91zo0jyf9c.cloudfront.net)
- Backend API (App Runner): [https://vdrpfsgzmf.us-east-1.awsapprunner.com](https://vdrpfsgzmf.us-east-1.awsapprunner.com)
- Health checks:
  - [https://vdrpfsgzmf.us-east-1.awsapprunner.com/health](https://vdrpfsgzmf.us-east-1.awsapprunner.com/health)
  - [https://vdrpfsgzmf.us-east-1.awsapprunner.com/health/deps](https://vdrpfsgzmf.us-east-1.awsapprunner.com/health/deps)

## What The App Does

- Tracks price behavior for supported symbols (`BTC`, `ETH`, `SOL`, `XRP`, `DOGE`)
- Computes key indicators:
  - start price
  - end price
  - return percentage
  - max drawdown percentage
- Shows staged overview loading:
  - indicators -> chart -> summary notes -> news
- Generates concise market notes for the selected period
- Supports question answering grounded in market indicators and news context
- Generates a background brief with source references in the History view

## AI Model Usage

- Overview summaries: `gpt-5-nano`
- Ask/Q&A responses: `gpt-5-mini`
- History background generation: lightweight GPT-5 flow in backend graph pipeline

## Production Architecture

The system is split into static frontend delivery and managed backend compute.  
Deployment and runtime responsibilities are separated to keep releases predictable and operations simple.

- Frontend delivery:
  - Vite build output is stored in S3.
  - CloudFront serves assets globally over HTTPS.
  - CDN invalidation is used after frontend deployments.
  - SPA route fallback is handled at CDN/error-response level.
- Backend runtime:
  - FastAPI is containerized with Docker.
  - Images are stored in ECR.
  - App Runner deploys and runs the backend container.
  - Runtime secrets are loaded from AWS Secrets Manager.
- API behavior:
  - Health probes: `/health`, `/health/deps`.
  - Staged overview endpoints: `/market`, `/summary_text`, `/news`.
  - Legacy compatibility endpoint: `/summary`.
- CI/CD and traffic flow:
  - GitHub Actions automates frontend and backend deployment workflows.
  - Browser -> CloudFront -> S3 for frontend requests.
  - Browser -> App Runner for backend API requests.
- External data services:
  - CoinGecko: market history and price series.
  - NewsAPI: period news context.
  - SerpAPI + Wikipedia: history/source retrieval.

## Local Development

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

## Environment Variables

Backend (`.env`):

```env
OPENAI_API_KEY=
COINGECKO_API_KEY=
COINGECKO_API_PLAN=demo
NEWS_API_KEY=
SERPAPI_KEY=
```

Frontend (`frontend/.env`):

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Repository Structure

```text
crypto_agenticAI/
|-- backend/
|   |-- main.py
|   |-- llm_graph.py
|   |-- market_data.py
|   |-- news_data.py
|   |-- asset_history_rag.py
|   |-- Dockerfile
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |-- public/
|   `-- package.json
|-- .github/workflows/
|   |-- backend-deploy.yml
|   `-- frontend-deploy.yml
`-- README.md
```

## API Surface

- Health:
  - `GET /health`
  - `GET /health/deps`
- Overview:
  - `POST /api/asset/{symbol}/summary` (legacy combined endpoint)
  - `POST /api/asset/{symbol}/market`
  - `POST /api/asset/{symbol}/summary_text`
  - `POST /api/asset/{symbol}/news`
- Ask/Q&A:
  - `POST /api/asset/{symbol}/qa`
- History:
  - `POST /api/asset/{symbol}/history`

 ## Tech Stack

- Frontend: React.js, Vite, MUI, Recharts
- Backend: FastAPI, LangGraph, OpenAI Python SDK, Uvicorn
- Third-Party API Data Providers: CoinGecko, NewsAPI, SerpAPI, Wikipedia
- DevOps: Docker (backend image), GitHub Actions (CI/CD workflows), AWS CloudFront + S3 (frontend hosting), AWS App Runner (backend runtime), AWS ECR (backend image registry), AWS Secrets Manager (runtime secrets)

## Project Status

`v2` is live and production-deployed. Current focus is performance tuning, reliability improvements, and continued UX refinement.
