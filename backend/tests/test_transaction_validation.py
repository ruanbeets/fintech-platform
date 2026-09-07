from decimal import Decimal
from support import DatabaseCase


class TransactionValidationTests(DatabaseCase):
    def setUp(self):
        super().setUp()
        self.user, self.account = self.user_account()
        self.payload = dict(user_id=str(self.user), account_id=str(self.account), amount="10.25",
                            type="income", occurred_at="2026-08-01T01:00:00+02:00")

    def test_valid_decimal_and_utc_normalization_round_trip(self):
        response = self.client.post("/transactions/", json=self.payload)
        self.assertEqual(response.status_code, 200, response.text)
        created = response.json()
        self.assertEqual(Decimal(str(created["amount"])), Decimal("10.25"))
        self.assertEqual(created["occurred_at"], "2026-07-31T23:00:00")
        tx_id = created["id"]
        update = self.client.put(f"/transactions/{tx_id}", json={"amount": "20.30"})
        self.assertEqual(update.status_code, 200, update.text)
        self.assertEqual(Decimal(str(update.json()["amount"])), Decimal("20.30"))
        self.assertEqual(self.client.get(f"/transactions/single/{tx_id}").status_code, 200)
        self.assertEqual(len(self.client.get(f"/transactions/{self.user}").json()), 1)
        self.assertEqual(self.client.delete(f"/transactions/{tx_id}").status_code, 200)

    def test_invalid_amounts_on_create_and_update(self):
        tx_id = self.client.post("/transactions/", json=self.payload).json()["id"]
        for amount in ["0", "-0.01", "NaN", "Infinity", "-Infinity", "1.001", "1000000000000", None, True, "invalid"]:
            with self.subTest(amount=amount):
                self.assertEqual(self.client.post("/transactions/", json={**self.payload, "amount": amount}).status_code, 422)
                self.assertEqual(self.client.put(f"/transactions/{tx_id}", json={"amount": amount}).status_code, 422)

    def test_account_must_belong_to_transaction_user(self):
        other, _ = self.user_account()
        response = self.client.post("/transactions/", json={**self.payload, "user_id": str(other)})
        self.assertEqual(response.status_code, 400)

    def test_update_cannot_reassign_owner_or_null_required_values(self):
        tx_id = self.client.post("/transactions/", json=self.payload).json()["id"]
        for update in [{"user_id": str(self.user)}, {"account_id": str(self.account)}, {"type": None},
                       {"occurred_at": None}, {"occurred_at": "bad"}, {"type": "refund"}]:
            with self.subTest(update=update):
                self.assertEqual(self.client.put(f"/transactions/{tx_id}", json=update).status_code, 422)
