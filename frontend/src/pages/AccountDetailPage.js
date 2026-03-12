import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";

import TransactionList from "../components/TransactionList";
import TransactionForm from "../components/TransactionForm";

import {
  getTransactions,
  deleteTransaction
} from "../services/api";

export default function AccountDetailPage() {

  const { id } = useParams();

  const [transactions, setTransactions] = useState([]);

  useEffect(() => {

    const fetchTransactions = async () => {

      const userId = localStorage.getItem("user_id");

      const data = await getTransactions(userId);

      const accountTx = data.filter(
        t => t.account_id === id
      );

      setTransactions(accountTx);

    };

    fetchTransactions();

  }, [id]);

  const handleDelete = async (txId) => {

    await deleteTransaction(txId);

    setTransactions(
      transactions.filter(t => t.transaction_id !== txId)
    );
  };

  return (
    <div>

      <h1 className="text-4xl font-bold mb-8">
        Account Details
      </h1>

      <TransactionForm accountId={id} />

      <TransactionList
        transactions={transactions}
        handleDelete={handleDelete}
      />

    </div>
  );
}