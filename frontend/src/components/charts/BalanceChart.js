import { Line } from "react-chartjs-2";
import { baseChartOptions } from "../../constants/chartConfig";

export default function BalanceChart({ data }) {

  if (!data || !data.labels) return null;

  return (

    <div className="h-96 bg-fintech-card border border-fintech-border rounded-xl p-6">

      <h3 className="text-lg font-semibold mb-4">
        Balance Over Time
      </h3>

      <Line
        data={data}
        options={baseChartOptions}
        redraw={true}
      />

    </div>

  );

}