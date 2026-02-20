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
  Stack,
} from "@mui/material";

function AskAITab({
  symbol,
  qaQuestion,
  onQuestionChange,
  onAsk,
  qaData,
  qaLoading,
  qaError,
  questionFieldId,
}) {
  return (
    <>
      <Paper sx={{ p: 2.5, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Market Q&A for {symbol}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Responses are based on price indicators and supporting news context.
        </Typography>

        <TextField
          id={questionFieldId}
          fullWidth
          multiline
          minRows={3}
          label="Your question"
          value={qaQuestion}
          onChange={(e) => onQuestionChange(e.target.value)}
          sx={{ mb: 2 }}
        />

        <Button variant="contained" onClick={onAsk} disabled={qaLoading || !qaQuestion.trim()}>
          {qaLoading ? "Working..." : "Get Answer"}
        </Button>
      </Paper>

      {qaError && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography color="error">Error: {qaError}</Typography>
        </Paper>
      )}

      {qaLoading && !qaData && (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
          <CircularProgress />
        </Box>
      )}

      {qaData && (
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid size={{ xs: 12, md: 8 }}>
            <Paper sx={{ p: 2.5, height: "100%" }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5 }}>
                Response
              </Typography>
              <Typography variant="body2" sx={{ whiteSpace: "pre-line", lineHeight: 1.7 }}>
                {qaData.answer}
              </Typography>
            </Paper>
          </Grid>

          <Grid size={{ xs: 12, md: 4 }}>
            <Paper sx={{ p: 2.5, height: "100%" }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5 }}>
                Supporting News
              </Typography>
              {qaData.news && qaData.news.length > 0 ? (
                <List dense disablePadding>
                  {qaData.news.map((item, idx) => (
                    <Box key={idx}>
                      <ListItem
                        component="a"
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        alignItems="flex-start"
                        sx={{ px: 0, py: 1.2, color: "inherit", textDecoration: "none" }}
                      >
                        <ListItemText
                          primary={
                            <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.4 }}>
                              {item.title}
                            </Typography>
                          }
                          secondary={
                            <Stack spacing={0.5}>
                              <Typography variant="caption" color="text.secondary">
                                {item.snippet}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {item.published_at}
                              </Typography>
                            </Stack>
                          }
                        />
                      </ListItem>
                      {idx < qaData.news.length - 1 && <Divider />}
                    </Box>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
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
