import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Link,
  Stack,
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
  generateButtonId,
}) {
  return (
    <>
      <Paper sx={{ p: 2.5, mb: 2 }}>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          justifyContent="space-between"
          spacing={2}
        >
          <Box>
            <Typography variant="h6">Background Brief for {symbol}</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Generate a grounded background story with chart context and source links.
            </Typography>
          </Box>
          <Button id={generateButtonId} variant="contained" onClick={onGenerate} disabled={historyLoading}>
            {historyLoading ? "Loading..." : "Generate History Story"}
          </Button>
        </Stack>
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
          <Grid size={{ xs: 12, md: 8 }}>
            <Paper sx={{ p: 2.5, height: "100%" }}>
              <Typography variant="subtitle1" sx={{ mb: 1.5, fontWeight: 700 }}>
                History Chart
              </Typography>
              <Box sx={{ height: 300 }}>
                {historyData.chart && historyData.chart.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={historyData.chart}>
                      <defs>
                        <linearGradient id="historyGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#1f6feb" stopOpacity={0.28} />
                          <stop offset="100%" stopColor="#1f6feb" stopOpacity={0} />
                        </linearGradient>
                      </defs>

                      <CartesianGrid stroke="#eef2f7" vertical={false} />
                      <XAxis dataKey="date" minTickGap={24} />
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
                        stroke="#1f6feb"
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

          <Grid size={{ xs: 12, md: 4 }}>
            <Paper sx={{ p: 2.5, height: "100%" }}>
              <Typography variant="subtitle1" sx={{ mb: 1.5, fontWeight: 700 }}>
                History Story
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {historyData.history_story || "No history story available."}
              </Typography>

              {historyData.news && historyData.news.length > 0 && (
                <Box mt={2}>
                  <Typography variant="subtitle2" sx={{ mb: 1 }}>
                    Sources
                  </Typography>

                  {historyData.news.map((item, idx) => {
                    const dateLabel =
                      item?.published_at && item.published_at.length > 0
                        ? item.published_at.slice(0, 10)
                        : "";

                    return (
                      <Box key={idx} mb={1.5}>
                        <Typography variant="body2" fontWeight={600}>
                          {dateLabel && `${dateLabel} - `}
                          <Link href={item.url} target="_blank" rel="noopener noreferrer">
                            {item.title}
                          </Link>
                        </Typography>

                        <Typography variant="caption" color="text.secondary">
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
