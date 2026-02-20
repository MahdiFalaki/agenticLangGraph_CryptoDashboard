import { useEffect, useMemo, useState } from "react";
import {
  Typography,
  Box,
  Container,
  Stack,
} from "@mui/material";

import DrawerAppBar from "./components/DrawerAppBar.jsx";
import FiltersBar from "./components/FiltersBar.jsx";
import OverviewTab from "./components/OverviewTab.jsx";
import AskAITab from "./components/AskAITab.jsx";
import HistoryTab from "./components/HistoryTab.jsx";
import GuidedTip from "./components/GuidedTip.jsx";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const COINGECKO_FREE_TIER_DAYS = 365;
const ALLOWED_WINDOW_DAYS = Math.floor(COINGECKO_FREE_TIER_DAYS * 0.75);

const formatAsIsoDate = (date) => date.toISOString().slice(0, 10);

const today = new Date();
today.setHours(0, 0, 0, 0);
const minAllowedDateObj = new Date(today);
minAllowedDateObj.setDate(today.getDate() - ALLOWED_WINDOW_DAYS);

const MAX_ALLOWED_DATE = formatAsIsoDate(today);
const MIN_ALLOWED_DATE = formatAsIsoDate(minAllowedDateObj);
const TOUR_STORAGE_PREFIX = "crypto_dashboard_tour_v1";

function getDateValidationError(startDate, endDate) {
  if (!startDate || !endDate) return "Start date and end date are required.";
  if (startDate > endDate) return "Start date must be before or equal to end date.";
  if (startDate < MIN_ALLOWED_DATE || endDate < MIN_ALLOWED_DATE) {
    return `Date must be within the last ${ALLOWED_WINDOW_DAYS} days (${MIN_ALLOWED_DATE} to ${MAX_ALLOWED_DATE}).`;
  }
  if (startDate > MAX_ALLOWED_DATE || endDate > MAX_ALLOWED_DATE) {
    return "Future dates are not allowed.";
  }
  return "";
}

