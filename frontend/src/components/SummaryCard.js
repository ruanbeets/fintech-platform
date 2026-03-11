export default function SummaryCard({ summary }) {

  if (!summary) {
    return (
      <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 p-6 rounded-2xl shadow-lg">
        <h2 className="text-xl font-semibold mb-4">Financial Summary</h2>
        <p className="text-gray-500">Loading summary...</p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 p-6 rounded-2xl shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Financial Summary</h2>

      <div className="space-y-2">

        <p>
          Total Income:
          <span className="text-green-400 font-medium ml-2">
            ${summary.total_income}
          </span>
        </p>

        <p>
          Total Expenses:
          <span className="text-red-400 font-medium ml-2">
            ${summary.total_expenses}
          </span>
        </p>

        <p>
          Net Cashflow:
          <span className="text-blue-400 font-medium ml-2">
            ${summary.net_cashflow}
          </span>
        </p>

      </div>
    </div>
  );
}