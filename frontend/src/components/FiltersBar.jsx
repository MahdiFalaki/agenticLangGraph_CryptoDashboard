// src/components/FiltersBar.jsx
import { Box, Grid, TextField, MenuItem, Button, Paper } from "@mui/material";

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
}) {
  return (
    <Paper sx={{ p: 2 }}>
      <Grid container alignItems="center" spacing={2}>
        <Grid>
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

        <Grid >
          <TextField
            fullWidth
            label="Start Date"
            type="date"
            InputLabelProps={{ shrink: true }}
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
          />
        </Grid>

        <Grid >
          <TextField
            fullWidth
            label="End Date"
            type="date"
            InputLabelProps={{ shrink: true }}
            value={endDate}
            onChange={(e) => onEndDateChange(e.target.value)}
          />
        </Grid>

        <Grid sx={{ ml: "auto", pr: 2 }}>
          {/*<Box sx={{ display: "flex", justifyContent: "flex-end" }}>*/}
            <Button
              sx={{backgroundColor:"#3B413C",
              color: "#DAF0EE",
              }}
              fullWidth
              variant="contained"
              onClick={onShow}
              disabled={loading}
            >
              {loading ? "Loading..." : "Show"}
            </Button>
          {/*</Box>*/}
        </Grid>
      </Grid>
    </Paper>
  );
}

export default FiltersBar;
