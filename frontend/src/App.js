import React, { useEffect, useState } from "react";

function App() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [transactions, setTransactions] = useState([]);

  // Fetch users on load
  useEffect(() => {
    fetch("http://127.0.0.1:9000/users")
      .then(res => res.json())
      .then(data => setUsers(data))
      .catch(err => console.error(err));
  }, []);

  // Fetch transactions when user changes
  useEffect(() => {
    if (!selectedUser) return;

    fetch(`http://127.0.0.1:9000/transactions?user_id=${selectedUser}`)
      .then(res => res.json())
      .then(data => setTransactions(data))
      .catch(err => console.error(err));
  }, [selectedUser]);

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

      <h2 style={{ marginTop: "30px" }}>Transactions</h2>

      {transactions.map(tx => (
        <div key={tx.transaction_id} style={{ marginBottom: "10px" }}>
          <strong>{tx.category}</strong> — ${tx.amount}
          <div>{tx.description}</div>
        </div>
      ))}
    </div>
  );
}

export default App;