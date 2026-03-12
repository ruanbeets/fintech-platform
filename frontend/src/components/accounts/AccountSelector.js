import { useNavigate, useParams } from "react-router-dom";
import { formatCurrency } from "../../utils/currencyUtils";

export default function AccountSelector({ accounts = [] }) {

  const navigate = useNavigate();
  const { id } = useParams();

  if (!accounts.length) {
    return (
      <p className="text-gray-500">
        No accounts available.
      </p>
    );
  }

  return (

    <div className="flex flex-wrap gap-4 mb-8">

      {accounts.map(acc => {

        const isActive = id === acc.account_id;

        return (

          <button
            key={acc.account_id}
            onClick={() =>
              navigate(`/accounts/${acc.account_id}`)
            }
            className={`p-4 rounded-xl border transition
              ${
                isActive
                  ? "border-blue-500 bg-gray-900"
                  : "border-gray-800 bg-gray-900 hover:border-gray-600"
              }`}
          >

            <div className="text-left">

              <p className="text-sm text-gray-400">
                {acc.account_type}
              </p>

              <p className="text-lg font-semibold">
                {formatCurrency(acc.balance)}
              </p>

            </div>

          </button>

        );

      })}

    </div>

  );
}