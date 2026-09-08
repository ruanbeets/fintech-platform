# FinTrack reviewed-import demo

Slice 3A adds reviewed financial file ingestion to the existing Overview and Trends. No anomaly/AI/forecasting calculations were added.

## Local launch (PowerShell)

From D:\Dev\Repos\fintech-platform, first-time setup with Python 3.12 and a Vite-compatible Node installation:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
cd frontend
npm ci
```

Backend terminal:
```powershell
cd D:\Dev\Repos\fintech-platform\backend
..\.venv\Scripts\python.exe -m scripts.run_demo
```

Frontend terminal:
```powershell
cd D:\Dev\Repos\fintech-platform\frontend
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Open http://127.0.0.1:5173/import. The launcher overrides database settings only in its process, uses ignored backend/.demo/overview.sqlite3, seeds the unchanged synthetic dataset, and binds loopback. Existing local PostgreSQL configuration is preserved. The old authenticated Overview route is available at /app; the public entry is /import.

## Import contract

- CSV (UTF-8/BOM, UTF-16 BOM, CP1252; comma, semicolon, tab or pipe), XLSX, XLS, XLSB and ODS use bounded table parsing. Excel uses python-calamine. XLSB is supported by the parser but has no end-to-end generated XLSB fixture in this repository.
- Text PDFs require extractable, consistently headed tables; pdfplumber cannot reliably interpret arbitrary layouts. Scans, loose text, encrypted/damaged files and uncertain structures are rejected. No OCR.
- 5 MB/file, 5,000 data rows, 50 columns, 10 sheets, 20 PDF pages; compressed workbook expansion capped at 25 MB. Parser subprocess timeout 20 seconds, two parser slots per process.
- Exact normalized header aliases suggest each mapping with high/ambiguous/unmapped confidence. Header candidates come from the first 50 rows. Ambiguous fields remain unmapped. Select the sheet/header, then press Detect selected table when changing either.
- Mandatory review specifies account label, currency, date order, decimal separator and signed-amount convention. ISO/Excel dates supported. Financial amounts use Decimal, two decimal places and the existing Numeric(14,2) range. No invalid amount becomes zero.
- Signed Amount, positive Debit/Credit and signed Money In/Money Out/Fee normalize through the same Decimal service. Posting and transaction dates are distinct; explicit source Transfer classifications and reviewed row overrides exclude transfers from analytics. See [the ingestion contract](INGESTION.md).
- Each currency is imported separately. Currency fields/symbols conflicting with the selected currency cause row errors. Blank categories remain uncategorised. Unsupported descriptions/dates/amounts give row-level errors. Source corrections require re-upload; type/exclusion changes require revalidation.
- Source balances reconcile adjacent statement movements and are retained as provenance. Account balances and net worth remain unavailable.
- Duplicate handling now uses balance/reference evidence and retains repeated no-balance purchases within a statement. See [the ingestion contract](INGESTION.md) for occurrence matching, limitations and the synthetic reconciliation fixtures.
- Server-owned reviewed snapshot and revision token prevent client-supplied amounts at confirmation. Confirmation is transactional and idempotent, with a unique database fingerprint constraint and PostgreSQL session row lock.
- All financial analytics come from DashboardViewModel and the existing services; no frontend finance calculations.

## Privacy and storage

Use anonymised/test data only. Anonymous capability sessions are not production authentication. Keep the random session key private; possession grants access. Only its SHA-256 hash is stored in the database; the browser stores the key in sessionStorage, never in URLs. Requests/responses are marked no-store; source rows and account labels are not logged by application code. Uvicorn access logs are disabled.

Original files stay in memory and are discarded after parsing; there are no upload files on disk. Parsed source rows/review snapshots live in PostgreSQL for review, are cleared on confirmation, and expire after one hour. Normalized transactions and minimal import provenance expire with the 24-hour session. Expiry denies access immediately; deletion runs at startup and every 15 minutes while the service is awake. On free-tier sleep, expired rows remain inaccessible until the next startup cleanup. Delete my imported data removes only that session's records immediately. Browser closure alone does not immediately delete stored data.

