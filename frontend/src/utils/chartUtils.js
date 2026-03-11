export function buildSummaryChart(summary) {
  if (!summary) return null;

  return {
    labels: ["Income", "Expenses"],
    datasets: [
      {
        label: "Amount",
        data: [
          summary.total_income,
          Math.abs(summary.total_expenses)
        ],
        backgroundColor: ["#4caf50", "#f44336"]
      }
    ]
  };
}

export function buildCategoryChart(categorySummary) {
  if (!categorySummary) return null;

  return {
    labels: Object.keys(categorySummary),
    datasets: [
      {
        label: "Total by Category",
        data: Object.values(categorySummary).map((v) =>
          Math.abs(v)
        ),
        backgroundColor: "#2196f3"
      }
    ]
  };
}