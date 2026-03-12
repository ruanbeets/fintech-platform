import BalanceChart from "../charts/BalanceChart";
import CashFlowChart from "../charts/CashFlowChart";
import CategoryChart from "../charts/CategoryChart";
import MonthlyTrendChart from "../charts/MonthlyTrendChart";
import AccountAllocationChart from "../charts/AccountAllocationChart";

export default function ChartsSection({
  summary,
  chartData,
  categoryChartData,
  transactions,
  accounts
}) {

  return (

    <div className="space-y-8">

      <BalanceChart data={chartData} />

      <div className="grid grid-cols-2 gap-6">

        <CashFlowChart summary={summary} />

        <CategoryChart data={categoryChartData} />

      </div>

      <MonthlyTrendChart
        transactions={transactions}
      />

      <AccountAllocationChart
        accounts={accounts}
      />

    </div>

  );
}