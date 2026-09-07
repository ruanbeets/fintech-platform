import { useId } from "react";

export default function TrendSeriesChart({ title, series, formatValue }) {
  const id = useId();
  // Geometry only: financial values and missing-data decisions come from the API.
  const width = 780, height = 180, left = 56, top = 15, bottom = 30;
  const values = series.filter((p) => p.value !== null).map((p) => Number(p.value));
  const min = Math.min(0, ...values), max = Math.max(1, ...values);
  const x = (i) => left + i * (width - left - 20) / Math.max(1, series.length - 1);
  const y = (value) => top + (max - Number(value)) / (max - min) * (height - top - bottom);
  return <>
    <div className="ft-chart ft-trend-chart"><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby={id}>
      <title id={id}>{title}. Exact values and coverage in the table below. Unavailable values leave gaps.</title>
      {[min, max].map((value) => <g key={value}><line x1={left} x2={width - 20} y1={y(value)} y2={y(value)} className="ft-gridline" /><text x={left - 7} y={y(value) + 4} textAnchor="end" className="ft-axis">{new Intl.NumberFormat("en-ZA", { notation: "compact", maximumFractionDigits: 1 }).format(value)}</text></g>)}
      {series.map((p, i) => <g key={p.month}>
        {p.value !== null && <>
          {i > 0 && series[i - 1].value !== null && <line x1={x(i - 1)} y1={y(series[i - 1].value)} x2={x(i)} y2={y(p.value)} className="ft-net-line" />}
          <circle cx={x(i)} cy={y(p.value)} r="4" className="ft-net-dot"><title>{p.month}: {formatValue(p.value)} · {p.coverage}</title></circle>
        </>}
        <text x={x(i)} y={height - 8} textAnchor="middle" className="ft-axis">{p.month.slice(2)}</text>
      </g>)}
    </svg></div>
    <details className="ft-table-details"><summary>{title} · exact values</summary><div className="ft-table-scroll"><table>
      <caption>{title}</caption><thead><tr><th>Month</th><th>Value</th><th>Coverage</th></tr></thead>
      <tbody>{series.map((p) => <tr key={p.month}><th scope="row">{p.month}</th><td>{formatValue(p.value)}</td><td>{p.coverage.replaceAll("_", " ")}{p.partial_month ? " · partial month" : ""}</td></tr>)}</tbody>
    </table></div></details>
  </>;
}
