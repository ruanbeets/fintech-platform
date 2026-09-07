const monthLabel = (month) =>
  new Date(`${month}-01T12:00:00Z`).toLocaleDateString("en-ZA", { month: "short", timeZone: "UTC" });

export default function MonthlyHistoryChart({ history, formatMoney, currency }) {
  // Number conversion and scaling below are presentation only; all financial values come from the API.
  const width = 960, height = 260, left = 64, right = 20, top = 20, bottom = 34;
  const values = history.flatMap((m) => [Number(m.income), Number(m.expenses), Number(m.net_cash_flow)]);
  const maximum = Math.max(1, ...values);
  const minimum = Math.min(0, ...values);
  const y = (v) => top + ((maximum - v) / (maximum - minimum)) * (height - top - bottom);
  const step = (width - left - right) / history.length;
  const x = (i) => left + step * (i + 0.5);
  const points = history.map((m, i) => `${x(i)},${y(Number(m.net_cash_flow))}`).join(" ");
  return (
    <>
      <div className="ft-legend" aria-label="Chart legend">
        <span><i className="income" />Income</span><span><i className="expenses" />Expenses</span><span><i className="net" />Net cash flow</span>
      </div>
      <div className="ft-chart">
        <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby="history-title history-desc">
          <title id="history-title">12-month income, expense and net cash-flow history in {currency}</title>
          <desc id="history-desc">Income and expense bars with a net cash-flow line. Exact values and coverage are in the expandable table below.</desc>
          {[0, 0.5, 1].map((fraction) => {
            const value = minimum + (maximum - minimum) * fraction;
            return <g key={fraction}><line x1={left} x2={width - right} y1={y(value)} y2={y(value)} className="ft-gridline" />
              <text x={left - 10} y={y(value) + 4} textAnchor="end" className="ft-axis">{new Intl.NumberFormat("en-ZA", { notation: "compact", maximumFractionDigits: 1 }).format(value)}</text></g>;
          })}
          <line x1={left} x2={width - right} y1={y(0)} y2={y(0)} className="ft-gridline" />
          {history.map((m, i) => <g key={m.month}>
            <title>{m.month}: income {formatMoney(m.income)}, expenses {formatMoney(m.expenses)}, net {formatMoney(m.net_cash_flow)}; {m.coverage.replaceAll("_", " ")}</title>
            <rect x={x(i) - 17} y={y(Number(m.income))} width="14" height={y(0) - y(Number(m.income))} rx="3" className="ft-income-bar" />
            <rect x={x(i) + 3} y={y(Number(m.expenses))} width="14" height={y(0) - y(Number(m.expenses))} rx="3" className="ft-expense-bar" />
            <text x={x(i)} y={height - 10} textAnchor="middle" className="ft-axis">{monthLabel(m.month)}</text>
          </g>)}
          <polyline points={points} className="ft-net-line" />
          {history.map((m, i) => <circle key={m.month} cx={x(i)} cy={y(Number(m.net_cash_flow))} r="4" className="ft-net-dot" />)}
        </svg>
      </div>
      <details className="ft-table-details">
        <summary>View exact monthly values & coverage</summary>
        <div className="ft-table-scroll"><table>
          <caption>Recorded monthly activity · {currency}</caption>
          <thead><tr><th>Month</th><th>Income</th><th>Expenses</th><th>Net cash flow</th><th>Savings rate</th><th>Coverage</th></tr></thead>
          <tbody>{history.map((m) => <tr key={m.month}>
            <th scope="row">{m.month}</th><td>{formatMoney(m.income)}</td><td>{formatMoney(m.expenses)}</td>
            <td>{formatMoney(m.net_cash_flow)}</td><td>{m.savings_rate === null ? "Unavailable" : `${m.savings_rate}%`}</td>
            <td>{m.coverage === "no_recorded_activity" ? "No recorded activity" : `${m.transaction_count} transactions`}{m.partial_month ? " · partial month" : ""}</td>
          </tr>)}</tbody>
        </table></div>
      </details>
    </>
  );
}
