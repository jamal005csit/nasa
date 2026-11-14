import type { Config } from "tailwindcss";

// Design tokens sourced from docs/SPEC.txt §5.
// Keep this file the single source of truth for UI colors; components use these names.
const config: Config = {
  content: ["./src/**/*.{ts,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        bg: "#070B14",
        surface: "#0E1624",
        "surface-2": "#141F33",
        border: "rgba(160,190,230,0.14)",
        text: "#EAF1FB",
        muted: "#8FA3BF",
        accent: "#38D7FF",
        warn: "#FFB547",
        negative: "#FF7A6B",
        positive: "#5EE6B0",
      },
      fontFamily: {
        sans: ["'Space Grotesk'", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"],
      },
      fontFeatureSettings: {
        tnum: '"tnum"',
      },
      transitionDuration: { DEFAULT: "250ms" },
    },
  },
  plugins: [],
};

export default config;
