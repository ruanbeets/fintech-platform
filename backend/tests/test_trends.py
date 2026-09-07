import unittest
from datetime import date, datetime
from decimal import Decimal as D
from types import SimpleNamespace as Row
from app.services.financial_analytics import calculate_overview


class TrendsTests(unittest.TestCase):
    def row(self, amount, kind="expense", month="2026-08", category="Groceries", merchant="Shop", account="a", user="u"):
        return Row(amount=D(amount), type=kind, occurred_at=datetime.fromisoformat(month + "-15T12:00:00"),
                   user_id=user, account_id=account, category=category, merchant=merchant, description=None)

    def result(self, rows, month="2026-08", currency="ZAR", as_of=date(2026, 9, 6)):
        accounts = [Row(id="a", user_id="u", currency="ZAR", name="Local"),
                    Row(id="b", user_id="u", currency="USD", name="Dollar"),
                    Row(id="c", user_id="other", currency="ZAR", name="Other")]
        return calculate_overview(accounts, rows, user_id="u", as_of=as_of, selected_month=month, currency=currency)

    def test_category_change_averages_share_and_twelve_months(self):
        rows = [self.row("100", month=f"2026-{m:02}") for m in range(3, 8)]
        rows += [self.row("150"), self.row("50", category="Dining")]
        category = self.result(rows).trends.categories[0]
        self.assertEqual(category.category, "Groceries")
        self.assertEqual((category.current_spend, category.previous_spend, category.change.absolute_change, category.change.percentage_change),
                         (D("150"), D("100"), D("50"), D("50")))
        self.assertEqual((category.trailing_3_month_average, category.trailing_6_month_average), (D("116.67"), D("108.33")))
        self.assertEqual(category.share_of_expenses, D("75"))
        self.assertEqual(len(category.history), 12)

    def test_zero_baseline_missing_and_uncategorised(self):
        result = self.result([self.row("50", category="   "), self.row("10", category=None, month="2026-06")]).trends.categories[0]
        self.assertEqual(result.category, "Uncategorised")
        self.assertEqual(result.previous_spend, D("0"))
        self.assertIsNone(result.change.percentage_change)
        self.assertEqual(result.change.coverage, "no_recorded_activity")
        self.assertEqual(result.history[-2].spend, D("0"))
        self.assertEqual(result.trailing_3_month_average, D("20"))

    def test_category_isolation_currency_users_and_transfers(self):
        rows = [self.row("20"), self.row("30", category="Dining"), self.row("999", kind="transfer"),
                self.row("888", account="b"), self.row("777", account="c", user="other"),
                self.row("666", account="c")]
        result = self.result(rows).trends
        self.assertEqual({c.category: c.current_spend for c in result.categories}, {"Groceries": D("20"), "Dining": D("30")})
        self.assertEqual(self.result(rows, currency="USD").trends.categories[0].current_spend, D("888"))
        self.assertEqual(result.spending.total_expenses, D("50"))

    def test_savings_means_exclude_unavailable_and_change_is_points(self):
        rows = [self.row("100", "income", "2026-06"), self.row("20", month="2026-06"),
                self.row("50", month="2026-07"), self.row("200", "income"), self.row("100")]
        savings = self.result(rows).trends.savings
        self.assertEqual(savings.current, D("50"))
        self.assertEqual(savings.previous_valid.month, "2026-06")
        self.assertEqual(savings.change_percentage_points, D("-30"))
        self.assertEqual(savings.trailing_3_month_average.value, D("65"))
        self.assertEqual(savings.trailing_6_month_average.value, D("65"))
        self.assertEqual(savings.trailing_3_month_average.valid_months, 2)
        self.assertIsNone(savings.history[-2].savings_rate)

    def test_current_zero_income_rate_and_change_unavailable(self):
        savings = self.result([self.row("100", "income", "2026-07"), self.row("20")]).trends.savings
        self.assertIsNone(savings.current)
        self.assertIsNone(savings.change_percentage_points)
        self.assertEqual(savings.trailing_3_month_average.value, D("100"))

    def test_previous_valid_month_can_precede_displayed_window(self):
        savings = self.result([self.row("100", "income", "2024-01"), self.row("100", "income")]).trends.savings
        self.assertEqual(savings.previous_valid.month, "2024-01")
        self.assertEqual(savings.change_percentage_points, D("0"))

    def test_income_comparisons_average_extremes_and_missing_coverage(self):
        rows = [self.row("100", "income", "2025-09"), self.row("200", "income", "2026-07"), self.row("300", "income")]
        result = self.result(rows).trends.income
        self.assertEqual(result.previous_month.absolute_change, D("100"))
        self.assertEqual(result.previous_month.percentage_change, D("50"))
        self.assertEqual(result.average_12_month, D("50"))
        self.assertEqual(result.recorded_months, 3)
        self.assertEqual(result.highest_month.month, "2026-08")
        self.assertEqual(result.lowest_month.month, "2025-09")
        self.assertEqual(result.versus_3_month_average.baseline, D("166.67"))

    def test_partial_month_not_used_for_income_extremes(self):
        rows = [self.row("100", "income", "2026-07"), self.row("999", "income")]
        result = self.result(rows, as_of=date(2026, 8, 31)).trends.income
        self.assertEqual(result.highest_month.month, "2026-07")

    def test_empty_data_and_unavailable_shares(self):
        result = self.result([]).trends
        self.assertEqual(result.categories, [])
        self.assertEqual(result.recurring, [])
        self.assertIsNone(result.income.highest_month)
        self.assertIsNone(result.savings.trailing_6_month_average.value)
        self.assertTrue(all(c.share is None for c in result.spending.classes))

    def test_fixed_variable_unclassified_reconcile(self):
        rows = [self.row("1000", month=f"2026-{m:02}", category="Housing", merchant="Rent") for m in range(3, 9)]
        rows += [self.row("100", category="Groceries"), self.row("70", category=None, merchant=None),
                 self.row("50", category="Travel"), self.row("999", kind="transfer", category="Savings")]
        spending = self.result(rows).trends.spending
        amounts = {c.classification: c.amount for c in spending.classes}
        self.assertEqual(amounts, {"fixed_recurring": D("1000"), "variable": D("150"), "unclassified": D("70")})
        self.assertEqual(sum(amounts.values()), spending.total_expenses)
        self.assertEqual(spending.total_expenses, D("1220"))

    def test_no_future_leakage_in_historical_classification(self):
        rows = [self.row("1000", month=f"2026-{m:02}", category="Housing", merchant="Rent") for m in range(3, 9)]
        result = self.result(rows, month="2026-04").trends
        self.assertEqual(result.recurring, [])
        self.assertEqual(result.spending.classes[0].amount, D("0"))

    def test_variable_categories_stay_variable_even_if_repeated(self):
        rows = [self.row("100", month=f"2026-{m:02}") for m in range(3, 9)]
        result = self.result(rows).trends
        self.assertEqual(len(result.recurring), 1)
        self.assertEqual(result.spending.classes[0].amount, D("0"))
        self.assertEqual(result.spending.classes[1].amount, D("100"))
