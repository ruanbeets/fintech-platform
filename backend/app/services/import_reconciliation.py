"""Check reported balances against adjacent movements, never infer an opening balance."""
from collections import defaultdict
from decimal import Decimal
from app.schemas.imports import Reconciliation


def reconcile(results):
    groups = defaultdict(list)
    skipped = [r.source_row for r in results if r.status in {"invalid", "excluded"}]
    for item in results:
        if item.transaction is not None and item.status != "duplicate":
            groups[(item.transaction.account, item.transaction.currency)].append(item.transaction)
    checks, reverse_checks, orders = [], [], set()
    for rows in groups.values():
        ascending = all(a.date <= b.date for a, b in zip(rows, rows[1:]))
        descending = all(a.date >= b.date for a, b in zip(rows, rows[1:]))
        if not ascending and not descending:
            skipped.extend(r.source_row for r in rows)
            continue
        candidates = []
        for order in (["ascending"] if ascending and not descending else ["descending"] if descending and not ascending else ["ascending", "descending"]):
            ordered = rows if order == "ascending" else list(reversed(rows))
            tested = []
            for previous, current in zip(ordered, ordered[1:]):
                low, high = sorted([previous.source_row, current.source_row])
                if any(low < n < high for n in skipped) or previous.balance_optional is None or current.balance_optional is None:
                    continue
                difference = current.balance_optional - previous.balance_optional
                tested.append((current.source_row, abs(difference - current.signed_amount), abs(difference + current.signed_amount)))
            candidates.append((sum(d <= Decimal("0.01") for _, d, _ in tested), order, tested))
        _, order, tested = max(candidates, key=lambda c: c[0])
        if tested:
            orders.add(order)
        checks.extend((n, d) for n, d, _ in tested)
        reverse_checks.extend(d for _, _, d in tested)
    if not checks:
        return Reconciliation(skipped_rows=sorted(set(skipped)))
    matched = sum(d <= Decimal("0.01") for _, d in checks)
    failed = [n for n, d in checks if d > Decimal("0.01")]
    missing_balance = any(r.transaction and r.transaction.balance_optional is None for r in results)
    status = "FAILED" if not matched else "PARTIAL" if failed or skipped or missing_balance else "RECONCILED"
    return Reconciliation(status=status, rows_tested=len(checks), rows_matched=matched,
        rows_failed=len(failed), maximum_difference=max(d for _, d in checks), failed_rows=failed,
        skipped_rows=sorted(set(skipped)), probable_sign_error=sum(d <= Decimal("0.01") for d in reverse_checks) > max(matched, 1),
        confidence="high" if len(checks) >= 2 and not failed and not skipped and not missing_balance else "medium" if matched else "low",
        order=next(iter(orders)) if len(orders) == 1 else "unknown")
