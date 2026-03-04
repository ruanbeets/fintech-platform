const BASE_URL =
  process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

export async function getUsers() {
  const res = await fetch(`${BASE_URL}/users`);
  return res.json();
}

export async function getAccounts(userId) {
  const res = await fetch(`${BASE_URL}/accounts?user_id=${userId}`);
  return res.json();
}

export async function getTransactions(userId) {
  const res = await fetch(`${BASE_URL}/transactions?user_id=${userId}`);
  return res.json();
}

export async function getSummary(userId) {
  const res = await fetch(`${BASE_URL}/transactions/summary?user_id=${userId}`);
  return res.json();
}

export async function getCategorySummary(userId) {
  const res = await fetch(`${BASE_URL}/transactions/category-summary?user_id=${userId}`);
  return res.json();
}

export async function createTransaction(payload) {
  await fetch(`${BASE_URL}/transactions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export async function deleteTransaction(id) {
  await fetch(`${BASE_URL}/transactions/${id}`, {
    method: "DELETE"
  });
}