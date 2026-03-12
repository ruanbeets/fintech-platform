import { formatCurrency } from "../../utils/currencyUtils";

export default function RecentTransactionsCard({
  transactions = []
}) {

  const recent = transactions.slice(0,5);

  if (!recent.length) return null;

  return (

    <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">

      <h2 className="text-xl font-semibold mb-4">
        Recent Transactions
      </h2>

      {recent.map(tx => (

        <div
          key={tx.transaction_id}
          className="flex justify-between border-t border-gray-800 py-3"
        >

          <div>

            <p>{tx.description}</p>

            <p className="text-xs text-gray-400">
              {tx.category}
            </p>

          </div>

          <p className={
            tx.amount >= 0
              ? "text-green-400"
              : "text-red-400"
          }>

            {formatCurrency(tx.amount)}

          </p>

        </div>

      ))}

    </div>

  );
}