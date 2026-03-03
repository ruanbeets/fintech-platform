import React, { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from "chart.js";

import {
  getUsers,
  getAccounts,
  getTransactions,
  getSummary,
  getCategorySummary,
  createTransaction,
  deleteTransaction
} from "./services/api";

import Sidebar from "./components/Sidebar";
import UserSelector from "./components/UserSelector";
import SummaryCard from "./components/SummaryCard";
import ChartsSection from "./components/ChartsSection";
import AccountsSection from "./components/AccountsSection";
import TransactionForm from "./components/TransactionForm";
import TransactionList from "./components/TransactionList";

ChartJS.register(
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

function App() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [categorySummary, setCategorySummary] = useState(null);

  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [selectedAccount, setSelectedAccount] = useState("");

  // =============================
// Fetch Users (once)
// =============================
useEffect(() => {
  const fetchUsersData = async () => {
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (err) {
      console.error(err);
    }
  };

  fetchUsersData();
}, []);


// =============================
// Fetch All User Data
// =============================
const fetchUserData = async (userId) => {
  try {
    const [accountsData, txData, summaryData, categoryData] =
      await Promise.all([
        getAccounts(userId),
        getTransactions(userId),
        getSummary(userId),
        getCategorySummary(userId)
      ]);

    setAccounts(accountsData);
    setTransactions(txData);
    setSummary(summaryData);
    setCategorySummary(categoryData);
  } catch (err) {
    console.error(err);
  }
};


// When selected user changes
useEffect(() => {
  if (!selectedUser) return;
  fetchUserData(selectedUser);
}, [selectedUser]);


// =============================
// Create Transaction
// =============================
const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    await createTransaction({
      user_id: selectedUser,
      account_id: selectedAccount,
      amount: parseFloat(amount),
      category,
      description,
      date: new Date().toISOString().split("T")[0]
    });

    setAmount("");
    setCategory("");
    setDescription("");

    await fetchUserData(selectedUser);

  } catch (err) {
    console.error(err);
  }
};


// =============================
// Delete Transaction
// =============================
const handleDelete = async (transactionId) => {
  try {
    await deleteTransaction(transactionId);
    await fetchUserData(selectedUser);
  } catch (err) {
    console.error(err);
  }
};

  // =============================
  // Chart Data
  // =============================
  const chartData = summary
    ? {
        labels: ["Income", "Expenses"],
        datasets: [
          {
            label: "Amount",
            data: [
              summary.total_income,
              Math.abs(summary.total_expenses)
            ],
            backgroundColor: ["#4caf50", "#f44336"]
          }
        ]
      }
    : null;

  const categoryChartData = categorySummary
    ? {
        labels: Object.keys(categorySummary),
        datasets: [
          {
            label: "Total by Category",
            data: Object.values(categorySummary).map((v) =>
              Math.abs(v)
            ),
            backgroundColor: "#2196f3"
          }
        ]
      }
    : null;

  const chartOptions = {
    plugins: {
      legend: {
        labels: {
          color: "#9CA3AF"
        }
      }
    },
    scales: {
      x: {
        ticks: { color: "#9CA3AF" },
        grid: { color: "rgba(255,255,255,0.05)" }
      },
      y: {
        ticks: { color: "#9CA3AF" },
        grid: { color: "rgba(255,255,255,0.05)" }
      }
    }
  };

  // =============================
  // Render
  // =============================
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">
      <Sidebar />

      <div className="flex-1 p-10 overflow-y-auto">
        <h1 className="text-4xl font-bold mb-8">
          Fintech Dashboard
        </h1>

        <UserSelector
          users={users}
          setSelectedUser={setSelectedUser}
        />

        {selectedUser && (
          <div className="space-y-10">
            <SummaryCard summary={summary} />

            <ChartsSection
              chartData={chartData}
              categoryChartData={categoryChartData}
              chartOptions={chartOptions}
            />

            <AccountsSection accounts={accounts} />

            <TransactionForm
              accounts={accounts}
              selectedAccount={selectedAccount}
              setSelectedAccount={setSelectedAccount}
              amount={amount}
              setAmount={setAmount}
              category={category}
              setCategory={setCategory}
              description={description}
              setDescription={setDescription}
              handleSubmit={handleSubmit}
            />

            <TransactionList
              transactions={transactions}
              handleDelete={handleDelete}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;