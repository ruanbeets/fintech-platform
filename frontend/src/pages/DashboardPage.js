import TopBar from "../components/layout/TopBar";

import PageHeader from "../components/common/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";

import DashboardGrid from "../components/dashboard/DashboardGrid";
import NetWorthCard from "../components/dashboard/NetWorthCard";
import AccountHealthIndicator from "../components/dashboard/AccountHealthIndicator";
import BudgetProgressBar from "../components/dashboard/BudgetProgressBar";
import SummaryCard from "../components/dashboard/SummaryCard";
import ChartsSection from "../components/dashboard/ChartsSection";
import RecentTransactionsCard from "../components/dashboard/RecentTransactionsCard";

import useDashboard from "../hooks/useDashboard";

import {
  buildBalanceChart,
  buildCategoryChart
} from "../utils/chartUtils";

export default function DashboardPage() {

  const {
    accounts,
    transactions,
    summary,
    categorySummary,
    loading
  } = useDashboard();

  if (loading) return <LoadingSpinner />;

  const balanceChart = buildBalanceChart(transactions);
  const categoryChart = buildCategoryChart(categorySummary);

  return (

    <div>

      <TopBar />

      <PageHeader
        title="Dashboard"
        subtitle="Financial overview across all accounts"
      />

      <DashboardGrid>

        <NetWorthCard accounts={accounts} />

        <AccountHealthIndicator
          transactions={transactions}
        />

        <BudgetProgressBar
          transactions={transactions}
        />

      </DashboardGrid>

      <SummaryCard summary={summary} />

      <ChartsSection
        balanceChart={balanceChart}
        categoryChart={categoryChart}
      />

      <div className="mt-10">

        <RecentTransactionsCard
          transactions={transactions}
        />

      </div>

    </div>

  );

}