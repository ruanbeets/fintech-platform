// src/hooks/useDashboard.js

import { useEffect, useState } from "react";

import {
  getAccounts,
  getTransactions,
  getSummary,
  getCategorySummary
} from "../services/api";

export default function useDashboard() {

  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [categorySummary, setCategorySummary] = useState([]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {

    const fetchDashboardData = async () => {

      try {

        const userId = localStorage.getItem("user_id");

        if (!userId) return;

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
        setSummary(summaryData || null);
        setCategorySummary(categoryData || []);

      } catch (error) {

        console.error("Dashboard load error:", error);

      } finally {

        setLoading(false);

      }

    };

    fetchDashboardData();

  }, []);

  return {

    accounts,
    transactions,
    summary,
    categorySummary,
    loading

  };

}