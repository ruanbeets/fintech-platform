import { Doughnut } from "react-chartjs-2";
import { doughnutOptions } from "../../constants/chartConfig";

export default function CategoryChart({ data }) {

  if (!data || !data.labels) return null;

  return (

    <div className="bg-fintech-card border border-fintech-border rounded-xl p-6">

      <h3 className="text-lg font-semibold mb-4">
        Category Breakdown
      </h3>

      <div className="h-72">

        <Doughnut
          data={data}
          options={doughnutOptions}
          redraw={true}
        />

      </div>

    </div>

  );

}