import React, { useEffect, useState } from "react";

function App() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState("");
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);

  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [selectedAccount, setSelectedAccount] = useState("");

  // ===== Financial Summary Calculations =====
  const totalIncome = transactions
    .filter(tx => tx.amount > 0)
    .reduce((sum, tx) => sum + tx.amount, 0);

  const totalExpenses = transactions
    .filter(tx => tx.amount < 0)
    .reduce((sum, tx) => sum + tx.amount, 0);

  const netCashflow = totalIncome + totalExpenses;

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

    fetch(`http://127.0.0.1:9000/accounts?user_id=${selectedUser}`)
      .then(res => res.json())
      .then(data => setAccounts(data))
      .catch(err => console.error(err));

    fetch(`http://127.0.0.1:9000/transactions?user_id=${selectedUser}`)
      .then(res => res.json())
      .then(data => setTransactions(data))
      .catch(err => console.error(err));
  }, [selectedUser]);

  const handleSubmit = (e) => {
    e.preventDefault();

    fetch("http://127.0.0.1:9000/transactions", {
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
    })
      .then(res => res.json())
      .then(newTx => {
        setTransactions([...transactions, newTx]);
        setAmount("");
        setCategory("");
        setDescription("");
      })
      .catch(err => console.error(err));
  };

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
          <p><strong>Total Income:</strong> ${totalIncome}</p>
          <p><strong>Total Expenses:</strong> ${totalExpenses}</p>
          <p><strong>Net Cashflow:</strong> ${netCashflow}</p>
        </div>
        
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
            </div>
          ))}
        </>
      )}
    </div>
  );
}

export default App;