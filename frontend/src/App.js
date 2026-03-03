import React, { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from "chart.js";

import { Bar } from "react-chartjs-2";

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

  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [selectedAccount, setSelectedAccount] = useState("");
  const [summary, setSummary] = useState(null);
  const [categorySummary, setCategorySummary] = useState(null);

  // Fetch users
  useEffect(() => {
    fetch("http://127.0.0.1:9000/users")
      .then(res => res.json())
      .then(data => setUsers(data))
      .catch(err => console.error(err));
  }, []);

  // Fetch accounts + transactions when user changes
  useEffect(() => {
  if (!selectedUser) return;

  // Fetch accounts
  fetch(`http://127.0.0.1:9000/accounts?user_id=${selectedUser}`)
    .then(res => res.json())
    .then(data => setAccounts(data))
    .catch(err => console.error(err));

  // Fetch transactions
  fetch(`http://127.0.0.1:9000/transactions?user_id=${selectedUser}`)
    .then(res => res.json())
    .then(data => setTransactions(data))
    .catch(err => console.error(err));

  // Fetch summary
  fetch(`http://127.0.0.1:9000/transactions/summary?user_id=${selectedUser}`)
    .then(res => res.json())
    .then(data => setSummary(data))
    .catch(err => console.error(err));

  // Fetch category summary 
  fetch(`http://127.0.0.1:9000/transactions/category-summary?user_id=${selectedUser}`)
    .then(res => res.json())
    .then(data => setCategorySummary(data))
    .catch(err => console.error(err));

}, [selectedUser]);

 const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    await fetch("http://127.0.0.1:9000/transactions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: selectedUser,
        account_id: selectedAccount,
        amount: parseFloat(amount),
        category: category,
        description: description,
        date: new Date().toISOString().split("T")[0],
      }),
    });

    // Re-fetch transactions
    const txRes = await fetch(
      `http://127.0.0.1:9000/transactions?user_id=${selectedUser}`
    );
    const txData = await txRes.json();
    setTransactions(txData);

    // Re-fetch summary
    const summaryRes = await fetch(
      `http://127.0.0.1:9000/transactions/summary?user_id=${selectedUser}`
    );
    const summaryData = await summaryRes.json();
    setSummary(summaryData);

    setAmount("");
    setCategory("");
    setDescription("");

    const categoryRes = await fetch(
      `http://127.0.0.1:9000/transactions/category-summary?user_id=${selectedUser}`
    );
    const categoryData = await categoryRes.json();
    setCategorySummary(categoryData);

  } catch (err) {
    console.error(err);
  }
};

 const handleDelete = async (transactionId) => {
  try {
    await fetch(
      `http://127.0.0.1:9000/transactions/${transactionId}`,
      { method: "DELETE" }
    );

    // Re-fetch transactions
    const txRes = await fetch(
      `http://127.0.0.1:9000/transactions?user_id=${selectedUser}`
    );
    const txData = await txRes.json();
    setTransactions(txData);

    // Re-fetch summary
    const summaryRes = await fetch(
      `http://127.0.0.1:9000/transactions/summary?user_id=${selectedUser}`
    );
    const summaryData = await summaryRes.json();
    setSummary(summaryData);


    const categoryRes = await fetch(
    `http://127.0.0.1:9000/transactions/category-summary?user_id=${selectedUser}`
    );
    const categoryData = await categoryRes.json();
    setCategorySummary(categoryData);
  } catch (err) {
    console.error(err);
  }
};

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
          backgroundColor: ["#4caf50", "#f44336"],
        },
      ],
    }
  : null;

const categoryChartData = categorySummary
  ? {
      labels: Object.keys(categorySummary),
      datasets: [
        {
          label: "Total by Category",
          data: Object.values(categorySummary).map(v => Math.abs(v)),
          backgroundColor: "#2196f3",
        },
      ],
    }
  : null;

const chartOptions = {
  plugins: {
    legend: {
      labels: {
        color: "#9CA3AF" // gray-400
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

return (
  <div className="min-h-screen bg-gray-950 text-gray-100 flex">

    {/* Sidebar */}
    <div className="w-64 bg-gray-900 border-r border-gray-800 p-6">
      <h2 className="text-xl font-bold mb-8">Fintech</h2>

      <nav className="space-y-4 text-gray-400">
        <div className="hover:text-white cursor-pointer">Dashboard</div>
        <div className="hover:text-white cursor-pointer">Accounts</div>
        <div className="hover:text-white cursor-pointer">Analytics</div>
        <div className="hover:text-white cursor-pointer">Settings</div>
      </nav>
    </div>

    {/* Main Content */}
    <div className="flex-1 p-10 overflow-y-auto">

      <h1 className="text-4xl font-bold mb-8">
        Fintech Dashboard
      </h1>

      <div className="mb-8">
        <label className="block text-sm text-gray-400 mb-2">
          Select User
        </label>
        <select
          onChange={(e) => setSelectedUser(e.target.value)}
          className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg w-64"
        >
          <option value="">-- Choose User --</option>
          {users.map(user => (
            <option key={user.user_id} value={user.user_id}>
              {user.email}
            </option>
          ))}
        </select>
      </div>

      {selectedUser && (
        <div className="space-y-10">

          {/* Financial Summary */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 backdrop-blur
           p-6 rounded-2xl shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Financial Summary</h2>
            <div className="space-y-2">
              <p>Total Income: <span className="text-green-400 font-medium">${summary?.total_income}</span></p>
              <p>Total Expenses: <span className="text-red-400 font-medium">${summary?.total_expenses}</span></p>
              <p>Net Cashflow: <span className="text-blue-400 font-medium">${summary?.net_cashflow}</span></p>
            </div>
          </div>

          {/* Charts */}
          <div className="grid md:grid-cols-2 gap-8">
            {chartData && (
              <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 backdrop-blur
               p-6 rounded-2xl shadow-lg">
                <h3 className="mb-4">Cash Flow</h3>
               <Bar data={chartData} options={chartOptions} />
              </div>
            )}

            {categoryChartData && (
              <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 backdrop-blur
               p-6 rounded-2xl shadow-lg">
                <h3 className="mb-4">Category Breakdown</h3>
                <Bar data={categoryChartData} options={chartOptions} />
              </div>
            )}
          </div>

          {/* Accounts */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 backdrop-blur
           p-6 rounded-2xl shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Accounts</h2>
            {accounts.map(acc => (
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

          {/* Create Transaction */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 backdrop-blur
           p-6 rounded-2xl shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Create Transaction</h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <select
                required
                value={selectedAccount}
                onChange={(e) => setSelectedAccount(e.target.value)}
                className="bg-gray-800 border border-gray-700 px-4 py-2 rounded-lg w-full"
              >
                <option value="">-- Select Account --</option>
                {accounts.map(acc => (
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

              <input
                type="text"
                placeholder="Category"
                required
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

          {/* Transactions */}
          <div className="bg-gradient-to-br from-gray-900 to-gray-950 border border-gray-800/60 backdrop-blur
           p-6 rounded-2xl shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Transactions</h2>

            {transactions.map(tx => (
              <div key={tx.transaction_id} className="mb-4 border-b border-gray-800 pb-4">
                <p>
                  <strong>{tx.category}</strong> — ${tx.amount}
                </p>
                <p className="text-gray-400">{tx.description}</p>

                <button
                  onClick={() => handleDelete(tx.transaction_id)}
                  className="mt-2 text-red-400 hover:text-red-300 text-sm"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>

        </div>
      )}
    </div>
  </div>
);
}

export default App;