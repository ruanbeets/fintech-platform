import { Bar } from "react-chartjs-2";

export default function ChartsSection({
  chartData,
  categoryChartData,
  chartOptions
}) {
  return (
    <div className="grid md:grid-cols-2 gap-8">
      {chartData && (
        <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 p-6 rounded-2xl shadow-lg">
          <h3 className="mb-4">Cash Flow</h3>
          <Bar data={chartData} options={chartOptions} />
        </div>
      )}

      {categoryChartData && (
        <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 p-6 rounded-2xl shadow-lg">
          <h3 className="mb-4">Category Breakdown</h3>
          <Bar data={categoryChartData} options={chartOptions} />
        </div>
      )}
    </div>
  );
}