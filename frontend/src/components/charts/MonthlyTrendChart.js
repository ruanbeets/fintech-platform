import { Bar } from "react-chartjs-2";
import { baseChartOptions } from "../../constants/chartConfig";

export default function MonthlyTrendChart({ data }) {

  if (!data || !data.labels) return null;

  return (

    <div className="bg-fintech-card border border-fintech-border rounded-xl p-6">

      <h3 className="text-lg font-semibold mb-4">
        Monthly Income vs Expenses
      </h3>

      <div className="h-80">

        <Bar
          data={data}
          options={baseChartOptions}
          redraw={true}
        />

      </div>

    </div>

  );

}