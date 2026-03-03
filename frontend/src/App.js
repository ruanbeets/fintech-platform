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

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Fintech Dashboard</h1>

      <h2>Select User</h2>
      <select onChange={(e) => setSelectedUser(e.target.value)}>
        <option value="">-- Choose User --</option>
        {users.map(user => (
          <option key={user.user_id} value={user.user_id}>
            {user.email}
          </option>
        ))}
      </select>

      {selectedUser && (
        <>
        <div style={{
          marginTop: "30px",
          padding: "20px",
          backgroundColor: "#f2f2f2",
          borderRadius: "8px",
          maxWidth: "400px"
        }}>
          <h2>Financial Summary</h2>
          <p><strong>Total Income:</strong> ${summary?.total_income}</p>
          <p><strong>Total Expenses:</strong> ${summary?.total_expenses}</p>
          <p><strong>Net Cashflow:</strong> ${summary?.net_cashflow}</p>
        </div>

        {chartData && (
          <div style={{ maxWidth: "500px", marginTop: "20px" }}>
            <Bar data={chartData} />
          </div>
        )}

        {categoryChartData && (
          <div style={{ maxWidth: "500px", marginTop: "40px" }}>
            <h3>Category Breakdown</h3>
            <Bar data={categoryChartData} />
          </div>
        )}
        
        <h2 style={{ marginTop: "30px" }}>Accounts</h2>
        {accounts.map(acc => (
          <div
            key={acc.account_id}
            style={{
              padding: "10px",
              backgroundColor: "#1f1f1f",
              borderRadius: "6px",
              marginBottom: "10px",
              maxWidth: "400px"
            }}
          >
            <strong>{acc.account_type}</strong> ({acc.currency})
            <div>Balance: ${acc.balance}</div>
          </div>
        ))}

          <h2 style={{ marginTop: "30px" }}>Create Transaction</h2>

          <form onSubmit={handleSubmit}>
            <div>
              <select
                required
                value={selectedAccount}
                onChange={(e) => setSelectedAccount(e.target.value)}
              >
                <option value="">-- Select Account --</option>
                {accounts.map(acc => (
                  <option key={acc.account_id} value={acc.account_id}>
                    {acc.account_type} ({acc.currency})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <input
                type="number"
                placeholder="Amount"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>

            <div>
              <input
                type="text"
                placeholder="Category"
                required
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </div>

            <div>
              <input
                type="text"
                placeholder="Description"
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <button type="submit">Add Transaction</button>
          </form>

          <h2 style={{ marginTop: "30px" }}>Transactions</h2>

          {transactions.map(tx => (
            <div key={tx.transaction_id} style={{ marginBottom: "10px" }}>
              <strong>{tx.category}</strong> — ${tx.amount}
              <div>{tx.description}</div>

              <button
                style={{ marginTop: "5px" }}
                onClick={() => handleDelete(tx.transaction_id)}
              >
                Delete
              </button>
            </div>
          ))}
        </>
      )}
    </div>
  );
}

export default App;