import { Box, Button, Paper, Popover, Stack, Typography } from "@mui/material";

function GuidedTip({
  open,
  anchorEl,
  title,
  description,
  onNext,
  onSkip,
  isLast = false,
}) {
  return (
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onSkip}
      anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
      transformOrigin={{ vertical: "top", horizontal: "left" }}
      slotProps={{
        paper: {
          sx: {
            mt: 1.5,
            maxWidth: 320,
            overflow: "visible",
            borderRadius: 2,
            "&:before": {
              content: '""',
              position: "absolute",
              top: -8,
              left: 22,
              width: 14,
              height: 14,
              bgcolor: "background.paper",
              transform: "rotate(45deg)",
              borderTop: "1px solid",
              borderLeft: "1px solid",
              borderColor: "divider",
            },
          },
        },
      }}
    >
      <Paper elevation={0} sx={{ p: 2 }}>
        <Stack spacing={1.5}>
          <Box>
            <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
              {title}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {description}
            </Typography>
          </Box>
          <Stack direction="row" spacing={1} justifyContent="flex-end">
            <Button size="small" onClick={onSkip}>
              Skip
            </Button>
            <Button size="small" variant="contained" onClick={onNext}>
              {isLast ? "Done" : "Next"}
            </Button>
          </Stack>
        </Stack>
      </Paper>
    </Popover>
  );
}

export default GuidedTip;
