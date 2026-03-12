import MetricCard from "./MetricCard";
import { formatCurrency } from "../../utils/currencyUtils";

export default function NetWorthCard({ accounts = [] }) {

  const netWorth = accounts.reduce(
    (sum, acc) => sum + Number(acc.balance || 0),
    0
  );

  return (

    <MetricCard
      title="Net Worth"
      value={formatCurrency(netWorth)}
      subtitle={`Across ${accounts.length} accounts`}
      color="text-green-400"
    />

  );
}