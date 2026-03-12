import { formatCurrency } from "../../utils/currencyUtils";

export default function TransactionRow({
  transaction,
  onDelete
}) {

  return (

    <tr className="border-t border-gray-800">

      <td className="py-2">
        {transaction.date}
      </td>

      <td>
        {transaction.description}
      </td>

      <td>
        {transaction.category}
      </td>

      <td
        className={`text-right ${
          transaction.amount >= 0
            ? "text-green-400"
            : "text-red-400"
        }`}
      >
        {formatCurrency(transaction.amount)}
      </td>

      {onDelete && (

        <td className="text-right">

          <button
            onClick={() =>
              onDelete(transaction.transaction_id)
            }
            className="text-red-400 hover:text-red-300"
          >
            Delete
          </button>

        </td>

      )}

    </tr>

  );

}