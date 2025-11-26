// src/components/HistoryTab.jsx
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Link,
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

function HistoryTab({
  symbol,
  historyData,
  historyLoading,
  historyError,
  onGenerate,
}) {
  return (
    <>
      {/* Top control panel */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6">History Story for {symbol}</Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          This will generate a background story for the asset using its price chart
          and external sources (Wikipedia and other web pages). The list on the right
          shows the sources used.
        </Typography>
        <Button
          variant="contained"
          onClick={onGenerate}
          disabled={historyLoading}
        >
          {historyLoading ? "Loading..." : "Generate History Story"}
        </Button>
      </Paper>

      {historyError && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography color="error">Error: {historyError}</Typography>
        </Paper>
      )}

      {historyLoading && !historyData && (
        <Box display="flex" justifyContent="center" mt={2}>
          <CircularProgress />
        </Box>
      )}

      {historyData && (
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Chart */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2, height: "100%", width: "171vh" }}>
              <Typography variant="h6" sx={{ mb: 1 }}>
                History Chart
              </Typography>
              <Box sx={{ height: 300 }}>
                {historyData.chart && historyData.chart.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={historyData.chart}>
                      <defs>
                        <linearGradient
                          id="historyGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor="#9c27b0"
                            stopOpacity={0.4}
                          />
                          <stop
                            offset="95%"
                            stopColor="#9c27b0"
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
                        stroke="#9c27b0"
                        fill="url(#historyGradient)"
                        dot={false}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <Typography>No history chart data available.</Typography>
                )}
              </Box>
            </Paper>
          </Grid>

          {/* Story + Sources */}
          <Grid item xs={12} md={4}>
            <Paper
              sx={{
                p: 2,
                height: "100%",
                display: "flex",
                flexDirection: "column",
              }}
            >
              <Typography variant="h6" sx={{ mb: 1 }}>
                History Story
              </Typography>
              <Typography variant="body2">
                {historyData.history_story || "No history story available."}
              </Typography>

              {/* Sources list */}
              {historyData.news && historyData.news.length > 0 && (
                <Box mt={2}>
                  <Typography variant="subtitle1" sx={{ mb: 1 }}>
                    Sources used for this history
                  </Typography>

                  {historyData.news.map((item, idx) => {
                    const dateLabel =
                      item?.published_at && item.published_at.length > 0
                        ? item.published_at.slice(0, 10)
                        : "";

                    const isWikipedia =
                      item.title?.startsWith("Wikipedia:") ||
                      (item.url && item.url.includes("wikipedia.org"));

                    return (
                      <Box key={idx} mb={1}>
                        <Typography
                          variant="body2"
                          fontWeight={600}
                          color={isWikipedia ? "primary.main" : "inherit"}
                        >
                          {dateLabel && `${dateLabel} – `}
                          <Link
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {item.title}
                          </Link>
                          {isWikipedia && (
                            <Typography
                              variant="caption"
                              component="span"
                              sx={{ ml: 0.5 }}
                            >
                              (Wikipedia)
                            </Typography>
                          )}
                        </Typography>

                        <Typography variant="body2" color="text.secondary">
                          {item.snippet}
                        </Typography>
                      </Box>
                    );
                  })}
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </>
  );
}

export default HistoryTab;
