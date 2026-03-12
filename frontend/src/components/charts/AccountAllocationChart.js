import { Doughnut } from "react-chartjs-2";
import { doughnutOptions } from "../../constants/chartConfig";
import { buildAccountAllocation } from "../../utils/chartUtils";

export default function AccountAllocationChart({ accounts }) {

  if (!accounts || accounts.length === 0) return null;

  const data = buildAccountAllocation(accounts);

  return (

    <div className="bg-fintech-card border border-fintech-border rounded-xl p-6">

      <h3 className="text-lg font-semibold mb-4">
        Account Allocation
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