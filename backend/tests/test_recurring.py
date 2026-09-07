import unittest
from datetime import date, timedelta
from decimal import Decimal as D
from types import SimpleNamespace as Row
from app.services.recurring import detect_recurring, normalize_name


class RecurringTests(unittest.TestCase):
    def rows(self, dates, amounts=None, kind="expense", names=None):
        amounts = amounts or ["100"] * len(dates)
        names = names or ["Gym club"] * len(dates)
        return [(Row(account_id="a", type=kind, category="Gym", merchant=names[i], description=None), d, D(amounts[i]))
                for i, d in enumerate(dates)]

    def test_true_monthly_expense_and_next_date(self):
        dates = [date(2026, m, 5) for m in range(3, 9)]
        result, _ = detect_recurring(self.rows(dates), cutoff=date(2026, 8, 31))
        self.assertEqual(len(result), 1)
        item = result[0]
        self.assertEqual((item["frequency"], item["strength"], item["occurrence_count"]), ("monthly", "strong", 6))
        self.assertEqual(item["typical_amount"], D("100"))
        self.assertEqual(item["expected_next_occurrence"], "2026-09-05")
        self.assertEqual((item["first_observed"], item["most_recent"]), ("2026-03-05", "2026-08-05"))

    def test_amount_variation_within_tolerance_and_salary(self):
        dates = [date(2026, m, 25) for m in range(3, 9)]
        result, _ = detect_recurring(self.rows(dates, ["100", "102", "98", "101", "99", "100"], kind="income"), cutoff=date(2026, 8, 31))
        self.assertEqual(result[0]["transaction_type"], "income")
        self.assertEqual(result[0]["typical_amount"], D("100"))

    def test_insufficient_history_and_weak_evidence(self):
        result, _ = detect_recurring(self.rows([date(2026, 7, 5), date(2026, 8, 5)]), cutoff=date(2026, 8, 31))
        self.assertEqual(result, [])
        result, _ = detect_recurring(self.rows([date(2026, m, 5) for m in [6, 7, 8]]), cutoff=date(2026, 8, 31))
        self.assertEqual(result[0]["strength"], "likely")
        self.assertIsNone(result[0]["expected_next_occurrence"])

    def test_irregular_intervals_not_recurring(self):
        dates = [date(2026, 1, 3), date(2026, 2, 19), date(2026, 4, 1), date(2026, 7, 25)]
        self.assertEqual(detect_recurring(self.rows(dates), cutoff=date(2026, 8, 31))[0], [])

    def test_irregular_amounts_not_recurring(self):
        dates = [date(2026, m, 5) for m in range(3, 9)]
        self.assertEqual(detect_recurring(self.rows(dates, ["10", "100", "250", "20", "500", "90"]), cutoff=date(2026, 8, 31))[0], [])

    def test_description_normalization_and_fallback(self):
        self.assertEqual(normalize_name("GYM Club - REF:123456 2026-08-05"), "gym club")
        dates = [date(2026, m, 5) for m in [6, 7, 8]]
        rows = self.rows(dates, names=["Gym CLUB", "gym-club", "GYM Club REF:123456"])
        rows[0][0].description, rows[0][0].merchant = "Gym CLUB", None
        result, _ = detect_recurring(rows, cutoff=date(2026, 8, 31))
        self.assertEqual(result[0]["normalized_name"], "gym club")

    def test_missing_month_allowed_without_inventing_occurrences(self):
        dates = [date(2026, m, 5) for m in [2, 3, 4, 6, 7, 8]]
        result, _ = detect_recurring(self.rows(dates), cutoff=date(2026, 8, 31))
        self.assertEqual(result[0]["occurrence_count"], 6)

    def test_stale_series_has_no_fabricated_next_date(self):
        dates = [date(2026, m, 5) for m in range(1, 7)]
        result, _ = detect_recurring(self.rows(dates), cutoff=date(2026, 8, 31))
        self.assertIsNone(result[0]["expected_next_occurrence"])

    def test_types_and_accounts_are_not_merged(self):
        rows = self.rows([date(2026, m, 5) for m in [6, 7, 8]])
        rows[0][0].type = "transfer"
        rows[1][0].account_id = "b"
        self.assertEqual(detect_recurring(rows, cutoff=date(2026, 8, 31))[0], [])

    def test_weekly_and_month_end_cadences(self):
        rows = self.rows([date(2026, 7, 1) + timedelta(days=7 * i) for i in range(8)])
        result, _ = detect_recurring(rows, cutoff=date(2026, 8, 31))
        self.assertEqual(result[0]["frequency"], "weekly")
        rows = self.rows([date(2026, 1, 31), date(2026, 2, 28), date(2026, 3, 31)])
        self.assertEqual(detect_recurring(rows, cutoff=date(2026, 3, 31))[0][0]["frequency"], "monthly")

    def test_duplicate_same_day_does_not_inflate_monthly_evidence(self):
        dates = [date(2026, 8, 5)] * 6
        self.assertEqual(detect_recurring(self.rows(dates), cutoff=date(2026, 8, 31))[0], [])
