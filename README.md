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
```
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
```


---

## 🧠 System Overview

### ⭐ Agent Architecture (LangGraph)

The backend implements a **LangGraph state machine** coordinating three LLM workflows:

---

### **1. Overview Agent**
Summarizes trends using:

- price data  
- indicators  
- compressed RAG context  
- news events  

---

### **2. Ask-AI Agent**
A retrieval-augmented QA agent that:

- pulls real-time market data  
- fetches news (NewsAPI)  
- performs SerpAPI/Wikipedia lookups  
- builds consolidated textual context  
- uses a **draft → verify** two-pass reasoning pattern  

---

### **3. History Agent**
Stores and returns previous queries & results.

---

## 🗄️ Backend Modules

### **main.py**
FastAPI entry point — routing for:

- `/overview`
- `/ask_ai`
- `/history`

Includes CORS config + dev/prod switching.

---

### **llm_graph.py**
Defines the LangGraph agent including:

- price fetch node  
- news fetch node  
- RAG assembly  
- verification step  
- overall execution flow  

---

### **asset_history_rag.py**
Fetches historical chart data and converts it into:

- trend descriptions  
- volatility indicators  
- RAG text chunks  

---

### **market_data.py**
Coingecko interface for:

- price  
- volume  
- market cap  
- 24h & 7d indicator summaries  

---

### **news_data.py**
Runs NewsAPI queries, filters headlines, and prepares summaries.

---

### **news_api_test.py**
Quick script for validating NewsAPI keys and endpoints.

---

## 🎨 Frontend Overview

### **OverviewTab.jsx**
Displays:

- price charts  
- AI-generated macro summary  

### **AskAITab.jsx**
Q&A interface powered by RAG + GPT-4.1.

### **HistoryTab.jsx**
Scrollable view of previous queries.

### **FiltersBar.jsx**
UI controls for:

- symbol  
- date range  
- aggregation options  

---

## 🛠️ Setup Instructions

### **Backend**
```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
---

## ✨ Features

- LangGraph-based agent workflow  
- Grounded RAG over price history & news  
- Two-pass LLM verification  
- React + Material UI dashboard  
- Real-time indicators (Coingecko)  
- Cloud-ready deployment (Render + Vercel)  

---

## 🔧 Future Improvements

- Dockerize backend + frontend  
- Fix responsive layout sizing  
- Add chat history to AskAI tab  
- Add chatbox UI for more natural prompts  

---

## 🤝 Contributing

Issues and PRs welcome.

---

## 📄 License

MIT License.

