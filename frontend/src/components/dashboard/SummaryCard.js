import MetricCard from "./MetricCard";
import { formatCurrency } from "../../utils/currencyUtils";

export default function SummaryCard({ summary }) {

  if (!summary) return null;

  const netCashFlow =
    summary.total_income +
    summary.total_expenses;

  return (

    <div className="grid grid-cols-3 gap-6 mb-8">

      <MetricCard
        title="Total Income"
        value={formatCurrency(summary.total_income)}
        color="text-green-400"
      />

      <MetricCard
        title="Total Expenses"
        value={formatCurrency(summary.total_expenses)}
        color="text-red-400"
      />

      <MetricCard
        title="Net Cash Flow"
        value={formatCurrency(netCashFlow)}
        color="text-blue-400"
      />

    </div>

  );
}