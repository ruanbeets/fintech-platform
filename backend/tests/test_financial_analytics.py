import unittest
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal as D
from types import SimpleNamespace as Row
from app.services.financial_analytics import calculate_overview


class FinancialAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.accounts = [Row(id="a", user_id="u", currency="ZAR", name="Everyday")]

    def tx(self, amount, kind="income", month="2026-08", **kwargs):
        return Row(amount=D(amount), type=kind, occurred_at=datetime.fromisoformat(month + "-15T12:00:00"),
                   user_id=kwargs.get("user_id", "u"), account_id=kwargs.get("account_id", "a"))

    def overview(self, txs, month="2026-08", **kwargs):
        return calculate_overview(self.accounts, txs, user_id="u", as_of=date(2026, 9, 6),
                                  selected_month=month, **kwargs)

    def test_decimal_income_expenses_net_and_rate(self):
        result = self.overview([self.tx("0.10"), self.tx("0.20"), self.tx("0.10", "expense")]).selected
        self.assertEqual((result.income, result.expenses, result.net_cash_flow, result.savings_rate),
                         (D("0.30"), D("0.10"), D("0.20"), D("66.67")))

    def test_transfers_do_not_change_financial_metrics(self):
        result = self.overview([self.tx("100"), self.tx("20", "expense"), self.tx("9999", "transfer")]).selected
        self.assertEqual((result.income, result.expenses, result.net_cash_flow, result.savings_rate),
                         (D("100"), D("20"), D("80"), D("80")))
        self.assertEqual(result.transaction_count, 3)

    def test_zero_income_and_negative_net(self):
        result = self.overview([self.tx("50.25", "expense")]).selected
        self.assertEqual(result.net_cash_flow, D("-50.25"))
        self.assertIsNone(result.savings_rate)

    def test_negative_savings_rate_is_preserved(self):
        self.assertEqual(self.overview([self.tx("100"), self.tx("150", "expense")]).selected.savings_rate, D("-50"))

    def test_missing_month_is_zero_recorded_activity(self):
        result = self.overview([self.tx("100", month="2026-06"), self.tx("200")], "2026-07").selected
        self.assertEqual((result.income, result.expenses, result.net_cash_flow), (D("0"), D("0"), D("0")))
        self.assertIsNone(result.savings_rate)
        self.assertEqual(result.coverage, "no_recorded_activity")

    def test_twelve_month_history_and_year_boundary(self):
        result = self.overview([self.tx("10", month="2025-12"), self.tx("20", month="2026-01")], "2026-01")
        self.assertEqual(len(result.history), 12)
        self.assertEqual(result.history[0].month, "2025-02")
        self.assertEqual(result.history[-2].income, D("10"))
        self.assertEqual(result.history[-1].income, D("20"))

    def test_three_and_six_month_windows_include_zero_gap(self):
        txs = [self.tx(str(n * 100), month=f"2026-{n:02}") for n in [3, 4, 5, 6, 8]]
        result = self.overview(txs).selected
        self.assertEqual(result.trailing_3_month.income, D("466.67"))
        self.assertEqual(result.trailing_6_month.income, D("433.33"))
        self.assertEqual(result.trailing_3_month.recorded_months, 2)
        self.assertEqual(result.trailing_6_month.recorded_months, 5)

    def test_rolling_expenses_net_and_weighted_rate(self):
        txs = [self.tx("100", month="2026-06"), self.tx("50", "expense", "2026-06"),
               self.tx("300", month="2026-07"), self.tx("200", "expense", "2026-07"),
               self.tx("500"), self.tx("200", "expense")]
        result = self.overview(txs).selected.trailing_3_month
        self.assertEqual((result.income, result.expenses, result.net_cash_flow, result.savings_rate),
                         (D("300"), D("150"), D("150"), D("50")))

    def test_short_history_and_empty_data_are_explicit(self):
        result = self.overview([self.tx("100")]).selected.trailing_3_month
        self.assertEqual(result.status, "insufficient_history")
        self.assertIsNone(result.income)
        empty = self.overview([])
        self.assertEqual(len(empty.history), 12)
        self.assertIsNone(empty.selected.savings_rate)
        self.assertIsNone(empty.selected.trailing_6_month.net_cash_flow)

    def test_user_and_currency_isolation(self):
        self.accounts += [Row(id="b", user_id="other", currency="ZAR", name="Other"),
                          Row(id="c", user_id="u", currency="USD", name="Dollar")]
        txs = [self.tx("10"), self.tx("1000", user_id="other", account_id="b"),
               self.tx("777", account_id="b"), self.tx("30", account_id="c")]
        self.assertEqual(self.overview(txs, currency="ZAR").selected.income, D("10"))
        self.assertEqual(self.overview(txs, currency="USD").selected.income, D("30"))
        self.assertEqual(len(self.overview(txs, currency="USD").account_balances), 1)
        with self.assertRaises(ValueError):
            self.overview(txs, currency="EUR")

    def test_balances_and_net_worth_never_inferred(self):
        result = self.overview([self.tx("900000")])
        self.assertIsNone(result.account_balances[0].value)
        self.assertEqual(result.account_balances[0].status, "unavailable")
        self.assertIsNone(result.net_worth.value)
        self.assertEqual(result.net_worth.status, "unavailable")

    def test_current_month_is_partial_and_future_activity_excluded(self):
        tx = self.tx("20", month="2026-09")
        tx.occurred_at = datetime(2026, 9, 1)
        result = self.overview([tx, self.tx("999", month="2026-09")], "2026-09")
        self.assertTrue(result.selected.partial_month)
        self.assertEqual(result.selected.income, D("20"))

    def test_utc_boundary(self):
        tx = self.tx("10")
        tx.occurred_at = datetime(2026, 8, 1, 1, tzinfo=timezone(timedelta(hours=2)))
        self.assertEqual(self.overview([tx], "2026-07").selected.income, D("10"))

    def test_invalid_recorded_amounts_fail_clearly(self):
        for amount in ["0", "-1", "NaN", "Infinity"]:
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                self.overview([self.tx(amount)])

    def test_future_month_rejected(self):
        with self.assertRaises(ValueError):
            self.overview([], "2027-01")
