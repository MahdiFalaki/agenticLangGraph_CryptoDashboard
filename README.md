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

## Tech Stack

- Frontend:
  - React
  - Vite
  - MUI
  - Recharts
- Backend:
  - FastAPI
  - LangGraph
  - OpenAI Python SDK
  - Uvicorn
- Data Providers:
  - CoinGecko
  - NewsAPI
  - SerpAPI
  - Wikipedia
- DevOps:
  - Docker (backend image)
  - GitHub Actions (CI/CD workflows)
  - AWS CloudFront + S3 (frontend hosting)
  - AWS App Runner (backend runtime)
  - AWS ECR (backend image registry)
  - AWS Secrets Manager (runtime secrets)

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

## Project Status

`v2` is live and production-deployed. Current focus is performance tuning, reliability improvements, and continued UX refinement.

## DevOps Scope: What We Did vs. What Professional DevOps Adds

### DevOps Work Implemented in This Project

- **Containerization and backend runtime packaging**
  - Built a production backend image with Docker (`backend/Dockerfile`) and standardized runtime startup with Uvicorn.
- **AWS backend delivery**
  - Published backend images to **AWS ECR**.
  - Deployed and updated backend service on **AWS App Runner**.
  - Exposed runtime probes (`/health`, `/health/deps`) for service readiness/liveness checks.
- **AWS frontend delivery**
  - Built frontend artifacts with Vite and deployed static assets to **AWS S3**.
  - Served frontend globally through **AWS CloudFront**.
  - Ran **CloudFront invalidation** after deployments to ensure users receive fresh assets.
- **CI/CD automation (GitHub Actions)**
  - Created separate workflows for backend and frontend deployment triggers.
  - Automated Docker build + push, App Runner deployment trigger, S3 sync, and CloudFront invalidation.
  - Used GitHub Actions OIDC/role-based AWS credential configuration.
- **Secrets/config handling**
  - Managed runtime/API configuration via environment variables and AWS secret-backed configuration.

### What Professional DevOps Engineering Usually Includes (Not Yet Fully Implemented Here)

- **Infrastructure as Code at full depth**
  - End-to-end infra definitions (e.g., Terraform/CloudFormation/CDK) for reproducible environments, drift detection, and formal change review.
- **Multi-environment release strategy**
  - Distinct dev/staging/prod environments with promotion gates, approvals, and environment parity controls.
- **Advanced release safety**
  - Blue/green or canary rollouts, automated rollback strategy, and progressive traffic shifting.
- **Deeper observability/SRE practices**
  - Centralized logs, metrics, distributed tracing, SLO/SLI dashboards, alert routing, and incident playbooks.
- **Security hardening maturity**
  - Automated SAST/DAST/container/IaC scanning in CI, dependency vulnerability policies, secret rotation policies, least-privilege audits, and compliance baselines.
- **Platform reliability operations**
  - Capacity planning, load/performance testing in pipeline, cost governance, backup/disaster-recovery drills, and formal on-call/incident response processes.

### Honest Summary

This project demonstrates **practical DevOps implementation for a production-capable web app** (containerization, AWS deployment, CI/CD automation, and runtime checks). It is strong for portfolio/interview evidence of hands-on delivery. It is not yet the full scope of a mature enterprise DevOps platform program with comprehensive IaC governance, staged release orchestration, deep SRE observability, and compliance-grade security operations.


## LinkedIn-Ready Project Description (Short)

**Crypto Market Dashboard** *(Nov 2025)*  
Full-stack crypto intelligence dashboard that combines market data, news context, and agentic LLM workflows to generate grounded insights for analysis.

- Built a FastAPI + LangGraph backend with dedicated overview, Q&A, and history flows.
- Implemented two-pass draft → verification generation to improve factual reliability.
- Developed a React + MUI frontend with interactive charts, staged loading, and source-linked outputs.
- Deployed on AWS: backend on App Runner (Docker images via ECR), frontend on S3 + CloudFront, with GitHub Actions CI/CD.

**Skills:** LangGraph Agents · FastAPI · React.js · Material UI · RAG · Docker · AWS (App Runner, ECR, S3, CloudFront) · GitHub Actions
