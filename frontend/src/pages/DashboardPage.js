import { useEffect, useState } from "react";

import SummaryCard from "../components/SummaryCard";
import ChartsSection from "../components/ChartsSection";

import {
  getSummary,
  getCategorySummary,
  getTransactions
} from "../services/api";

import {
  buildSummaryChart,
  buildCategoryChart
} from "../utils/chartUtils";

export default function DashboardPage() {

  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [categorySummary, setCategorySummary] = useState([]);

  useEffect(() => {

    const fetchData = async () => {

      const userId = localStorage.getItem("user_id");

      if (!userId) return;

      const summaryData = await getSummary(userId);
      const categoryData = await getCategorySummary(userId);
      const transactionData = await getTransactions(userId);

      setSummary(summaryData);
      setCategorySummary(categoryData);
      setTransactions(transactionData);
    };

    fetchData();

  }, []);

  const chartData = buildSummaryChart(summary);
  const categoryChartData = buildCategoryChart(categorySummary);

  return (
    <div>

      <h1 className="text-4xl font-bold mb-2">
        Dashboard
      </h1>

      <p className="text-gray-400 mb-8">
        Financial overview across all accounts
      </p>

      {summary && (
        <SummaryCard summary={summary} />
      )}

      <ChartsSection
        transactions={transactions}
        chartData={chartData}
        categoryChartData={categoryChartData}
      />

    </div>
  );
}