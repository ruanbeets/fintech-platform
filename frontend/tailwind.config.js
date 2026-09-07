/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",

  theme: {
    extend: {
      colors: {
        "surface-container-lowest": "#060e20",
        "surface-container-low": "#131b2e",
        "surface-container": "#171f33",
        "surface-container-high": "#222a3d",
        "surface-container-highest": "#2d3449",
        "surface-bright": "#31394d",

        "on-surface": "#dae2fd",
        "on-surface-variant": "#bbc9cf",

        "primary": "#4cd6ff",
        "primary-container": "#00d1ff",
        "primary-fixed-dim": "#4cd6ff",

        "secondary": "#4edea3",
        "secondary-container": "#00a572",

        "outline": "#859399",
        "outline-variant": "#3c494e",
      },

      fontFamily: {
        headline: ["Manrope"],
        body: ["Inter"],
        label: ["Inter"],
      },

      borderRadius: {
        xl: "0.5rem",
        "2xl": "1rem",
      },
    },
  },

  plugins: [],
};