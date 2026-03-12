import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import TopBar from "../components/layout/TopBar";

import PageHeader from "../components/common/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";

import AccountSelector from "../components/accounts/AccountSelector";

import BalanceChart from "../components/charts/BalanceChart";

import TransactionForm from "../components/transactions/TransactionForm";
import TransactionFilters from "../components/transactions/TransactionFilters";
import TransactionList from "../components/transactions/TransactionList";

import {
  getAccounts,
  getTransactions,
  createTransaction,
  deleteTransaction
} from "../services/api";

import { buildBalanceChart } from "../utils/chartUtils";

export default function AccountDetailPage() {

  const { id } = useParams();

  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [filtered, setFiltered] = useState([]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {

    const fetchData = async () => {

      const userId = localStorage.getItem("user_id");

      const accountsData = await getAccounts(userId);

      const transactionsData = await getTransactions(userId);

      const accountTransactions =
        transactionsData.filter(
          tx => tx.account_id === id
        );

      setAccounts(accountsData || []);
      setTransactions(accountTransactions);
      setFiltered(accountTransactions);

      setLoading(false);

    };

    fetchData();

  }, [id]);

  if (loading) return <LoadingSpinner />;

  const chartData = buildBalanceChart(transactions);

  const handleCreate = async (tx) => {

    await createTransaction(tx);

    setTransactions(prev => [tx, ...prev]);
    setFiltered(prev => [tx, ...prev]);

  };

  const handleDelete = async (txId) => {

    await deleteTransaction(txId);

    const updated = transactions.filter(
      t => t.transaction_id !== txId
    );

    setTransactions(updated);
    setFiltered(updated);

  };

  const handleSearch = (value) => {

    const results = transactions.filter(tx =>
      tx.description?.toLowerCase()
        .includes(value.toLowerCase())
    );

    setFiltered(results);

  };

  return (

    <div>

      <TopBar />

      <PageHeader
        title="Account Details"
        subtitle="View activity and analytics"
      />

      <AccountSelector accounts={accounts} />

      <div className="mt-6">

        <BalanceChart data={chartData} />

      </div>

      <div className="mt-8">

        <TransactionForm
          accounts={accounts}
          onCreate={handleCreate}
        />

      </div>

      <div className="mt-8">

        <TransactionFilters
          onSearch={handleSearch}
        />

        <TransactionList
          transactions={filtered}
          onDelete={handleDelete}
        />

      </div>

    </div>

  );

}