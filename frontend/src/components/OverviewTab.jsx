// src/components/OverviewTab.jsx
import {
  Stack,
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
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

function OverviewTab({ summaryData, summaryLoading, summaryError }) {
  // ---- error / loading guards ----
  if (summaryError) {
    return (
      <Paper sx={{ p: 2 }}>
        <Typography color="error">Error: {summaryError}</Typography>
      </Paper>
    );
  }

  if (!summaryLoading && !summaryData) {
    return (
      <Typography>
        Select a symbol and date range, then click <b>Show</b> to load data.
      </Typography>
    );
  }

  if (summaryLoading && !summaryData) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  // ---- main layout ----
  return (
    <>
  {/* ============ ROW 1 CONTAINER: CHART + INDICATORS ============ */}
  <Grid container spacing={2}>
    {/* Chart column */}
    <Grid size={8}>
      <Paper sx={{ p: 3, height: "100%" }}>
        <Typography variant="h6" sx={{ mb: 1 }} align={"center"}>
          Price Chart ({summaryData.start_date} → {summaryData.end_date})
        </Typography>

        <Box sx={{ width: "100%", height: { xs: 260, md: 380 } }}>
          {summaryData.chart && summaryData.chart.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={summaryData.chart}>
                <defs>
                  <linearGradient
                    id="priceGradient"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="0%"
                      stopColor="#1976d2"
                      stopOpacity={0.4}
                    />
                    <stop
                      offset="95%"
                      stopColor="#1976d2"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>

                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" />
                <YAxis
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
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="#1976d2"
                  fill="url(#priceGradient)"
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <Typography>No chart data available.</Typography>
          )}
        </Box>
      </Paper>
    </Grid>

    {/* Indicators column */}
    <Grid size={4} >
      <Paper sx={{ p: 3, height: "100%", }}>
        <Typography variant="h6" sx={{ mb: 4}} align={"center"}>
          Indicators
        </Typography>

        {summaryData.indicators ? (
          <Stack
          direction="column"
          spacing={4}
          >

            {/* Row 1 — Price Card */}
            <Grid >
              <Paper
                elevation={3}
                sx={{
                  p: 3,
                  borderRadius: 1,
                  bgcolor: "#3B413C",
                  color: "#DAF0EE",
                }}
              >
                <Typography variant="subtitle1" sx={{ opacity: 0.8, mb: 1 }} align={"center"}>
                  Prices
                </Typography>

                <Grid container justifyContent="space-around">
                  <Grid>
                    <Typography variant="body2" sx={{ opacity: 0.7 }}>
                      Start
                    </Typography>
                    <Typography variant="h6">
                      {Number(summaryData.indicators.start_price).toLocaleString("en-US", {
                        style: "currency",
                        currency: "USD",
                        maximumFractionDigits: 0,
                      })}
                    </Typography>
                  </Grid>

                  <Grid>
                    <Typography variant="body2" sx={{ opacity: 0.7 }}>
                      End
                    </Typography>
                    <Typography variant="h6">
                      {Number(summaryData.indicators.end_price).toLocaleString("en-US", {
                        style: "currency",
                        currency: "USD",
                        maximumFractionDigits: 0,
                      })}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

            {/* Row 2 — Performance Card */}
            <Grid  >
              <Paper
                elevation={3}
                sx={{
                  p: 3,
                  borderRadius: 1,
                  bgcolor: "#3B413C",
                  color: "#DAF0EE",
                }}
              >
                <Typography variant="subtitle1" sx={{ opacity: 0.8, mb: 1 }} align={"center"}>
                  Performance
                </Typography>

                <Grid container justifyContent="space-around">
                  <Grid>
                    <Typography variant="body2" sx={{ opacity: 0.7 }}>
                      Return
                    </Typography>
                    <Typography
                      variant="h6"
                      sx={{
                        color:
                          summaryData.indicators.return_pct >= 0
                            ? "success.main"
                            : "error.main",
                      }}
                    >
                      {summaryData.indicators.return_pct}%
                    </Typography>
                  </Grid>

                  <Grid>
                    <Typography variant="body2" sx={{ opacity: 0.7 }}>
                      Max Drawdown
                    </Typography>
                    <Typography variant="h6" sx={{ color: "error.main" }}>
                      {summaryData.indicators.max_drawdown_pct}%
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

          </Stack>
        ) : (
          <Typography>No indicators available.</Typography>
        )}
      </Paper>
    </Grid>
  </Grid>

  {/* ============ ROW 2 CONTAINER: AI SUMMARY FULL WIDTH ============ */}
  <Grid container spacing={2} sx={{ mt: 2 }}>
    <Grid>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          AI Summary for changes in the period
        </Typography>
        <Typography variant="body2">
          {summaryData.summary || "No summary available."}
        </Typography>
      </Paper>
    </Grid>
  </Grid>

  {/* ============ ROW 3 CONTAINER: NEWS FULL WIDTH ============ */}
  <Grid container spacing={2} sx={{ mt: 2 }}>
    <Grid size={12}>
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" sx={{ mb: 1 }}>
          Latest News
        </Typography>
        {summaryData.news && summaryData.news.length > 0 ? (
          <List>
            {summaryData.news.map((item, idx) => (
              <Box key={idx}>
                <ListItem
                  component="a"
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  alignItems="flex-start"
                >
                  <ListItemText
                    primary={item.title}
                    secondary={
                      <>
                        <Typography variant="body2">
                          {item.snippet}
                        </Typography>
                        <Typography variant="caption">
                          {item.published_at}
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
          <Typography>No news available.</Typography>
        )}
      </Paper>
    </Grid>
  </Grid>
</>

  );
}

export default OverviewTab;
