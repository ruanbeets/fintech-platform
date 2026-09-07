from decimal import Decimal as D
from support import DatabaseCase
from scripts.seed_demo import seed_demo, DEMO_USER_ID


class TrendsApiTests(DatabaseCase):
    def setUp(self):
        super().setUp()
        with self.sessions.begin() as db:
            seed_demo(db)

    def test_demo_and_real_api_share_trends_contract(self):
        demo = self.client.get("/dashboard/demo?month=2026-08").json()["trends"]
        real = self.client.get(f"/dashboard/{DEMO_USER_ID}?month=2026-08").json()["trends"]
        self.assertEqual(demo, real)
        self.assertEqual(len(demo["savings"]["history"]), 12)
        self.assertEqual(demo["observed_through"], "2026-08-31")

    def test_independent_august_category_and_savings_figures(self):
        trends = self.client.get("/dashboard/demo?month=2026-08").json()["trends"]
        groceries = next(c for c in trends["categories"] if c["category"] == "Groceries")
        # Four grocery transactions each month, independently itemized.
        august = sum(map(D, ["969.45", "1032.45", "780.45", "843.45"]))
        july = sum(map(D, ["906.45", "969.45", "1032.45", "780.45"]))
        self.assertEqual(D(groceries["current_spend"]), august)
        self.assertEqual(D(groceries["previous_spend"]), july)
        self.assertEqual(groceries["change"]["absolute_change"], "-63.00")
        self.assertEqual(groceries["change"]["percentage_change"], "-1.71")
        self.assertEqual(trends["savings"]["current"], "45.68")
        self.assertEqual(trends["savings"]["previous_valid"]["savings_rate"], "42.95")
        self.assertEqual(trends["savings"]["change_percentage_points"], "2.73")

    def test_recurring_rent_and_partition_reconcile_to_transactions(self):
        response = self.client.get("/dashboard/demo?month=2026-08").json()
        trends = response["trends"]
        rent = next(r for r in trends["recurring"] if r["normalized_name"] == "monthly rent")
        self.assertEqual(rent["typical_amount"], "11850.00")
        self.assertEqual(rent["frequency"], "monthly")
        self.assertEqual(rent["occurrence_count"], 11)
        self.assertEqual(rent["expected_next_occurrence"], "2026-09-01")
        classes = {c["classification"]: D(c["amount"]) for c in trends["spending"]["classes"]}
        self.assertEqual(sum(classes.values()), D(response["selected"]["expenses"]))
        # Fixed: rent + insurance + fibre. Variable: groceries + transport + utilities + dining + health.
        self.assertEqual(classes["fixed_recurring"], sum(map(D, ["11850", "890.50", "749"])))
        self.assertEqual(classes["variable"], sum(map(D, ["3625.80", "1910", "1635", "1445", "710"])))
        self.assertEqual(classes["unclassified"], D("0"))

    def test_missing_month_keeps_expenses_zero_and_rates_unavailable(self):
        trends = self.client.get("/dashboard/demo?month=2025-11").json()["trends"]
        self.assertIsNone(trends["savings"]["current"])
        self.assertIsNone(trends["savings"]["change_percentage_points"])
        self.assertEqual(trends["savings"]["previous_valid"]["month"], "2025-10")
        self.assertEqual(trends["spending"]["total_expenses"], "0.00")
        self.assertTrue(all(c["share"] is None for c in trends["spending"]["classes"]))
