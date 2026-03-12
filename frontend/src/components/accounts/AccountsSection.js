import { useNavigate } from "react-router-dom";
import { formatCurrency } from "../../utils/currencyUtils";
import EmptyState from "../common/EmptyState";

export default function AccountsSection({ accounts = [] }) {

  const navigate = useNavigate();

  if (!accounts.length) {
    return (
      <EmptyState message="No accounts found." />
    );
  }

  return (

    <div>

      <h2 className="text-xl font-semibold mb-6">
        Accounts
      </h2>

      <div className="grid grid-cols-3 gap-6">

        {accounts.map(acc => (

          <div
            key={acc.account_id}
            onClick={() =>
              navigate(`/accounts/${acc.account_id}`)
            }
            className="bg-gray-900 border border-gray-800 rounded-xl p-6 cursor-pointer hover:border-blue-500 transition"
          >

            <p className="text-gray-400 text-sm">
              {acc.account_type}
            </p>

            <p className="text-2xl font-semibold mt-2">
              {formatCurrency(acc.balance)}
            </p>

            <p className="text-xs text-gray-500 mt-2">
              Currency: {acc.currency}
            </p>

          </div>

        ))}

      </div>

    </div>

  );
}