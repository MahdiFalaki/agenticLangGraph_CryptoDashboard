import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";

import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1f6feb",
    },
    success: {
      main: "#15803d",
    },
    error: {
      main: "#b42318",
    },
    text: {
      primary: "#111827",
      secondary: "#667085",
    },
    background: {
      default: "#f3f6fb",
      paper: "#ffffff",
    },
  },
  typography: {
    fontFamily: '"IBM Plex Sans", "Segoe UI", "Helvetica Neue", Arial, sans-serif',
    h6: {
      fontWeight: 700,
      letterSpacing: 0.2,
    },
  },
  shape: {
    borderRadius: 14,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          border: "1px solid #e4e7ec",
          boxShadow: "0 1px 2px rgba(16,24,40,0.06)",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          textTransform: "none",
          fontWeight: 600,
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        size: "small",
      },
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
