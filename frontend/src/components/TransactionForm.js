export default function TransactionForm({
  accounts = [],
  selectedAccount,
  setSelectedAccount,
  amount,
  setAmount,
  date,
  setDate,
  category,
  setCategory,
  description,
  setDescription,
  handleSubmit
}) {

  const safeAccounts = Array.isArray(accounts) ? accounts : [];

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 p-6 rounded-2xl shadow-lg">
      <h2 className="text-xl font-semibold mb-4">Create Transaction</h2>

      <form onSubmit={handleSubmit} className="space-y-4">

        <select
          required
          value={selectedAccount}
          onChange={(e) => setSelectedAccount(e.target.value)}
          className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg w-full"
        >
          <option value="">-- Select Account --</option>

          {safeAccounts.map((acc) => (
            <option key={acc.account_id} value={acc.account_id}>
              {acc.account_type} ({acc.currency})
            </option>
          ))}

        </select>

        <input
          type="number"
          placeholder="Amount"
          required
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg w-full"
        />

        <div>
          <label className="text-sm text-gray-400 block mb-1">
            Date
          </label>

          <input
            type="date"
            required
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg w-full text-gray-100"
          />
        </div>

        <input
          type="text"
          placeholder="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg w-full"
        />

        <input
          type="text"
          placeholder="Description"
          required
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg w-full"
        />

        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 transition px-6 py-2 rounded-lg font-medium"
        >
          Add Transaction
        </button>

      </form>
    </div>
  );
}