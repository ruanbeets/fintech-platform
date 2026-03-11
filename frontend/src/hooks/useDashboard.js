import { useEffect, useState } from "react";

import {
  getUsers,
  getAccounts,
  getTransactions,
  getSummary,
  getCategorySummary,
  createTransaction,
  deleteTransaction
} from "../services/api";

export default function useDashboard() {

  // ==========================
  // STATE
  // ==========================

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
  const [date, setDate] = useState("");

  // ==========================
  // FETCH USERS
  // ==========================

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await getUsers();
        setUsers(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error(err);
      }
    };

    fetchUsers();
  }, []);


  // ==========================
  // FETCH ALL USER DATA
  // ==========================

  const fetchUserData = async (userId) => {
    try {
      const [
        accountsData,
        transactionsData,
        summaryData,
        categoryData
      ] = await Promise.all([
        getAccounts(userId),
        getTransactions(userId),
        getSummary(userId),
        getCategorySummary(userId)
      ]);

      setAccounts(accountsData || []);
      setTransactions(transactionsData || []);
      setSummary(summaryData);
      setCategorySummary(categoryData);

    } catch (err) {
      console.error(err);
    }
  };


  // ==========================
  // USER CHANGE
  // ==========================

  useEffect(() => {
    if (!selectedUser) return;
    fetchUserData(selectedUser);
  }, [selectedUser]);


  // ==========================
  // CREATE TRANSACTION
  // ==========================

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {

      await createTransaction({
        user_id: selectedUser,
        account_id: selectedAccount,
        amount: parseFloat(amount),
        category,
        description,
        date
      });

      setAmount("");
      setCategory("");
      setDescription("");

      await fetchUserData(selectedUser);

    } catch (err) {
      console.error(err);
    }
  };


  // ==========================
  // DELETE TRANSACTION
  // ==========================

  const handleDelete = async (transactionId) => {
    try {

      await deleteTransaction(transactionId);

      await fetchUserData(selectedUser);

    } catch (err) {
      console.error(err);
    }
  };


  // ==========================
  // EXPORT CONTROLLER STATE
  // ==========================

  return {
    users,
    selectedUser,
    setSelectedUser,

    accounts,
    transactions,
    summary,
    categorySummary,

    amount,
    setAmount,
    category,
    setCategory,
    description,
    setDescription,
    selectedAccount,
    setSelectedAccount,
    date,
    setDate,

    handleSubmit,
    handleDelete
  };
}