Per-session quotas: 20 uploaded batches, 20,000 transactions. Basic in-memory per-client throttling allows 60 POSTs/minute. These are lightweight demo safeguards, not an adversarial abuse/security certification. No audit logging, verified identity, recovery, backups lifecycle or production tenancy system is claimed.

## Public hosting: actions requiring your accounts

1. Create/select a dedicated Supabase Free project. Use **only synthetic/anonymised demo data**. Disable the Supabase Data API for this project (FastAPI uses PostgreSQL directly). No frontend Supabase SDK or public API key is needed.
2. Copy the **Session pooler** PostgreSQL connection string from Supabase Connect. Use a table-owning backend database role; URL-encode special password characters and require TLS (`?sslmode=require`). Keep it solely in Render's secret DATABASE_URL. The startup creates only missing FinTrack tables and enables PostgreSQL RLS without browser-role policies on these tables. Use a dedicated project; do not mix with existing tables/policies.
3. Connect your repository to Render. Create the backend Free Python web service, root `backend`, Python 3.12, build `pip install -r requirements.txt`, start `python -m scripts.serve`, health `/health`. Alternatively review the included render.yaml Blueprint.
4. Set DEMO_MODE=true, LOCAL_DEMO=false, DATABASE_URL, CORS_ALLOWED_ORIGINS (exact HTTPS frontend origin, comma-separated if needed), SESSION_HOURS=24. Do not use wildcard CORS. Render supplies PORT; serve binds 0.0.0.0:$PORT. Public demo mode refuses SQLite.
5. Create the free static frontend on Render (or another static host), root `frontend`, build `npm ci && npm run build`, publish `dist`. Set VITE_API_BASE_URL to the HTTPS backend URL and rebuild. Configure SPA rewrite `/* → /index.html` (included in Blueprint; _redirects supports compatible hosts).
6. Update backend CORS_ALLOWED_ORIGINS to the final frontend origin. Verify /health, /import, CSV/XLSX acceptance, expiry/delete and a separate browser session. Confirm /dashboard/{user_id}, /users, /transactions and legacy auth routes return 404 in DEMO_MODE. Verify Supabase browser/Data API access is disabled before sharing the URL.
7. Review the final Git diff, push only intended code/fixtures/config examples, and approve any external account connection. No deployment, account creation or credential submission was performed by Codex.

Public storage is PostgreSQL, never Render's ephemeral filesystem. Free services can sleep and impose resource limits; the UI shows loading/retry states. The live Supabase connection, TLS, hosted RLS and Render/static-host integration still need a deployment smoke test. Local PostgreSQL initialization and RLS isolation have passed.

