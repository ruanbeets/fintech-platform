// src/constants/chartConfig.js

export const chartColors = {
  income: "#22c55e",
  expenses: "#ef4444",
  balance: "#3b82f6",
  savings: "#10b981",
  investment: "#f59e0b",
  categories: [
    "#3b82f6",
    "#6366f1",
    "#8b5cf6",
    "#ec4899",
    "#f59e0b",
    "#ef4444",
    "#10b981"
  ]
};

export const baseChartOptions = {

  responsive: true,

  maintainAspectRatio: false,

  plugins: {

    legend: {
      position: "top",
      labels: {
        color: "#e5e7eb"
      }
    },

    tooltip: {
      mode: "index",
      intersect: false
    }

  },

  scales: {

    x: {
      ticks: {
        color: "#9ca3af"
      },
      grid: {
        color: "rgba(255,255,255,0.05)"
      }
    },

    y: {
      ticks: {
        color: "#9ca3af"
      },
      grid: {
        color: "rgba(255,255,255,0.05)"
      }
    }

  }

};

export const doughnutOptions = {

  responsive: true,

  plugins: {
    legend: {
      position: "bottom",
      labels: {
        color: "#e5e7eb"
      }
    }
  }

};