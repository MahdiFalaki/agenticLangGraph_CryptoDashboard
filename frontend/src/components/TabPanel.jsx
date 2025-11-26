// src/components/TabPanel.jsx
import { Box } from "@mui/material";

function TabPanel({ value, index, children }) {
  if (value !== index) return null;
  return <Box sx={{ mt: 2 }}>{children}</Box>;
}

export default TabPanel;
