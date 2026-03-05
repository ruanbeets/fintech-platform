export default function TransactionList({ transactions, handleDelete }) {
  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 p-6 rounded-2xl shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Transactions</h2>

      {transactions.map(tx => (
        <div key={tx.transaction_id} className="mb-4 border-b border-gray-800 pb-3">
          <p>
            <strong>{tx.category}</strong> — ${tx.amount}
          </p>

          <p className="text-gray-400">{tx.description}</p>

          {/* NEW DATE LINE */}
          <p className="text-gray-500 text-sm">
            {new Date(tx.date).toLocaleDateString("en-US", {
              year: "numeric",
              month: "short",
              day: "numeric"
            })}
          </p>

          <button
            onClick={() => handleDelete(tx.transaction_id)}
            className="mt-2 text-red-400 hover:text-red-300 text-sm"
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}