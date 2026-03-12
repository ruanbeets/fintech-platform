import { formatCurrency } from "../../utils/currencyUtils";

export default function BudgetProgressBar({
  transactions = [],
  monthlyBudget = 5000
}) {

  const month = new Date()
    .toISOString()
    .slice(0,7);

  const spending = transactions
    .filter(tx =>
      tx.amount < 0 &&
      tx.date.startsWith(month)
    )
    .reduce(
      (sum, tx) => sum + Math.abs(tx.amount),
      0
    );

  const percent = Math.min(
    (spending / monthlyBudget) * 100,
    100
  );

  return (

    <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">

      <h3 className="text-sm text-gray-400 mb-2">
        Monthly Budget
      </h3>

      <p className="text-lg mb-3">
        {formatCurrency(spending)} / {formatCurrency(monthlyBudget)}
      </p>

      <div className="w-full bg-gray-800 h-3 rounded">

        <div
          className="bg-blue-500 h-3 rounded"
          style={{ width: `${percent}%` }}
        />

      </div>

      <p className="text-xs text-gray-500 mt-2">
        {percent.toFixed(1)}% used
      </p>

    </div>

  );
}