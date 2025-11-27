// src/App.jsx
import { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  Container,
} from "@mui/material";

import FiltersBar from "./components/FiltersBar.jsx";
import TabPanel from "./components/TabPanel.jsx";
import OverviewTab from "./components/OverviewTab.jsx";
import AskAITab from "./components/AskAITab.jsx";
import HistoryTab from "./components/HistoryTab.jsx";

// Backend base URL:
// - In production (Vercel) it comes from VITE_API_BASE_URL
// - In local dev it falls back to your local FastAPI server
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function App() {
  // ---- state ----
  const [symbol, setSymbol] = useState("BTC");
  const [startDate, setStartDate] = useState("2025-01-01");
  const [endDate, setEndDate] = useState("2025-01-31");
  const [tabIndex, setTabIndex] = useState(0);

  const [summaryData, setSummaryData] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState(null);

  const [qaQuestion, setQaQuestion] = useState("");
  const [qaData, setQaData] = useState(null);
  const [qaLoading, setQaLoading] = useState(false);
  const [qaError, setQaError] = useState(null);

  const [historyData, setHistoryData] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState(null);

  const handleTabChange = (_event, newValue) => setTabIndex(newValue);

  // ---- API calls ----
  const handleFetchSummary = async () => {
    setSummaryLoading(true);
    setSummaryError(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/asset/${symbol}/summary`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            start_date: startDate,
            end_date: endDate,
          }),
        }
      );
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }
      const data = await response.json();
      setSummaryData(data);
    } catch (err) {
      setSummaryError(err.message || "Unknown error");
      setSummaryData(null);
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleAskAI = async () => {
    if (!qaQuestion.trim()) return;

    setQaLoading(true);
    setQaError(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/asset/${symbol}/qa`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            start_date: startDate,
            end_date: endDate,
            question: qaQuestion,
          }),
        }
      );
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }
      const data = await response.json();
      setQaData(data);
    } catch (err) {
      setQaError(err.message || "Unknown error");
      setQaData(null);
    } finally {
      setQaLoading(false);
    }
  };

  const handleFetchHistory = async () => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/asset/${symbol}/history`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            start_date: startDate,
            end_date: endDate,
          }),
        }
      );
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }
      const data = await response.json();
      setHistoryData(data);
    } catch (err) {
      setHistoryError(err.message || "Unknown error");
      setHistoryData(null);
    } finally {
      setHistoryLoading(false);
    }
  };

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">Market AI Dashboard</Typography>
        </Toolbar>
      </AppBar>

      {/* Page background + vertical padding */}
      <Box sx={{ bgcolor: "background.default", minHeight: "100vh", py: 2 }}>
        {/* Centered content */}
        <Container
          maxWidth={false}
          sx={{ maxWidth: "80vw", mx: "auto" }} // 80% of viewport, centered
        >
          {/* Filters */}
          <Box sx={{ mb: 2 }}>
            <FiltersBar
              symbol={symbol}
              startDate={startDate}
              endDate={endDate}
              onSymbolChange={setSymbol}
              onStartDateChange={setStartDate}
              onEndDateChange={setEndDate}
              onShow={handleFetchSummary}
              loading={summaryLoading}
            />
          </Box>

          {/* Tabs header */}
          <Paper sx={{ mb: 2 }}>
            <Tabs value={tabIndex} onChange={handleTabChange}>
              <Tab label="Overview" />
              <Tab label="Ask AI" />
              <Tab label="History" />
            </Tabs>
          </Paper>

          {/* Tab content */}
          <TabPanel value={tabIndex} index={0}>
            <OverviewTab
              summaryData={summaryData}
              summaryLoading={summaryLoading}
              summaryError={summaryError}
            />
          </TabPanel>

          <TabPanel value={tabIndex} index={1}>
            <AskAITab
              symbol={symbol}
              qaQuestion={qaQuestion}
              onQuestionChange={setQaQuestion}
              onAsk={handleAskAI}
              qaData={qaData}
              qaLoading={qaLoading}
              qaError={qaError}
            />
          </TabPanel>

          <TabPanel value={tabIndex} index={2}>
            <HistoryTab
              symbol={symbol}
              historyData={historyData}
              historyLoading={historyLoading}
              historyError={historyError}
              onGenerate={handleFetchHistory}
            />
          </TabPanel>
        </Container>
      </Box>
    </>
  );
}

export default App;
