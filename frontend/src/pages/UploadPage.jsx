import { useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { importClient, ensureSession, deleteSession, errorMessage } from "../features/imports";

const fields = { date: "Posting / booking date", transaction_datetime: "Transaction date (optional)", description: "Description / reference",
  original_description: "Original description", amount: "Amount", debit: "Debit / money out", fee: "Fee",
  credit: "Credit / money in", currency: "Currency", category: "Source category", parent_category: "Parent category",
  account: "Source account (hidden)", source_reference: "Transaction reference (hidden)", balance: "Statement balance", transaction_type: "Transaction type" };
const initial = { account: "Everyday account", currency: "ZAR", date_order: "DMY", number_format: "dot", sign_convention: "negative_expense",
  type_overrides: {}, excluded_rows: [] };

export default function UploadPage() {
  const navigate = useNavigate();
  const cache = useQueryClient();
  const fileInput = useRef(null);
  const [accept, setAccept] = useState(".csv,.xlsx,.xls,.xlsb,.ods");
  const [detected, setDetected] = useState(null);
  const [options, setOptions] = useState(initial);
  const [review, setReview] = useState(null);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [skipInvalid, setSkipInvalid] = useState(false);
  const [page, setPage] = useState(0);
  const [fileName, setFileName] = useState("");
  const [erasePrompt, setErasePrompt] = useState(false);
  const [editMapping, setEditMapping] = useState(false);
  const update = (next) => { setOptions((old) => ({ ...old, ...next })); setReview(null); setConfirmed(false); };
  const act = async (label, work) => {
    setBusy(label); setError("");
    try { await work(); } catch (e) { setError(errorMessage(e)); } finally { setBusy(""); }
  };
  const applyDetection = (data) => {
    setDetected(data);
    const next = { ...initial, ...data.defaults, sheet: data.sheet, header_row: data.header_row,
      mapping: Object.fromEntries(Object.entries(data.mapping).map(([key, value]) => [key, value.column])),
      type_overrides: {}, excluded_rows: [] };
    setOptions(next); setEditMapping(!data.high_confidence);
    setReview(null); setConfirmed(false); setSkipInvalid(false); setPage(0);
    return next;
  };
  const upload = (file) => {
    if (!file) return;
    setDetected(null); setReview(null);
    if (file.size > 5 * 1024 * 1024) { setError("Upload limit: 5 MB. Split the export first."); return; }
    act("Reading your file…", async () => {
      await ensureSession();
      const { data } = await importClient.post("/imports/upload", file, {
        headers: { "Content-Type": "application/octet-stream", "X-File-Name": encodeURIComponent(file.name) },
      });
      setFileName(file.name); const next = applyDetection(data);
      if (data.high_confidence) {
        const checked = await importClient.post(`/imports/${data.batch_id}/review`, next);
        setReview(checked.data);
        if (checked.data.invalid || checked.data.reconciliation?.status === "FAILED" || checked.data.reconciliation?.probable_sign_error) setEditMapping(true);
      }
    });
  };
  const validate = () => act("Validating rows…", async () => {
    const { data } = await importClient.post(`/imports/${detected.batch_id}/review`, options);
    setReview(data); setConfirmed(false); setPage(0);
  });
  const finish = () => act("Importing reviewed transactions…", async () => {
    const { data } = await importClient.post(`/imports/${detected.batch_id}/confirm`, {
      review_id: review.review_id, confirmed: true, skip_invalid: skipInvalid,
    });
    sessionStorage.setItem("fintrack-import-result", `${data.message} ${data.duplicates} duplicates, ${data.skipped_invalid} invalid and ${data.excluded} excluded rows skipped.`);
    await cache.invalidateQueries({ queryKey: ["dashboard"] });
    navigate("/workspace");
  });
  const cash = (value) => new Intl.NumberFormat("en-ZA", { style: "currency", currency: review?.currency || options.currency }).format(value);
  const choose = (types) => { setAccept(types); setTimeout(() => fileInput.current?.click(), 0); };

  return <div className="ft-app">
    <header className="ft-topbar"><Link className="ft-brand" to="/import"><span className="ft-brand-mark">F</span>FinTrack<span className="ft-brand-divider">/</span><span className="ft-brand-sub">Personal financial intelligence</span></Link><span className="ft-demo-badge">PUBLIC DEMO · TEST DATA ONLY</span></header>
    <main className="ft-main ft-import">
      <nav className="ft-page-nav" aria-label="Financial views"><Link to="/import" aria-current="page">Import data</Link><Link to="/workspace">Your Overview</Link><Link to="/workspace/trends">Your Trends</Link><Link to="/demo">Sample demo</Link></nav>
      <div className="ft-heading"><div><p className="ft-eyebrow">YOUR DATA → YOUR FINANCIAL PICTURE</p><h1>Import data<span>.</span></h1><p className="ft-subtitle">Bring an export. Check the details. Understand your finances.</p></div></div>
      <div className="ft-empty"><strong>Use anonymised or synthetic data.</strong> This demo is not a production banking service. Your browser tab holds a private session key. Imported data expires after 24 hours; source previews expire after one hour. Files are discarded after parsing. Closing the tab loses access; use Delete my imported data to erase it sooner.</div>
      <section className="ft-panel">
        <h2>1. Choose your starting point</h2>
        <div className="ft-import-actions">
          <Link className="ft-import-link" to="/demo">Try sample demo</Link>
          <button disabled={!!busy} onClick={() => choose(".csv,.xlsx,.xls,.xlsb,.ods")}>Upload CSV / Excel</button>
        </div>
        <div className="ft-import-actions"><button disabled={!!busy} onClick={() => choose(".pdf")}>Upload PDF statement</button><span className="ft-muted">Text-based statements only.</span></div>
        <input ref={fileInput} type="file" accept={accept} aria-label="Financial export file" className="ft-file-input" onChange={(e) => { upload(e.target.files[0]); e.target.value = ""; }} />
        <p className="ft-muted">CSV, XLSX, XLS, XLSB, ODS · up to 5 MB, 5,000 rows and 10 sheets. PDF: text-based tables only, up to 20 pages. No scanned statements or OCR.</p>
      </section>
      {busy && <div className="ft-state" role="status"><div className="ft-skeleton" />{busy}{busy === "Reading your file…" && <p>Starting the FinTrack demo server… Free hosting may take up to about a minute to wake.</p>}</div>}
      {error && <div className="ft-state ft-error" role="alert"><h2>Import needs attention</h2><p>{error}</p><p>Nothing from this step was imported. Adjust the file or mapping and try again.</p></div>}
      {detected && <fieldset disabled={!!busy} className="ft-import-fieldset">
        <section className="ft-panel">
          <h2>2. Statement detected</h2><p className="ft-muted">{fileName} · {detected.row_count} source rows in {detected.sheet}. Check the normalized preview before importing.</p>
          <p>{Object.entries(fields).filter(([key]) => options.mapping[key] != null).map(([key, label]) => `${detected.mapping[key]?.confidence === "high" ? "✓" : "Review"} ${label}: ${detected.headers[options.mapping[key]]}`).join(" · ")}</p>
          <p>Date order: {options.date_order} · Decimal separator: {options.number_format === "comma" ? "comma" : "point"} · Currency: {options.currency}</p>
          <button onClick={() => setEditMapping(!editMapping)}>{editMapping ? "Hide mapping details" : "Edit mapping / formats"}</button>
          {editMapping && <>
          <div className="ft-import-grid">
            <label>Sheet<select value={options.sheet} onChange={(e) => update({ sheet: e.target.value })}>{detected.sheets.map((sheet) => <option key={sheet}>{sheet}</option>)}</select></label>
            <label>Header row<input type="number" min="1" max="50" value={options.header_row} onChange={(e) => update({ header_row: Number(e.target.value) })} /></label>
            <button onClick={() => act("Detecting columns…", async () => {
              const { data } = await importClient.post(`/imports/${detected.batch_id}/detect`, { sheet: options.sheet, header_row: options.sheet === detected.sheet ? options.header_row : null });
              applyDetection(data);
            })}>Detect selected table</button>
          </div>
          <div className="ft-import-grid">{Object.entries(fields).map(([key, label]) => <label key={key}>{label}<span className="ft-muted">Suggestion: {detected.mapping[key]?.confidence || "unmapped"}</span>
            <select value={options.mapping[key] ?? ""} onChange={(e) => update({ mapping: { ...options.mapping, [key]: e.target.value === "" ? null : Number(e.target.value) } })}>
              <option value="">Not mapped</option>{detected.headers.map((name, i) => <option value={i} key={i}>{i + 1}. {name || "(blank header)"}</option>)}
            </select></label>)}</div>
          <p className="ft-muted">Posting date controls monthly totals. Money Out and Fee may be signed negative columns. Explicit source Transfer categories are excluded from income and expenses. Review ambiguous dates and classifications.</p>
          <div className="ft-table-scroll"><table><caption>Source preview · first 10 rows</caption><thead><tr>{detected.headers.map((name, i) => <th key={i}>{name || "—"}</th>)}</tr></thead><tbody>{detected.preview.map((row, i) => <tr key={i}>{detected.headers.map((_, j) => <td key={j}>{row[j]}</td>)}</tr>)}</tbody></table></div>
          </>}
        </section>
        {editMapping && <section className="ft-panel"><h2>3. Set how to read the values</h2><div className="ft-import-grid">
          <label>Account label<input value={options.account} maxLength={80} onChange={(e) => update({ account: e.target.value })} /><small>Use the same label for later exports. Do not enter account numbers.</small></label>
          <label>Currency<select value={options.currency} onChange={(e) => update({ currency: e.target.value })}>{["ZAR","USD","EUR","GBP","AUD","CAD","NZD","CHF","JPY","INR","BWP","NAD","KES","NGN","SGD","HKD"].map((code) => <option key={code}>{code}</option>)}</select><small>Import each currency separately.</small></label>
          <label>Date order<select value={options.date_order} onChange={(e) => update({ date_order: e.target.value })}><option value="DMY">Day / Month / Year</option><option value="MDY">Month / Day / Year</option><option value="YMD">Year / Month / Day</option></select></label>
          <label>Number format<select value={options.number_format} onChange={(e) => update({ number_format: e.target.value })}><option value="dot">1,234.56 · decimal point</option><option value="comma">1.234,56 · decimal comma</option></select></label>
          <label>Amount model<select value={options.amount_model || "auto"} onChange={(e) => update({ amount_model: e.target.value })}><option value="auto">Detect from headers</option><option value="signed">Signed Amount (includes any fee)</option><option value="debit_credit">Debit / Credit / Fee: positive magnitudes</option><option value="money_columns">Money In positive / Money Out and Fee negative</option></select></label>
          <label>Signed amount convention<select value={options.sign_convention} onChange={(e) => update({ sign_convention: e.target.value })}><option value="negative_expense">Negative = money out; positive = money in</option><option value="positive_expense">Positive = money out; negative = money in</option></select></label>
        </div><button disabled={options.sheet !== detected.sheet || options.header_row !== detected.header_row} onClick={validate}>Validate & preview transactions</button>
          {(options.sheet !== detected.sheet || options.header_row !== detected.header_row) && <p className="ft-muted">Press Detect selected table to refresh the mapping and source preview first.</p>}</section>}
        {!editMapping && !review && <button onClick={validate}>Validate & preview transactions</button>}
        {review && <section className="ft-panel" aria-label="Validated transactions"><h2>4. Review before importing</h2>
          <p><strong>{review.amount_model}</strong> · {review.date_start || "No valid dates"} — {review.date_end || "—"} · {review.account_count} account(s)</p>
          {review.reconciliation && <div className="ft-empty"><strong>Balance reconciliation: {review.reconciliation.status}</strong>
            <p>{review.reconciliation.rows_matched} of {review.reconciliation.rows_tested} comparable movements matched · Confidence: {review.reconciliation.confidence} · Maximum difference: {cash(review.reconciliation.maximum_difference)}</p>
            {!!review.reconciliation.failed_rows.length && <p>Check source rows: {review.reconciliation.failed_rows.join(", ")}. A mismatch may indicate an omitted movement or incorrect mapping.</p>}
            {!!review.reconciliation.skipped_rows.length && <p>Gaps / excluded rows: {review.reconciliation.skipped_rows.join(", ")}. Reconciliation does not bridge these gaps.</p>}
            {review.reconciliation.probable_sign_error && <p role="alert">Probable sign-convention error: reversing movements matches more balances. Edit the amount convention and validate again.</p>}
            <p>No opening balance is invented. This check validates statement movements, not completeness or current account value.</p>
          </div>}
          <div className="ft-import-counts">{[["Detected", review.detected], ["Valid", review.valid], ["Invalid", review.invalid], ["Possible duplicates", review.duplicates], ["Excluded", review.excluded], ["To import", review.to_import]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
          <p>New rows: income <strong>{cash(review.income)}</strong> · expenses <strong>{cash(review.expenses)}</strong> · net cash flow <strong>{cash(review.net_cash_flow)}</strong></p>
          <p className="ft-muted">{review.warning}</p>
          <div className="ft-table-scroll"><table><caption>Normalized preview · rows {page * 10 + 1}–{Math.min((page + 1) * 10, review.rows.length)} of {review.rows.length}</caption>
            <thead><tr><th>Source row</th><th>Posting date</th><th>Description</th><th>Movement</th><th>Balance</th><th>Type</th><th>Category</th><th>Status / errors</th><th>Exclude</th></tr></thead>
            <tbody>{review.rows.slice(page * 10, page * 10 + 10).map((row) => <tr key={row.source_row}><td>{row.source_row}</td><td>{row.transaction?.date.slice(0, 10) || "—"}</td><td>{row.transaction?.description || "See source row"}</td><td>{row.transaction ? cash(row.transaction.signed_amount ?? row.transaction.amount) : "—"}</td><td>{row.transaction?.balance_optional != null ? cash(row.transaction.balance_optional) : "—"}</td><td>
              <select aria-label={`Type for row ${row.source_row}`} value={options.type_overrides[row.source_row] || row.transaction?.transaction_type || ""} onChange={(e) => { setOptions((old) => ({ ...old, type_overrides: { ...old.type_overrides, [row.source_row]: e.target.value } })); setConfirmed(false); setReview((old) => ({ ...old, stale: true })); }}>
                <option value="" disabled>Choose type</option><option value="income">Income</option><option value="expense">Expense</option><option value="transfer">Transfer</option>
              </select></td><td>{row.transaction?.category || "Uncategorised"}</td><td>{row.status}{row.errors.map((message) => <p key={message}>{message}</p>)}</td><td><input type="checkbox" aria-label={`Exclude row ${row.source_row}`} checked={options.excluded_rows.includes(row.source_row)} onChange={(e) => { setOptions((old) => ({ ...old, excluded_rows: e.target.checked ? [...old.excluded_rows, row.source_row] : old.excluded_rows.filter((r) => r !== row.source_row) })); setConfirmed(false); setReview((old) => ({ ...old, stale: true })); }} /></td></tr>)}</tbody></table></div>
          <div className="ft-import-actions"><button disabled={page === 0} onClick={() => setPage(page - 1)}>Previous rows</button><button disabled={(page + 1) * 10 >= review.rows.length} onClick={() => setPage(page + 1)}>Next rows</button>{review.stale && <button onClick={validate}>Revalidate changed rows</button>}</div>
          {review.invalid > 0 && <label className="ft-check"><input type="checkbox" checked={skipInvalid} onChange={(e) => setSkipInvalid(e.target.checked)} />Skip the {review.invalid} invalid rows. Valid rows can be imported.</label>}
          <label className="ft-check"><input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />I checked the mapping, dates, currency and classifications, including transfers.</label>
          <button disabled={!confirmed || review.stale || (!!review.invalid && !skipInvalid) || !review.to_import} onClick={finish}>Import {review.to_import} transactions</button>
        </section>}
      </fieldset>}
      <footer className="ft-footnote"><p>The sample demo and your imported data are separate. No bank connections. No financial advice.</p>
        {!erasePrompt ? <button disabled={!!busy} onClick={() => setErasePrompt(true)}>Delete my imported data</button> : <div><p>Delete all data in this browser tab’s import session? This cannot be undone.</p><button disabled={!!busy} onClick={() => act("Deleting session data…", async () => { await deleteSession(); cache.removeQueries({ queryKey: ["dashboard"] }); setDetected(null); setReview(null); setErasePrompt(false); })}>Delete this session now</button> <button onClick={() => setErasePrompt(false)}>Keep my session</button></div>}
      </footer>
    </main>
  </div>;
}
