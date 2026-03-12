import TransactionRow from "./TransactionRow";
import TransactionTableHeader from "./TransactionTableHeader";
import EmptyState from "../common/EmptyState";

export default function TransactionList({
  transactions = [],
  onDelete
}) {

  if (!transactions.length) {

    return (

      <EmptyState
        title="No Transactions"
        message="Add your first transaction to begin tracking finances."
      />

    );

  }

  return (

    <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl">

      <h2 className="text-xl font-semibold mb-4">
        Transactions
      </h2>

      <table className="w-full text-sm">

        <TransactionTableHeader />

        <tbody>

          {transactions.map(tx => (

            <TransactionRow
              key={tx.transaction_id}
              transaction={tx}
              onDelete={onDelete}
            />

          ))}

        </tbody>

      </table>

    </div>

  );

}