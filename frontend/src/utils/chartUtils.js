// src/utils/chartUtils.js

// ===============================
// BALANCE OVER TIME
// ===============================

export function buildBalanceChart(transactions = []) {

  const sorted = [...transactions].sort(
    (a, b) => new Date(a.date) - new Date(b.date)
  );

  return {
    labels: sorted.map(tx =>
      new Date(tx.date).toLocaleDateString()
    ),
    datasets: [
      {
        label: "Balance",
        data: sorted.map(tx => tx.balance),
        borderColor: "#22c55e",
        backgroundColor: "rgba(34,197,94,0.15)",
        tension: 0.3,
        fill: true
      }
    ]
  };

}


// ===============================
// CASHFLOW CHART
// ===============================

export function buildCashFlowChart(summary) {

  if (!summary) return null;

  return {
    labels: ["Income", "Expenses"],
    datasets: [
      {
        label: "Amount",
        data: [
          summary.total_income || 0,
          Math.abs(summary.total_expenses || 0)
        ],
        backgroundColor: [
          "#22c55e",
          "#ef4444"
        ]
      }
    ]
  };

}


// ===============================
// CATEGORY BREAKDOWN
// ===============================

export function buildCategoryChart(categories) {

  if (!categories) return null;

  // If backend returned object instead of array
  if (!Array.isArray(categories)) {
    categories = Object.entries(categories).map(
      ([category, total]) => ({
        category,
        total
      })
    );
  }

  return {

    labels: categories.map(c => c.category),

    datasets: [
      {
        label: "Spending",
        data: categories.map(c => Math.abs(c.total)),
        backgroundColor: [
          "#3b82f6",
          "#6366f1",
          "#8b5cf6",
          "#ec4899",
          "#f59e0b",
          "#ef4444",
          "#10b981"
        ]
      }
    ]

  };

}


// ===============================
// MONTHLY TREND
// ===============================

export function buildMonthlyTrend(transactions = []) {

  const months = {};

  transactions.forEach(tx => {

    const month = new Date(tx.date)
      .toLocaleDateString(undefined, {
        year: "numeric",
        month: "short"
      });

    if (!months[month]) {

      months[month] = {
        income: 0,
        expenses: 0
      };

    }

    if (tx.amount > 0) {
      months[month].income += tx.amount;
    } else {
      months[month].expenses += Math.abs(tx.amount);
    }

  });

  const labels = Object.keys(months);

  return {

    labels,

    datasets: [

      {
        label: "Income",
        data: labels.map(m => months[m].income),
        backgroundColor: "#22c55e"
      },

      {
        label: "Expenses",
        data: labels.map(m => months[m].expenses),
        backgroundColor: "#ef4444"
      }

    ]

  };

}


// ===============================
// ACCOUNT ALLOCATION
// ===============================

export function buildAccountAllocation(accounts = []) {

  return {

    labels: accounts.map(a => a.account_type),

    datasets: [
      {
        label: "Account Balance",
        data: accounts.map(a => a.balance),
        backgroundColor: [
          "#3b82f6",
          "#10b981",
          "#f59e0b",
          "#ef4444",
          "#8b5cf6"
        ]
      }
    ]

  };

}