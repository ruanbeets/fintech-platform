import { useState } from "react";
import { useAuthStore } from "../core/authStore";
import { useDashboard } from "../features/dashboard";
import MonthlyHistoryChart from "../components/overview/MonthlyHistoryChart";
import TrendSeriesChart from "../components/overview/TrendSeriesChart";

const monthName = (month) => new Date(`${month}-01T12:00:00Z`).toLocaleDateString("en-ZA", { month: "long", year: "numeric", timeZone: "UTC" });
const percent = (value) => value === null || value === undefined ? "Unavailable" : `${value}%`;
const points = (value) => value === null || value === undefined ? "Unavailable" : `${value} pp`;

export default function AnalyticsPage({ demo = false, imported = false }) {
  const user = useAuthStore((state) => state.user);
  const [month, setMonth] = useState("");
  const [currency, setCurrency] = useState("");
  const [category, setCategory] = useState("");
  const { data, isPending, isError, error, refetch } = useDashboard({ demo, imported, userId: user?.id, month, currency });
  const cash = (value) => value === null || value === undefined ? "Unavailable" :
    new Intl.NumberFormat("en-ZA", { style: "currency", currency: data?.currency || "ZAR", maximumFractionDigits: 2 }).format(value);
  const trends = data?.trends;
  const selectedCategory = trends?.categories.find((c) => c.category === category) || trends?.categories[0];

  return <div className="ft-app">
    <header className="ft-topbar"><a className="ft-brand" href={imported ? "/workspace" : demo ? "/demo" : "/app"}><span className="ft-brand-mark">F</span>FinTrack<span className="ft-brand-divider">/</span><span className="ft-brand-sub">Personal financial intelligence</span></a><span className="ft-demo-badge">{imported ? "PRIVATE DEMO SESSION · IMPORTED DATA" : demo ? "SYNTHETIC SAMPLE DATA" : "RECORDED FINANCES"}</span></header>
    <main className="ft-main">
      <nav className="ft-page-nav" aria-label="Financial views"><a href={imported ? "/workspace" : demo ? "/demo" : "/app"}>Overview</a><a href={imported ? "/workspace/trends" : demo ? "/demo/trends" : "/trends"} aria-current="page">Trends</a><a href="/import">Import data</a></nav>
      <div className="ft-heading"><div><p className="ft-eyebrow">FINANCIAL BEHAVIOUR</p><h1>What is changing<span>?</span></h1><p className="ft-subtitle">Follow your income, spending patterns and likely repeat costs.</p></div>
        {data && <div className="ft-controls"><label>Month<select value={month || data.selected_month} onChange={(e) => setMonth(e.target.value)}>{data.available_months.map((m) => <option key={m} value={m}>{monthName(m)}</option>)}</select></label>
          <label>Currency<select value={currency || data.currency} onChange={(e) => { setCurrency(e.target.value); setMonth(""); }}>{(data.available_currencies.length ? data.available_currencies : [data.currency]).map((c) => <option key={c}>{c}</option>)}</select></label></div>}
      </div>
      {isPending && <section className="ft-state" role="status"><div className="ft-skeleton" /><h2>Starting the FinTrack demo server…</h2><p>Free hosting may take up to about a minute to wake.</p></section>}
      {isError && <section className="ft-state ft-error" role="alert"><h2>Trends unavailable</h2><p>{typeof error?.response?.data?.detail === "string" ? error.response.data.detail : "We could not reach the financial data service. Start the local demo API and retry."}</p><button onClick={() => refetch()}>Try again</button></section>}
      {trends && !isError && <>
        <div className="ft-period"><span className="ft-status-dot" />{monthName(data.selected_month)}<span>Evidence through {trends.observed_through} · {data.currency}{data.selected.partial_month ? " · partial month" : ""}</span></div>
        {data.selected.coverage === "no_recorded_activity" && <div className="ft-empty" role="status"><strong>No recorded activity in this month.</strong> Zero values describe missing records, not confirmed zero spending. Comparisons and expense estimates inherit this gap.</div>}

        <section className="ft-metrics" aria-label="Trend highlights">
          <article className="ft-metric"><p>Income vs previous month</p><h2>{cash(trends.income.previous_month.absolute_change)}</h2><small>{percent(trends.income.previous_month.percentage_change)} change · {trends.income.previous_month.coverage.replaceAll("_", " ")}</small></article>
          <article className="ft-metric"><p>Selected-month expenses</p><h2>{cash(data.selected.expenses)}</h2><small>Recorded spending · excludes transfers</small></article>
          <article className="ft-metric net"><p>Savings-rate change</p><h2>{points(trends.savings.change_percentage_points)}</h2><small>vs {trends.savings.previous_valid?.month || "no earlier valid month"} · percentage points</small></article>
          <article className="ft-metric"><p>Fixed / recurring share</p><h2>{percent(trends.spending.classes[0].share)}</h2><small>Rule-based share of recorded expenses</small></article>
        </section>

        <section className="ft-panel ft-history" aria-label="Income and expense trends">
          <div className="ft-section-heading"><div><p className="ft-eyebrow">INCOME & EXPENSE TREND</p><h2>How your cash flow is changing</h2></div><span className="ft-range">{data.history[0].month} — {data.selected_month}</span></div>
          <MonthlyHistoryChart history={data.history} formatMoney={cash} currency={data.currency} />
          <div className="ft-income-comparisons">
            <div><span>Selected-month income</span><strong>{cash(trends.income.current)}</strong></div>
            <div><span>vs trailing 3-month average</span><strong>{cash(trends.income.versus_3_month_average.absolute_change)}</strong><small>Baseline {cash(trends.income.versus_3_month_average.baseline)} · {percent(trends.income.versus_3_month_average.percentage_change)}</small></div>
            <div><span>vs trailing 6-month average</span><strong>{cash(trends.income.versus_6_month_average.absolute_change)}</strong><small>Baseline {cash(trends.income.versus_6_month_average.baseline)} · {percent(trends.income.versus_6_month_average.percentage_change)}</small></div>
            <div><span>12-month income average</span><strong>{cash(trends.income.average_12_month)}</strong><small>{trends.income.recorded_months} / 12 months with recorded activity</small></div>
          </div>
          <p className="ft-muted">Highest recorded complete month: {trends.income.highest_month ? `${trends.income.highest_month.month} · ${cash(trends.income.highest_month.income)}` : "Unavailable"} · Lowest: {trends.income.lowest_month ? `${trends.income.lowest_month.month} · ${cash(trends.income.lowest_month.income)}` : "Unavailable"}</p>
          <p className="ft-muted">{trends.income.coverage_note}</p>
        </section>

        <section className="ft-panel ft-history" aria-label="Savings-rate trend">
          <div className="ft-section-heading"><div><p className="ft-eyebrow">SAVINGS-RATE TREND</p><h2>How much income remains after spending?</h2></div><span className="ft-mini-badge">PERCENTAGE POINTS ≠ PERCENT CHANGE</span></div>
          <div className="ft-income-comparisons">
            <div><span>Current savings rate</span><strong>{percent(trends.savings.current)}</strong></div>
            <div><span>Previous valid · {trends.savings.previous_valid?.month || "none"}</span><strong>{percent(trends.savings.previous_valid?.savings_rate)}</strong></div>
            {[trends.savings.trailing_3_month_average, trends.savings.trailing_6_month_average].map((a) => <div key={a.window_months}><span>Trailing {a.window_months}-month mean</span><strong>{percent(a.value)}</strong><small>{a.valid_months} valid / {a.window_months} calendar months</small></div>)}
          </div>
          <TrendSeriesChart title="Monthly savings rate" series={trends.savings.history.map((m) => ({ ...m, value: m.savings_rate }))} formatValue={percent} />
          <p className="ft-muted">{trends.savings.methodology}</p>
        </section>

        <section className="ft-panel ft-history" aria-label="Category trends">
          <div className="ft-section-heading"><div><p className="ft-eyebrow">CATEGORY TRENDS</p><h2>Where spending is changing</h2></div><span className="ft-mini-badge">EXPENSES ONLY</span></div>
          {trends.categories.length === 0 ? <p className="ft-empty">No categorized or uncategorised expenses in this 12-month window.</p> : <>
            <div className="ft-table-scroll"><table className="ft-category-table"><caption>Recorded category spending · {data.currency} · sorted by selected-month spend</caption><thead><tr><th>Category</th><th>This month</th><th>Previous</th><th>Change</th><th>Change %</th><th>3-month avg</th><th>6-month avg</th><th>Expense share</th></tr></thead>
              <tbody>{trends.categories.map((c) => <tr key={c.category}><th scope="row">{c.category}</th><td>{cash(c.current_spend)}</td><td>{cash(c.previous_spend)}</td><td>{cash(c.change.absolute_change)}</td><td>{percent(c.change.percentage_change)}</td><td>{cash(c.trailing_3_month_average)}</td><td>{cash(c.trailing_6_month_average)}</td><td>{percent(c.share_of_expenses)}</td></tr>)}</tbody>
            </table></div>
            <p className="ft-muted">Previous-month coverage: {trends.income.previous_month.coverage.replaceAll("_", " ")}. A zero baseline has no percentage change. Missing months remain zero recorded activity, not verified zero spend.</p>
            <div className="ft-controls ft-category-control"><label>Category history<select value={selectedCategory.category} onChange={(e) => setCategory(e.target.value)}>{trends.categories.map((c) => <option key={c.category}>{c.category}</option>)}</select></label></div>
            <TrendSeriesChart title={`${selectedCategory.category} spending history`} series={selectedCategory.history.map((m) => ({ ...m, value: m.spend }))} formatValue={cash} />
          </>}
        </section>

        <section className="ft-panel ft-history" aria-label="Fixed versus variable spending">
          <div className="ft-section-heading"><div><p className="ft-eyebrow">FIXED VS VARIABLE</p><h2>The shape of this month's spending</h2></div><span className="ft-mini-badge">EXPLAINABLE ESTIMATE</span></div>
          <div className="ft-spending-classes">{trends.spending.classes.map((c) => <article key={c.classification}><p>{c.classification.replaceAll("_", " / ")}</p><h3>{cash(c.amount)}</h3><strong>{percent(c.share)} of expenses</strong><p className="ft-muted">{c.transaction_count} recorded expenses</p><p className="ft-muted">{c.explanation}</p></article>)}</div>
          <p className="ft-muted">Reconciled recorded expenses: <strong>{cash(trends.spending.total_expenses)}</strong>. {trends.spending.methodology}</p>
        </section>

        <section className="ft-panel ft-history" aria-label="Recurring transactions">
          <div className="ft-section-heading"><div><p className="ft-eyebrow">RECURRING BEHAVIOUR</p><h2>Likely repeat transactions</h2></div><span className="ft-mini-badge">RULES, NOT CERTAINTY</span></div>
          <p className="ft-muted">Patterns in the last 12 calendar months through {trends.observed_through}. Income and transfers are listed for context; neither counts as spending.</p>
          {trends.recurring.length === 0 ? <p className="ft-empty">No patterns meet the recurrence rules yet. More history may help; this does not prove there are no recurring costs.</p> :
            <div className="ft-table-scroll"><table><caption>Recurring candidates · {data.currency}</caption><thead><tr><th>Merchant / description</th><th>Type / category</th><th>Typical amount</th><th>Frequency</th><th>Evidence</th><th>First / latest</th><th>Next cadence date</th></tr></thead>
              <tbody>{trends.recurring.map((r) => <tr key={`${r.account_id}-${r.transaction_type}-${r.category}-${r.normalized_name}`}><th scope="row">{r.normalized_name}</th><td>{r.transaction_type}<br />{r.category}</td><td>{cash(r.typical_amount)}</td><td>{r.frequency}</td><td><details><summary>{r.strength} · {r.occurrence_count} occurrences</summary><p className="ft-rule-text">{r.evidence}</p></details></td><td>{r.first_observed}<br />{r.most_recent}</td><td>{r.expected_next_occurrence || "Unavailable"}<details><summary>Why?</summary><p className="ft-rule-text">{r.next_occurrence_note}</p></details></td></tr>)}</tbody>
            </table></div>}
          <details className="ft-table-details"><summary>How recurring detection works</summary><p className="ft-muted">{trends.recurring_methodology}</p></details>
        </section>
        <footer className="ft-footnote"><strong>Recorded behaviour, with explicit limits</strong><p>These trends describe recorded transactions in the selected currency. Missing months do not prove zero income or spending. Money averages include calendar gaps as zero recorded activity; savings-rate means exclude unavailable rates. Dates use UTC and partial months are labelled. Recurring candidates are not confirmed commitments.</p>{demo && <p>Synthetic ZAR data · Sep 2024–Aug 2026. November 2025 is deliberately missing. No real accounts are connected.</p>}</footer>
      </>}
    </main>
  </div>;
}
