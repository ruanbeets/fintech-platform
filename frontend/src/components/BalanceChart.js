import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
} from "chart.js";

import { Line } from "react-chartjs-2";

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
);

function BalanceChart({ transactions }) {

  if (!transactions || transactions.length === 0) {
    return null;
  }

  // sort transactions chronologically
  const sorted = [...transactions].sort(
    (a, b) => new Date(a.date) - new Date(b.date)
  );

  const data = {
    labels: sorted.map(tx =>
      new Date(tx.date).toLocaleDateString()
    ),
    datasets: [
      {
        label: "Balance",
        data: sorted.map(tx => tx.balance),
        borderColor: "#4ade80",
        backgroundColor: "#4ade80",
        tension: 0.3,
        pointRadius: 2
      }
    ]
  };

  const options = {
    plugins: {
      legend: {
        labels: {
          color: "#9CA3AF"
        }
      }
    },
    scales: {
      x: {
        ticks: { color: "#9CA3AF" },
        grid: { color: "rgba(255,255,255,0.05)" }
      },
      y: {
        ticks: { color: "#9CA3AF" },
        grid: { color: "rgba(255,255,255,0.05)" }
      }
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 p-6 rounded-2xl shadow-lg">
      <h3 className="mb-4">Balance Over Time</h3>
      <Line data={data} options={options} />
    </div>
  );
}

export default BalanceChart;