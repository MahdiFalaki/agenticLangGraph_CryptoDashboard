// src/components/AskAITab.jsx
import {
  Box,
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
} from "@mui/material";

function AskAITab({
  symbol,
  qaQuestion,
  onQuestionChange,
  onAsk,
  qaData,
  qaLoading,
  qaError,
}) {
  return (
    <>
      {/* Top card: question input */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Ask AI about {symbol}
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          The question will be answered using price &amp; news in the selected
          date range.
        </Typography>

        <TextField
          fullWidth
          multiline
          minRows={3}
          label="Your question"
          value={qaQuestion}
          onChange={(e) => onQuestionChange(e.target.value)}
          sx={{ mb: 2 }}
        />

        <Button
          variant="contained"
          onClick={onAsk}
          disabled={qaLoading || !qaQuestion.trim()}
        >
          {qaLoading ? "Thinking..." : "Ask"}
        </Button>
      </Paper>

      {/* Error card */}
      {qaError && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography color="error">Error: {qaError}</Typography>
        </Paper>
      )}

      {/* Loading spinner while no data yet */}
      {qaLoading && !qaData && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Answer + Supporting News */}
      {qaData && (
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Left: AI Answer */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2, height: "100%" }}>
              <Typography variant="h6" gutterBottom>
                AI Answer
              </Typography>
              <Typography
                variant="body2"
                sx={{ whiteSpace: "pre-line" }} // nicer wrapping if LLM uses line breaks
              >
                {qaData.answer}
              </Typography>
            </Paper>
          </Grid>

          {/* Right: Supporting News */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2, height: "100%" }}>
              <Typography variant="h6" gutterBottom>
                Supporting News
              </Typography>
              {qaData.news && qaData.news.length > 0 ? (
                <List dense>
                  {qaData.news.map((item, idx) => (
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
                              <Typography variant="body2" component="span">
                                {item.snippet}
                              </Typography>
                              <br />
                              <Typography variant="caption" component="span">
                                {item.published_at}
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                      {idx < qaData.news.length - 1 && <Divider />}
                    </Box>
                  ))}
                </List>
              ) : (
                <Typography variant="body2">
                  No supporting news available.
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      )}
    </>
  );
}

export default AskAITab;
