import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Stack,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
} from "@mui/material";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const formatUsd = (value) =>
  Number(value || 0).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });

const formatPct = (value) => `${Number(value || 0).toFixed(2)}%`;

function buildInsightCards(summaryText, indicators) {
  const sentences = (summaryText || "")
    .replace(/\s+/g, " ")
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);

  const fallback = [
    `Price moved from ${formatUsd(indicators.start_price)} to ${formatUsd(indicators.end_price)} in the selected range.`,
    `Net return for the period was ${formatPct(indicators.return_pct)}.`,
    `Maximum drawdown reached ${formatPct(indicators.max_drawdown_pct)} during this window.`,
  ];

  return [0, 1, 2].map((idx) => sentences[idx] || fallback[idx]);
}

function KpiCard({ title, value, tone = "default" }) {
  const colorMap = {
    default: "text.primary",
    positive: "success.main",
    negative: "error.main",
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
        {title}
      </Typography>
      <Typography variant="h6" sx={{ color: colorMap[tone], fontWeight: 700 }}>
        {value}
      </Typography>
    </Paper>
  );
}

function OverviewTab({
  summaryData,
  summaryLoading,
  summaryError,
  summaryLoadingStages = {},
}) {
  if (summaryError) {
    return (
      <Paper sx={{ p: 2.5 }}>
        <Typography color="error">Error: {summaryError}</Typography>
      </Paper>
    );
  }

  if (!summaryLoading && !summaryData) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>
          Ready to analyze
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Pick a symbol and date range, then click Apply Filters to load market insights.
        </Typography>
      </Paper>
    );
  }

  if (summaryLoading && !summaryData) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  const indicators = summaryData.indicators || {};
  const returnValue = Number(indicators.return_pct || 0);
  const drawdownValue = Number(indicators.max_drawdown_pct || 0);
  const insightCards = buildInsightCards(summaryData.summary, indicators);

  return (
    <Stack spacing={2.5}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KpiCard
            title="Start Price"
            value={summaryLoadingStages.indicators ? "Loading..." : formatUsd(indicators.start_price)}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KpiCard
            title="End Price"
            value={summaryLoadingStages.indicators ? "Loading..." : formatUsd(indicators.end_price)}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KpiCard
            title="Return"
            value={summaryLoadingStages.indicators ? "Loading..." : formatPct(indicators.return_pct)}
            tone={returnValue >= 0 ? "positive" : "negative"}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <KpiCard
            title="Max Drawdown"
            value={summaryLoadingStages.indicators ? "Loading..." : formatPct(indicators.max_drawdown_pct)}
            tone={drawdownValue < 0 ? "negative" : "default"}
          />
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Paper sx={{ p: 2.5, height: "100%" }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                Price Trend
              </Typography>
              <Chip label={`${summaryData.start_date} to ${summaryData.end_date}`} size="small" />
            </Stack>

            <Box sx={{ width: "100%", height: { xs: 280, md: 360 } }}>
              {summaryLoadingStages.chart ? (
                <Box sx={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <CircularProgress size={28} />
                </Box>
              ) : summaryData.chart && summaryData.chart.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={summaryData.chart} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#1f6feb" stopOpacity={0.28} />
                        <stop offset="100%" stopColor="#1f6feb" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid stroke="#eef2f7" vertical={false} />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
                    <YAxis
                      tick={{ fontSize: 11 }}
                      tickFormatter={(v) =>
                        v.toLocaleString(undefined, {
                          maximumFractionDigits: 0,
                        })
                      }
                      domain={["dataMin", "dataMax"]}
                    />
                    <Tooltip
                      formatter={(value) =>
                        value.toLocaleString(undefined, {
                          maximumFractionDigits: 2,
                        })
                      }
                      labelFormatter={(label) => `Date: ${label}`}
                    />
                    <Area type="monotone" dataKey="price" stroke="#1f6feb" strokeWidth={2} fill="url(#priceGradient)" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No chart data available.
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Stack spacing={2} sx={{ height: "100%" }}>
            {insightCards.map((insight, idx) => (
              <Paper key={idx} sx={{ p: 2.5, flex: 1 }}>
                <Typography variant="overline" color="text.secondary" sx={{ letterSpacing: 0.8 }}>
                  Market Note {idx + 1}
                </Typography>
                <Typography variant="body2" sx={{ mt: 0.5, lineHeight: 1.7 }}>
                  {summaryLoadingStages.summary ? "Preparing market note..." : insight}
                </Typography>
              </Paper>
            ))}
          </Stack>
        </Grid>
      </Grid>

      <Paper sx={{ p: 2.5 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5 }}>
          Latest News
        </Typography>

        {summaryLoadingStages.news ? (
          <Box sx={{ py: 2, display: "flex", justifyContent: "center" }}>
            <CircularProgress size={24} />
          </Box>
        ) : summaryData.news && summaryData.news.length > 0 ? (
          <List disablePadding>
            {summaryData.news.map((item, idx) => (
              <Box key={idx}>
                <ListItem
                  component="a"
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  alignItems="flex-start"
                  sx={{
                    px: 0,
                    py: 1.5,
                    color: "inherit",
                    textDecoration: "none",
                  }}
                >
                  <ListItemText
                    primary={
                      <Typography variant="body1" sx={{ fontWeight: 600, mb: 0.5 }}>
                        {item.title}
                      </Typography>
                    }
                    secondary={
                      <>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                          {item.snippet || "No snippet available."}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {item.published_at || "Unknown date"}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
                {idx < summaryData.news.length - 1 && <Divider />}
              </Box>
            ))}
          </List>
        ) : (
          <Typography variant="body2" color="text.secondary">
            No news available.
          </Typography>
        )}
      </Paper>
    </Stack>
  );
}

export default OverviewTab;
