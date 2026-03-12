/** @type {import('tailwindcss').Config} */
module.exports = {

  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],

  theme: {

    extend: {

      colors: {

        fintech: {

          bg: "#0b0f19",
          card: "#111827",
          border: "#1f2937",
          text: "#e5e7eb",

          income: "#22c55e",
          expense: "#ef4444",
          accent: "#3b82f6"

        }

      }

    },

  },

  plugins: [],

}