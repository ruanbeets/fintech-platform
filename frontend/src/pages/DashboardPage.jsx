import { Link } from "react-router-dom";
import { useState } from "react";
import { useAuthStore } from "../core/authStore";
import { useDashboard } from "../features/dashboard";
import MonthlyHistoryChart from "../components/overview/MonthlyHistoryChart";

const labelMonth = (month) => new Date(`${month}-01T12:00:00Z`).toLocaleDateString("en-ZA", {
  month: "long", year: "numeric", timeZone: "UTC",
});

export default function DashboardPage({ demo = false, imported = false }) {
  const user = useAuthStore((state) => state.user);
  const [month, setMonth] = useState("");
  const [currency, setCurrency] = useState("");
  const { data, isPending, isError, error, refetch } = useDashboard({ demo, imported, userId: user?.id, month, currency });
  const formatMoney = (value) => value === null || value === undefined ? "Unavailable" :
    new Intl.NumberFormat("en-ZA", { style: "currency", currency: data?.currency || "ZAR", maximumFractionDigits: 2 }).format(value);
  const selected = data?.selected;

  return (
    <div className="ft-app">
      <header className="ft-topbar">
        <a className="ft-brand" href={imported ? "/workspace" : demo ? "/demo" : "/app"}><span className="ft-brand-mark">F</span>FinTrack<span className="ft-brand-divider">/</span><span className="ft-brand-sub">Personal financial intelligence</span></a>
        <span className="ft-demo-badge">{imported ? "PRIVATE DEMO SESSION · IMPORTED DATA" : demo ? "SYNTHETIC SAMPLE DATA" : "RECORDED FINANCES"}</span>
      </header>
      <main className="ft-main">
        <nav className="ft-page-nav" aria-label="Financial views"><Link to={imported ? "/workspace" : demo ? "/demo" : "/app"} aria-current="page">Overview</Link><Link to={imported ? "/workspace/trends" : demo ? "/demo/trends" : "/trends"}>Trends</Link><Link to="/import">Import data</Link></nav>
        <div className="ft-heading">
          <div><p className="ft-eyebrow">YOUR FINANCIAL PICTURE</p><h1>Overview<span>.</span></h1>
            <p className="ft-subtitle">Understand your cash flow. See the longer view.</p></div>
          {data && <div className="ft-controls">
            <label>Month<select value={month || data.selected_month} onChange={(e) => setMonth(e.target.value)}>
              {data.available_months.map((value) => <option key={value} value={value}>{labelMonth(value)}</option>)}
            </select></label>
            <label>Currency<select value={currency || data.currency} onChange={(e) => { setCurrency(e.target.value); setMonth(""); }}>
              {(data.available_currencies.length ? data.available_currencies : [data.currency]).map((value) => <option key={value}>{value}</option>)}
            </select></label>
          </div>}
        </div>

        {imported && sessionStorage.getItem("fintrack-import-result") && <div className="ft-empty" role="status">{sessionStorage.getItem("fintrack-import-result")}</div>}
        {isPending && <section className="ft-state" role="status"><div className="ft-skeleton" /><h2>Starting the FinTrack demo server…</h2><p>Free hosting may take up to about a minute to wake.</p></section>}
        {isError && <section className="ft-state ft-error" role="alert"><h2>Overview unavailable</h2>
          <p>{typeof error?.response?.data?.detail === "string" ? error.response.data.detail : "We could not reach the financial data service."}</p>
          {demo && <p>Start the local demo API from the backend folder: <code>python -m scripts.run_demo</code></p>}
          <button onClick={() => refetch()}>Try again</button></section>}

        {data && !isError && <>
          <div className="ft-period"><span className="ft-status-dot" />{labelMonth(data.selected_month)}
            <span>{selected.partial_month ? "Month to date · partial month" : "Calendar month"} · {selected.transaction_count} recorded transactions · {data.currency}</span>
          </div>
          {selected.coverage === "no_recorded_activity" && <div className="ft-empty" role="status"><strong>No recorded activity this month.</strong> Values below are zero recorded activity, not proof of zero income or spending. Select another month to explore the history.</div>}

          <section className="ft-metrics" aria-label="Selected month metrics">
            {[
              ["Income", selected.income, "Recorded money in", "income"],
              ["Expenses", selected.expenses, "Recorded spending", "expenses"],
              ["Net cash flow", selected.net_cash_flow, "Income minus expenses", "net"],
            ].map(([title, value, caption, tone]) => <article className={`ft-metric ${tone}`} key={title}><p>{title}<span aria-hidden="true">{tone === "expenses" ? "↗" : "↙"}</span></p><h2>{formatMoney(value)}</h2><small>{caption} · excludes transfers</small></article>)}
            <article className="ft-metric"><p>Savings rate<span aria-hidden="true">%</span></p><h2>{selected.savings_rate === null ? "Unavailable" : `${selected.savings_rate}%`}</h2><small>{selected.savings_rate === null ? "No recorded income to calculate a rate" : "Net cash flow ÷ income · before transfers"}</small></article>
          </section>

          <section className="ft-panel ft-history">
            <div className="ft-section-heading"><div><p className="ft-eyebrow">THE LONGER VIEW</p><h2>Cash flow over time</h2></div>
              <span className="ft-range">{data.history[0].month} — {data.selected_month} · 12 MONTHS</span></div>
            <MonthlyHistoryChart history={data.history} formatMoney={formatMoney} currency={data.currency} />
          </section>

          <section className="ft-rolling" aria-label="Trailing monthly averages">
            {[selected.trailing_3_month, selected.trailing_6_month].map((average) => <article className="ft-panel" key={average.months}>
              <div className="ft-section-heading"><h2>Trailing {average.months}-month average</h2><span className="ft-mini-badge">PER MONTH</span></div>
              <p className="ft-muted">Through {labelMonth(data.selected_month)}{selected.partial_month ? " · includes partial month" : ""}</p>
              {average.status === "insufficient_history" ? <p className="ft-unavailable">Unavailable · not enough historical months.</p> :
                <dl className="ft-average-values"><div><dt>Income</dt><dd>{formatMoney(average.income)}</dd></div><div><dt>Expenses</dt><dd>{formatMoney(average.expenses)}</dd></div><div><dt>Net cash flow</dt><dd className="ft-green">{formatMoney(average.net_cash_flow)}</dd></div></dl>}
              <small className="ft-muted">{average.recorded_months} of {average.months} months contain recorded activity. Missing months count as zero recorded activity.</small>
            </article>)}
          </section>

          <section className="ft-bottom-grid">
            <article className="ft-panel"><div className="ft-section-heading"><h2>Account balances</h2><span className="ft-mini-badge">UNAVAILABLE</span></div>
              {data.account_balances.length ? data.account_balances.map((account) => <div className="ft-account-row" key={account.account_id}><span><i aria-hidden="true">▤</i>{account.name}<small>{account.currency}</small></span><strong>Unavailable</strong></div>) : <p className="ft-muted">No accounts recorded for this currency.</p>}
              <p className="ft-muted ft-explanation">No opening balances, snapshots or valuations are recorded. Transaction net flows are not account balances.</p>
            </article>
            <article className="ft-panel"><div className="ft-section-heading"><h2>Net worth</h2><span className="ft-mini-badge">UNAVAILABLE</span></div>
              <p className="ft-unavailable">More data needed</p><p className="ft-muted">{data.net_worth.reason}</p>
              <div className="ft-principle">A clear gap is more useful than a misleading number.</div>
            </article>
          </section>
          <footer className="ft-footnote"><strong>How to read these numbers</strong><p>{data.coverage_note}</p>
            {demo && <p>Synthetic fixture: Sep 2024–Aug 2026. November 2025 is intentionally missing. No real accounts are connected.</p>}
          </footer>
        </>}
      </main>
    </div>
  );
}
