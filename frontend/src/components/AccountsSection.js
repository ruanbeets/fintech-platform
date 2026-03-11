export default function AccountsSection({ accounts = [] }) {

  const safeAccounts = Array.isArray(accounts) ? accounts : [];

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 p-6 rounded-2xl shadow-lg">

      <h2 className="text-xl font-semibold mb-4">Accounts</h2>

      {safeAccounts.length === 0 && (
        <p className="text-gray-500">No accounts found.</p>
      )}

      {safeAccounts.map((acc) => (
        <div key={acc.account_id} className="mb-3">

          <p className="font-medium">
            {acc.account_type} ({acc.currency})
          </p>

          <p className="text-gray-400">
            Balance: ${acc.balance}
          </p>

        </div>
      ))}

    </div>
  );
}