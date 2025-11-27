# 🚀 Market AI Crypto Dashboard

---

## Agentic LLM Dashboard for Live Crypto Insights  
*(FastAPI + LangGraph + RAG + GPT-4.1 + React + Material UI)*

---

## 🌐 Live Demo

🔗 **https://agentic-lang-graph-crypto-dashboard-q42vfe62t.vercel.app/**

---

This repository contains a full-stack **agentic LLM system** that provides grounded, real-time cryptocurrency insights using a combination of:

- **FastAPI backend**
- **LangGraph agent state machine**
- **RAG over price history, news & market data**
- **OpenAI GPT-4.1**
- **React + Material UI frontend**

The system is fully deployed with:

- **Backend → Render**
- **Frontend → Vercel**

---

## 📁 Project Structure

crypto_agenticAI/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── llm_graph.py
│   ├── asset_history_rag.py
│   ├── market_data.py
│   ├── news_data.py
│   ├── news_api_test.py
│   ├── requirements.txt
│
└── frontend/
    ├── public/
    ├── dist/
    ├── node_modules/
    └── src/
        ├── assets/
        ├── components/
        │   ├── AskAITab.jsx
        │   ├── OverviewTab.jsx
        │   ├── HistoryTab.jsx
        │   ├── FiltersBar.jsx
        │   ├── TabPanel.jsx
        ├── App.jsx
        ├── App.css
        ├── index.css
        ├── main.jsx
