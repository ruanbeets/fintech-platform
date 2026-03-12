import MetricCard from "./MetricCard";

export default function AccountHealthIndicator({
  transactions = []
}) {

  const income = transactions
    .filter(tx => tx.amount > 0)
    .reduce((sum, tx) => sum + tx.amount, 0);

  const expenses = transactions
    .filter(tx => tx.amount < 0)
    .reduce((sum, tx) => sum + Math.abs(tx.amount), 0);

  const ratio = income
    ? ((income - expenses) / income) * 100
    : 0;

  let status = "Poor";
  let color = "text-red-400";

  if (ratio > 40) {
    status = "Excellent";
    color = "text-green-400";
  }
  else if (ratio > 20) {
    status = "Healthy";
    color = "text-blue-400";
  }

  return (

    <MetricCard
      title="Financial Health"
      value={`${ratio.toFixed(1)}%`}
      subtitle={status}
      color={color}
    />

  );
}