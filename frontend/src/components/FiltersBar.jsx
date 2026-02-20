import { Grid, TextField, MenuItem, Button, Paper, Stack, Typography } from "@mui/material";

const SYMBOL_OPTIONS = ["BTC", "ETH", "SOL", "XRP", "DOGE"];

function FiltersBar({
  symbol,
  startDate,
  endDate,
  onSymbolChange,
  onStartDateChange,
  onEndDateChange,
  onShow,
  loading,
  minDate,
  maxDate,
  dateError,
  showApplyButton = true,
  symbolAnchorId,
  applyButtonId,
}) {
  return (
    <Paper sx={{ p: { xs: 2, md: 2.5 } }}>
      <Stack spacing={2}>
        <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" spacing={1}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
            Market Filters
          </Typography>
          <Typography variant="caption" color="text.secondary">
            CoinGecko free tier: use data in the allowed recent window only.
          </Typography>
        </Stack>

        <Grid container spacing={2} alignItems="flex-start">
          <Grid id={symbolAnchorId} size={{ xs: 12, sm: 6, md: showApplyButton ? 2.5 : 4 }}>
            <TextField
              select
              fullWidth
              label="Symbol"
              value={symbol}
              onChange={(e) => onSymbolChange(e.target.value)}
            >
              {SYMBOL_OPTIONS.map((opt) => (
                <MenuItem key={opt} value={opt}>
                  {opt}
                </MenuItem>
              ))}
            </TextField>
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: showApplyButton ? 3 : 4 }}>
            <TextField
              fullWidth
              label="Start Date"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={startDate}
              onChange={(e) => onStartDateChange(e.target.value)}
              inputProps={{ min: minDate, max: maxDate }}
              error={Boolean(dateError)}
              helperText={dateError || `Allowed: ${minDate} to ${maxDate}`}
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6, md: showApplyButton ? 3 : 4 }}>
            <TextField
              fullWidth
              label="End Date"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={endDate}
              onChange={(e) => onEndDateChange(e.target.value)}
              inputProps={{ min: minDate, max: maxDate }}
              error={Boolean(dateError)}
              helperText={dateError || "No future dates allowed"}
            />
          </Grid>

          {showApplyButton && (
            <Grid size={{ xs: 12, sm: 6, md: 3.5 }}>
              <Button
                id={applyButtonId}
                fullWidth
                size="large"
                variant="contained"
                onClick={onShow}
                disabled={loading || Boolean(dateError)}
                sx={{ height: 40 }}
              >
                {loading ? "Loading..." : "Apply Filters"}
              </Button>
            </Grid>
          )}
        </Grid>
      </Stack>
    </Paper>
  );
}

export default FiltersBar;
