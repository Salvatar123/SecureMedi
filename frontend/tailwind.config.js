module.exports = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#667eea",
        secondary: "#764ba2",
        danger: "#f43f5e",
        warning: "#f59e0b",
        success: "#10b981",
        info: "#06b6d4",
        background: "#0f172a",
        foreground: "#f1f5f9",
        card: "#1e293b",
        border: "#334155",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