Official hosting references: [Render free instances](https://render.com/docs/free), [Render web-service ports](https://render.com/docs/web-services), [Supabase PostgreSQL connections](https://supabase.com/docs/guides/database/connecting-to-postgres).

## Verification

```powershell
cd D:\Dev\Repos\fintech-platform\backend
..\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
cd ..\frontend
npm run build
npx eslint src/pages/UploadPage.jsx src/pages/DashboardPage.jsx src/pages/AnalyticsPage.jsx src/features/imports.js src/features/dashboard.js src/app/router.jsx
```

Synthetic fixtures are in backend/tests/fixtures. Rebuild them with requirements-dev installed using `python tests/fixtures/generate.py`. They contain no real bank details. XLS/ODS/CSV/XLSX/table-PDF parser tests and existing Slice 1/2 regressions run without connecting to your database.

Independent August 2026 fixture ledger totals, excluding transfers:

| Fixture | Transactions | Income ZAR | Expenses ZAR | Net cash flow ZAR |
|---|---:|---:|---:|---:|
| standard.csv | 4 (including 1 transfer) | 1,000.00 | 250.00 | 750.00 |
| debit_credit.csv | 3 | 2,000.00 | 625.00 | 1,375.00 |
| renamed_headers.xlsx | 4 (including 1 transfer) | 3,000.00 | 699.99 | 2,300.01 |

Tests assert these totals at review and after persistence through the existing analytics API, including Trends expense reconciliation. Missing months retain existing explicit coverage semantics.

## Slice 3A file inventory

New backend files: app/demo_app.py; app/models/imports.py; app/schemas/imports.py; app/services/file_parser.py; app/services/import_normalization.py; app/services/import_sessions.py; app/views/import_view.py; scripts/serve.py; requirements-dev.txt; .env.example; tests/test_imports.py.

Updated backend files: app/core/config.py; app/database/connection.py; app/database/init_db.py; app/views/dashboard_view.py (sample availability only); main.py (demo surface selection only); scripts/run_demo.py; requirements.txt; Dockerfile; .dockerignore.

New frontend files: src/features/imports.js; public/_redirects; .env.example. Updated frontend files: index.html (title/description only); src/pages/UploadPage.jsx; src/pages/DashboardPage.jsx; src/pages/AnalyticsPage.jsx; src/features/dashboard.js; src/app/router.jsx; src/styles/globals.css.

Synthetic fixtures: tests/fixtures/generate.py, standard.csv, debit_credit.csv, malformed.csv, missing_column.csv, duplicates.csv, positive_expense.csv, manual.csv, renamed_headers.xlsx, standard.xlsx, standard.xls, standard.ods, synthetic_statement.pdf (all under backend).

Repository/deployment: render.yaml, docs/PUBLIC_DEMO.md, README.md, .gitignore.

Existing analytics, trends, recurrence services and the demo seed were reused without Slice 3A changes. Earlier uncommitted Slice 1/2 and frontend work remains in the Git diff; this inventory identifies only Slice 3A work.

Supabase exposure guidance: [disable the Data API](https://supabase.com/docs/guides/api/securing-your-api). Render configuration: [Blueprint specification](https://render.com/docs/blueprint-spec).

## Local acceptance result

81 backend tests pass (54 existing Slice 1/2 regressions plus 27 import/deployment tests). Frontend production build and targeted ESLint pass. Build reports only the existing stale Browserslist-data advisory.

Browser acceptance: CSV automatic mapping, preview, confirmation and Overview/Trends; repeat CSV caught 4/4 duplicates with zero rows to import; renamed-column XLSX detected Transactions/header row 3 and reconciled its independent totals in Overview and Trends; malformed CSV produced two explicit row errors with confirmation disabled; session deletion worked; synthetic table PDF passed the same reviewed flow and produced income R1,000.00, expenses R250.00 and net R750.00. No browser console warnings/errors were observed. Desktop layout was visually inspected. Health returned 200; allowed-origin preflight succeeded; legacy /users returned 404 in demo mode.

Fresh PostgreSQL 18 initialization, synthetic seeding, three fixture imports with reconciled analytics, deletion and RLS guest isolation passed using a temporary local cluster. Live Supabase TLS/RLS and Render deployment have not been exercised. Complete the hosting smoke test above before publicly sharing the demo. XLSB remains parser-supported without a generated end-to-end fixture; scanned PDFs, arbitrary loose-text layouts, password-protected documents, unsupported locale/sign conventions and exports missing verifiable transaction dates require a cleaner export.

## Portfolio-release readiness

Feature development is frozen. The entry prioritizes Try sample demo and Upload CSV / Excel; PDF is labelled Text-based statements only. The README contains captured synthetic-data screenshots and distinguishes implemented features from future work.

VITE_API_BASE_URL is the preferred frontend setting (legacy VITE_API_URL still works locally). Render builds reject localhost/non-HTTPS backend settings. A cloud-configured build was checked to contain its configured HTTPS API origin and no localhost API fallback. Public backend startup rejects missing/non-HTTPS frontend CORS origins. SPA rewrites are included in render.yaml.

Final local checks: 81 backend tests; production build; targeted ESLint including API configuration and Vite config; fresh PostgreSQL 18 schema/sample initialization, three reconciled fixture imports, deletion and RLS guest isolation. Sample Overview/Trends and the inaccessible state after session deletion were rechecked in the browser. Temporary PostgreSQL clusters and generated verification build output were removed. No feature work or test-suite expansion was performed during the freeze.

No public services have been provisioned or deployed. The deployment release preserves the existing frontend and completed slices; unrelated local login work is excluded from the release. External account configuration is the next step; never paste database credentials into chat.
