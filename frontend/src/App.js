import React from "react";

import Sidebar from "./components/Sidebar";
import UserSelector from "./components/UserSelector";
import SummaryCard from "./components/SummaryCard";
import ChartsSection from "./components/ChartsSection";
import AccountsSection from "./components/AccountsSection";
import TransactionForm from "./components/TransactionForm";
import TransactionList from "./components/TransactionList";

import useDashboard from "./hooks/useDashboard";

import {
  buildSummaryChart,
  buildCategoryChart
} from "./utils/chartUtils";

function App() {
  const dashboard = useDashboard();

  const chartData = buildSummaryChart(dashboard.summary);
  const categoryChartData = buildCategoryChart(
    dashboard.categorySummary
  );

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">
      <Sidebar />

      <div className="flex-1 p-10 overflow-y-auto">
        <h1 className="text-4xl font-bold mb-8">
          Fintech Dashboard
        </h1>

        <UserSelector
          users={dashboard.users}
          setSelectedUser={dashboard.setSelectedUser}
        />

        {dashboard.selectedUser && (
          <div className="space-y-10">
            <SummaryCard summary={dashboard.summary} />

            <ChartsSection
              transactions={dashboard.transactions}
              chartData={chartData}
              categoryChartData={categoryChartData}
            />

            <AccountsSection accounts={dashboard.accounts} />

            <TransactionForm
              {...dashboard}
            />

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