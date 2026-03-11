import React, { useState, useEffect } from "react";

import Sidebar from "./components/Sidebar";
import UserSelector from "./components/UserSelector";
import SummaryCard from "./components/SummaryCard";
import ChartsSection from "./components/ChartsSection";
import AccountsSection from "./components/AccountsSection";
import TransactionForm from "./components/TransactionForm";
import TransactionList from "./components/TransactionList";
import LoginPage from "./pages/LoginPage";

import useDashboard from "./hooks/useDashboard";

import {
  buildSummaryChart,
  buildCategoryChart
} from "./utils/chartUtils";

function App() {

  const logout = () => {
    localStorage.clear();
    window.location.reload();
  };

  const [user, setUser] = useState(null);

  const dashboard = useDashboard();

  useEffect(() => {

    const savedUser = localStorage.getItem("user_id");
    const email = localStorage.getItem("user_email");

    if (savedUser) {
      setUser({
        user_id: savedUser,
        email: email
      });

      dashboard.setSelectedUser(savedUser);
    }

  }, []);

  if (!user) {
    return <LoginPage setUser={setUser} />;
  }

  const chartData = buildSummaryChart(dashboard.summary);

  const categoryChartData = buildCategoryChart(
    dashboard.categorySummary
  );

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">

      <Sidebar />

      <div className="flex-1 p-10 overflow-y-auto">

        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">
            Fintech Dashboard
          </h1>

          <button
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
          >
            Logout
          </button>
        </div>

        <div className="text-sm mb-6 text-gray-400">
          Logged in as: {user.email}
        </div>

        {dashboard.selectedUser && (
          <div className="space-y-10">

            <SummaryCard summary={dashboard.summary} />

            <ChartsSection
              transactions={dashboard.transactions}
              chartData={chartData}
              categoryChartData={categoryChartData}
            />

            <AccountsSection accounts={dashboard.accounts} />

            <TransactionForm {...dashboard} />

            <TransactionList
              transactions={dashboard.transactions}
              handleDelete={dashboard.handleDelete}
            />

          </div>
        )}

      </div>
    </div>
  );
}

export default App;