function App() {
  // ---- state ----
  const [symbol, setSymbol] = useState("BTC");
  const [startDate, setStartDate] = useState(MIN_ALLOWED_DATE);
  const [endDate, setEndDate] = useState(MAX_ALLOWED_DATE);
  const [tabIndex, setTabIndex] = useState(0);
  const [dateError, setDateError] = useState("");

  const [summaryData, setSummaryData] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState(null);
  const [summaryLoadingStages, setSummaryLoadingStages] = useState({
    indicators: false,
    chart: false,
    summary: false,
    news: false,
  });

  const [qaQuestion, setQaQuestion] = useState("");
  const [qaData, setQaData] = useState(null);
  const [qaLoading, setQaLoading] = useState(false);
  const [qaError, setQaError] = useState(null);

  const [historyData, setHistoryData] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState(null);
  const [activeTip, setActiveTip] = useState(null);

  const tipConfigsByTab = useMemo(
    () => ({
      0: [
        {
          anchorId: "tour-symbol-field",
          title: "Choose a market",
          description:
            "Pick the symbol you want to analyze before applying filters.",
        },
        {
          anchorId: "tour-apply-filters",
          title: "Load market data",
          description:
            "Apply filters to load metrics, chart, market notes, and news in sequence.",
        },
      ],
      1: [
        {
          anchorId: "tour-question-field",
          title: "Ask a question",
          description:
            "Write a focused question to get a grounded market response with supporting sources.",
        },
      ],
      2: [
        {
          anchorId: "tour-history-generate",
          title: "Generate history",
          description:
            "Use this to create a concise background story with linked source references.",
        },
      ],
    }),
    []
  );

  useEffect(() => {
    const key = `${TOUR_STORAGE_PREFIX}_tab_${tabIndex}`;
    if (localStorage.getItem(key) === "1") return;
    const steps = tipConfigsByTab[tabIndex] || [];
    if (!steps.length) return;

    const timer = setTimeout(() => {
      setActiveTip({ tab: tabIndex, steps, index: 0 });
    }, 250);

    return () => clearTimeout(timer);
  }, [tabIndex, tipConfigsByTab]);

  const closeTipFlow = (tab) => {
    const key = `${TOUR_STORAGE_PREFIX}_tab_${tab}`;
    localStorage.setItem(key, "1");
    setActiveTip(null);
  };

  const handleTipNext = () => {
    if (!activeTip) return;
    if (activeTip.index >= activeTip.steps.length - 1) {
      closeTipFlow(activeTip.tab);
      return;
    }
    setActiveTip((prev) => ({ ...prev, index: prev.index + 1 }));
  };

  const handleTipSkip = () => {
    if (!activeTip) return;
    closeTipFlow(activeTip.tab);
  };

  const currentTip = activeTip ? activeTip.steps[activeTip.index] : null;
  const currentTipAnchorEl = currentTip
    ? document.getElementById(currentTip.anchorId)
    : null;

  const handleStartDateChange = (value) => {
    setStartDate(value);
    setDateError(getDateValidationError(value, endDate));
  };

  const handleEndDateChange = (value) => {
    setEndDate(value);
    setDateError(getDateValidationError(startDate, value));
  };

  const validateDatesOrSetError = (setError) => {
    const error = getDateValidationError(startDate, endDate);
    setDateError(error);
    if (!error) return true;
    if (setError) setError(error);
    return false;
  };

  const fetchJson = async (url, payload) => {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    return response.json();
  };

  const fetchWithStatus = async (url, payload) => {
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return response;
  };

  // ---- API calls ----
  const handleFetchSummary = async () => {
    if (!validateDatesOrSetError(setSummaryError)) return;
    setSummaryLoading(true);
    setSummaryError(null);
    const payload = { start_date: startDate, end_date: endDate };

    setSummaryData({
      start_date: startDate,
      end_date: endDate,
      chart: [],
      indicators: null,
      summary: "",
      news: [],
    });
    setSummaryLoadingStages({
      indicators: true,
      chart: true,
      summary: true,
      news: true,
    });

    try {
      const marketResponse = await fetchWithStatus(
        `${API_BASE_URL}/api/asset/${symbol}/market`,
        payload
      );

      // Backward compatibility: if staged endpoints are unavailable, use legacy /summary.
      if (marketResponse.status === 404) {
        const legacy = await fetchJson(
          `${API_BASE_URL}/api/asset/${symbol}/summary`,
          payload
        );
        setSummaryData(legacy);
        setSummaryLoadingStages({
          indicators: false,
          chart: false,
          summary: false,
          news: false,
        });
        return;
      }

      if (!marketResponse.ok) {
        throw new Error(`Request failed with status ${marketResponse.status}`);
      }
      const market = await marketResponse.json();

      setSummaryData((prev) => ({
        ...prev,
        start_date: market.start_date,
        end_date: market.end_date,
        indicators: market.indicators,
      }));
      setSummaryLoadingStages((prev) => ({ ...prev, indicators: false }));

      setSummaryData((prev) => ({ ...prev, chart: market.chart || [] }));
      setSummaryLoadingStages((prev) => ({ ...prev, chart: false }));

      const summaryText = await fetchJson(
        `${API_BASE_URL}/api/asset/${symbol}/summary_text`,
        payload
      );
      setSummaryData((prev) => ({ ...prev, summary: summaryText.summary || "" }));
      setSummaryLoadingStages((prev) => ({ ...prev, summary: false }));

      const newsData = await fetchJson(
        `${API_BASE_URL}/api/asset/${symbol}/news`,
        payload
      );
      setSummaryData((prev) => ({ ...prev, news: newsData.news || [] }));
      setSummaryLoadingStages((prev) => ({ ...prev, news: false }));
    } catch (err) {
      setSummaryError(err.message || "Unknown error");
      setSummaryData(null);
      setSummaryLoadingStages({
        indicators: false,
        chart: false,
        summary: false,
        news: false,
      });
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleAskAI = async () => {
    if (!qaQuestion.trim()) return;
    if (!validateDatesOrSetError(setQaError)) return;

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
    if (!validateDatesOrSetError(setHistoryError)) return;
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const payload = {
        start_date: startDate,
        end_date: endDate,
      };

      let response;
      try {
        response = await fetch(`${API_BASE_URL}/api/asset/${symbol}/history`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } catch {
        // One retry for transient network hiccups.
        response = await fetch(`${API_BASE_URL}/api/asset/${symbol}/history`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = await response.json();
      setHistoryData(data);
    } catch (err) {
      const rawMessage = err?.message || "Unknown error";
      if (rawMessage.includes("Failed to fetch")) {
        setHistoryError(
          `Network error: unable to reach backend at ${API_BASE_URL}. Confirm backend is running and reachable from this browser.`
        );
      } else {
        setHistoryError(rawMessage);
      }
      setHistoryData(null);
    } finally {
      setHistoryLoading(false);
    }
  };

  return (
    <>
      <DrawerAppBar tabIndex={tabIndex} onTabChange={(i) => setTabIndex(i)} />

      <Box sx={{ bgcolor: "background.default", minHeight: "100vh" }}>
        <Container maxWidth="xl" sx={{ py: { xs: 2, md: 3 } }}>
          <Stack spacing={2.5}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
                Overview Workspace
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Track price movement, market highlights, and relevant news in one view.
              </Typography>
            </Box>

            <FiltersBar
              symbol={symbol}
              startDate={startDate}
              endDate={endDate}
              onSymbolChange={setSymbol}
              onStartDateChange={handleStartDateChange}
              onEndDateChange={handleEndDateChange}
              onShow={handleFetchSummary}
              loading={summaryLoading}
              minDate={MIN_ALLOWED_DATE}
              maxDate={MAX_ALLOWED_DATE}
              dateError={dateError}
              showApplyButton={tabIndex === 0}
              symbolAnchorId="tour-symbol-field"
              applyButtonId="tour-apply-filters"
            />

            {tabIndex === 0 && (
              <OverviewTab
                summaryData={summaryData}
                summaryLoading={summaryLoading}
                summaryError={summaryError}
                summaryLoadingStages={summaryLoadingStages}
              />
            )}

            {tabIndex === 1 && (
              <AskAITab
                symbol={symbol}
                qaQuestion={qaQuestion}
                onQuestionChange={setQaQuestion}
                onAsk={handleAskAI}
                qaData={qaData}
                qaLoading={qaLoading}
                qaError={qaError}
                questionFieldId="tour-question-field"
              />
            )}

            {tabIndex === 2 && (
              <HistoryTab
                symbol={symbol}
                historyData={historyData}
                historyLoading={historyLoading}
                historyError={historyError}
                onGenerate={handleFetchHistory}
                generateButtonId="tour-history-generate"
              />
            )}
          </Stack>
        </Container>
      </Box>

      <GuidedTip
        open={Boolean(activeTip && currentTipAnchorEl)}
        anchorEl={currentTipAnchorEl}
        title={currentTip?.title || ""}
        description={currentTip?.description || ""}
        onNext={handleTipNext}
        onSkip={handleTipSkip}
        isLast={Boolean(activeTip && activeTip.index === activeTip.steps.length - 1)}
      />
    </>
  );
}

export default App;
