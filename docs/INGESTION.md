# Reviewed bank-statement ingestion

FinTrack supports a small set of explicit amount models instead of a bank-specific parser. No real statement data is included in this repository.

## Interview explanation

“I separate file parsing from financial interpretation. Header aliases suggest a mapping; the user reviews ambiguous formats. Decimal normalization keeps posting dates, transaction dates, signed movements and source categories. Running balances independently check the interpretation. Only reviewed, validated transactions enter the existing analytics service.”

## Stages and contract

1. `file_parser.py`: bounded CSV/workbook/PDF table parsing; deterministic header aliases within the first 50 rows. CSV supports comma, semicolon and tab delimiters, including metadata before the header. Existing file limits remain unchanged.
2. `import_detection.py`: suggest the amount model, date order and decimal separator. A unique exact header alias is high confidence; multiple matches remain ambiguous/unmapped. Optional missing fields are allowed. Ambiguous day/month dates require visible format review. ISO dates are unambiguous. Defaults are suggestions, not proof.
3. `import_normalization.py`: map source cells, parse Decimal amounts and dates, validate each row. Booking date (`date`/`booking_date`) comes from Posting/Booking/Date and drives existing monthly analytics. A separate transaction timestamp is preserved. A lone transaction date becomes the booking date. ISO timestamps normalize to UTC, consistent with existing analytics.
4. `import_reconciliation.py`: independently compare adjacent reported balances using `previous balance + current signed movement`, separately by account/currency. Ascending and descending statements are supported; equal-date order is resolved using balance evidence. Non-monotonic dates and invalid-row gaps are not silently reordered or bridged. Tolerance is one cent. No opening balance is inferred. Response includes tested/matched/failed counts, maximum difference, affected rows, direction and confidence. Two or more clean matches can be high confidence. Missing rows/balances lower confidence. Better matches with inverted movements flag a probable sign error; no automatic sign reversal occurs.
5. Duplicate check, then server-owned review and transactional confirmation. The existing transaction model and analytics remain unchanged.

Canonical provenance retains a pseudonymous account label, booking date, optional transaction timestamp, description/original description, signed amount, CREDIT/DEBIT direction, fee magnitude, optional reported balance, currency, source categories, source row/file/batch, review status and optional hashed source transaction reference. `transaction_type` is the existing semantic income/expense/transfer field. Invalid or unknown explicit classifications require review and cannot be silently persisted. Provenance uses existing batch JSON storage, expires with the anonymous session, and requires no database migration. Raw source account identifiers are not returned in previews or account labels; no financial rows are added to application logging.

## Amount models

| Source | Interpretation |
|---|---|
| Amount | Signed total; user can reverse the sign convention. A Fee column is provenance and is **not added**. |
| Debit / Credit / optional Fee | Positive magnitudes: credit − debit − fee. |
| Money In / Money Out / optional Fee | Signed columns: money in + money out + fee. Fee-only rows are valid expenses. |
| Positive Money Out export | Suggested as the positive-magnitude Debit/Credit model; the user can edit it. |

Both debit and credit populated on one row, conflicting signs, invalid dates, invalid grouping, more than two decimal places and missing/zero movements produce source-row errors. Recognized balance summaries, repeated headers, blanks and metadata without a date/movement are skipped. Summary recognition is deliberately conservative; unfamiliar malformed rows remain visible issues.

Direction is independent of semantics. Explicit Transfer/Internal Transfer/Transfer In/Transfer Out source categories or parent categories produce transfers. A generic Credit/Debit source type does not override that evidence. Explicit type or row overrides remain reviewable. Otherwise direction supplies the initial income/expense suggestion. FinTrack does not infer transfers from merchant descriptions or identify both legs automatically.

## Duplicate limits

Within a session, fingerprints use account, booking date/time, normalized description, signed amount, currency, and reported balance/source reference when present. Source `Nr` is not treated as a unique bank reference. Semantic edits do not change identity. Different balances distinguish identical same-day purchases. Without balance/reference evidence, repeated purchases within one statement are retained using occurrence counts; matching occurrences in another upload are shown as **possible duplicates** and skipped. Overlapping exports without identifiers remain inherently ambiguous. Correct source/mapping or import a non-overlapping export when the evidence is insufficient; no automatic historical deletion occurs. Old sessions imported before this fingerprint upgrade should be restarted before re-uploading the same files (sessions expire within 24 hours).

## Reproducible synthetic evidence

Generate fixtures with `python tests/fixtures/generate_bank_formats.py` from `backend`. All six formats encode the same seven-movement ledger so differences isolate parsing rather than financial behaviour.

| Fixture | Format | Valid rows | Credits | Debits (including fees) | Fees | Transfer in / out | Net movement | Ending reported balance |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| bank_signed.csv | Signed Amount + Fee + Balance | 7 | 3200.00 | 953.00 | 3.00 | 200.00 / 400.00 | 2247.00 | 3247.00 |
| bank_debit_credit.csv | Positive Debit/Credit/Fee | 7 | 3200.00 | 953.00 | 3.00 | 200.00 / 400.00 | 2247.00 | 3247.00 |
| bank_money.csv | Signed Money In/Out/Fee | 7 | 3200.00 | 953.00 | 3.00 | 200.00 / 400.00 | 2247.00 | 3247.00 |
| bank_reference.csv | Full reference structure + one malformed row | 7 | 3200.00 | 953.00 | 3.00 | 200.00 / 400.00 | 2247.00 | 3247.00 |
| bank_european.csv | Semicolon, decimal comma, metadata | 7 | 3200.00 | 953.00 | 3.00 | 200.00 / 400.00 | 2247.00 | 3247.00 |
| bank_tab.csv | Tab-delimited reference structure | 7 | 3200.00 | 953.00 | 3.00 | 200.00 / 400.00 | 2247.00 | 3247.00 |

Independent arithmetic: credits = 3000 + 200; debits = 500 + 3 + 400 + 25 + 25. The fixture's specified initial 1000 plus net movement 2247 equals final 3247; the importer itself does not infer that initial balance. All six adjacent balance transitions match. Reference file source row 10 has no monetary movement and is rejected. Analytics exclude transfers: income 3000, expenses 553, net cash flow 2447, savings rate 81.57%. Posting date puts the salary in August even though its transaction date is July 31.

Run `python -m unittest discover -s tests -p "test_*.py"`; frontend verification is `npm run build` and `npx eslint src/pages/UploadPage.jsx`. Local launch remains documented in [PUBLIC_DEMO.md](PUBLIC_DEMO.md).

## Deliberate limits

This is an explainable reviewed importer, not universal ETL. No OCR, automatic transfer matching, FX conversion, balance/net-worth inference or bank-specific integrations. Ambiguous date/sign conventions and unfamiliar source categories need human review. Excel account identifiers should be stored as text: zeros already lost by the spreadsheet cannot be recovered. Reconciliation proves internal consistency of comparable rows, not that an export is complete or authentic. Public demo remains for synthetic/anonymised data.
