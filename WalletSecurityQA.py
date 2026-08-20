import unittest
import threading

from DigitalWallet import DigitalWallet


class WalletSecurityQA(unittest.TestCase):

    # --------------------------------------------------
    # Setup
    # --------------------------------------------------

    def setUp(self):

        self.wallet = DigitalWallet()

        result, message = self.wallet.create_account(
            "A1",
            "Test User",
            "1234",
            10000
        )

        self.assertTrue(result)

    # --------------------------------------------------
    # 1. Normal Transaction
    # --------------------------------------------------

    def test_normal_transaction(self):

        result, message = self.wallet.withdraw(
            "A1",
            500,
            "1234"
        )

        self.assertTrue(result)
        self.assertEqual(
            self.wallet.get_balance("A1"),
            9500
        )

    # --------------------------------------------------
    # 2. Insufficient Balance
    # --------------------------------------------------

    def test_insufficient_balance(self):

        result, message = self.wallet.withdraw(
            "A1",
            20000,
            "1234"
        )

        self.assertFalse(result)
        self.assertEqual(
            message,
            "Insufficient balance"
        )

    # --------------------------------------------------
    # 3. Daily Transaction Limit
    # --------------------------------------------------

    def test_daily_limit(self):

        result, message = self.wallet.withdraw(
            "A1",
            10001,
            "1234"
        )

        self.assertFalse(result)
        self.assertEqual(
            message,
            "Daily transaction limit exceeded"
        )

    # --------------------------------------------------
    # 4. Multiple Failed PIN Attempts
    # --------------------------------------------------

    def test_multiple_failed_pins(self):

        self.wallet.withdraw(
            "A1",
            100,
            "1111"
        )

        self.wallet.withdraw(
            "A1",
            100,
            "2222"
        )

        self.wallet.withdraw(
            "A1",
            100,
            "3333"
        )

        account = self.wallet.accounts["A1"]

        self.assertEqual(
            account["failed_pins"],
            3
        )

        fraud, reasons = self.wallet.check_fraud(
            "A1",
            100
        )

        self.assertTrue(fraud)

        self.assertIn(
            "Multiple failed PIN attempts",
            reasons
        )

    # --------------------------------------------------
    # 5. Suspicious / Large Transaction
    # --------------------------------------------------

    def test_suspicious_transaction(self):

        result, message = self.wallet.withdraw(
            "A1",
            6000,
            "1234"
        )

        self.assertTrue(result)

        self.assertIn(
            "SUSPICIOUS",
            message
        )

    # --------------------------------------------------
    # 6. Duplicate Transaction
    # --------------------------------------------------

    def test_duplicate_transaction(self):

        result1, message1 = self.wallet.withdraw(
            "A1",
            500,
            "1234"
        )

        result2, message2 = self.wallet.withdraw(
            "A1",
            500,
            "1234"
        )

        self.assertTrue(result1)
        self.assertTrue(result2)

        history = self.wallet.get_transaction_history("A1")

        withdrawal_amounts = [
            transaction["amount"]
            for transaction in history
            if transaction["type"] == "withdrawal"
        ]

        self.assertEqual(
            withdrawal_amounts.count(500),
            2
        )

    # --------------------------------------------------
    # 7. Negative Amount
    # --------------------------------------------------

    def test_negative_amount(self):

        result, message = self.wallet.deposit(
            "A1",
            -100,
            "1234"
        )

        self.assertFalse(result)

        self.assertEqual(
            message,
            "Negative/invalid amount"
        )

    # --------------------------------------------------
    # 8. Concurrent Transactions
    # --------------------------------------------------

    def test_concurrent_transactions(self):

        results = []

        def transaction():

            result, message = self.wallet.withdraw(
                "A1",
                100,
                "1234"
            )

            results.append((result, message))

        threads = []

        for i in range(5):

            thread = threading.Thread(
                target=transaction
            )

            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All 5 transactions should complete
        self.assertEqual(
            len(results),
            5
        )

        # All transactions should succeed
        for result, message in results:
            self.assertTrue(result)

        # Balance should be 9500
        self.assertEqual(
            self.wallet.get_balance("A1"),
            9500
        )

    # --------------------------------------------------
    # 9. More Than 5 Transactions in 10 Minutes
    # --------------------------------------------------

    def test_more_than_five_transactions(self):

        for i in range(5):

            result, message = self.wallet.withdraw(
                "A1",
                100,
                "1234"
            )

            self.assertTrue(result)

        # 6th transaction should be flagged
        result, message = self.wallet.withdraw(
            "A1",
            100,
            "1234"
        )

        self.assertTrue(result)

        self.assertIn(
            "SUSPICIOUS",
            message
        )

        self.assertIn(
            "More than 5 transactions in 10 minutes",
            message
        )

    # --------------------------------------------------
    # 10. Money Transfer
    # --------------------------------------------------

    def test_money_transfer(self):

        result, message = self.wallet.create_account(
            "A2",
            "Receiver",
            "5678",
            5000
        )

        self.assertTrue(result)

        result, message = self.wallet.transfer(
            "A1",
            "A2",
            2000,
            "1234"
        )

        self.assertTrue(result)

        self.assertEqual(
            self.wallet.get_balance("A1"),
            8000
        )

        self.assertEqual(
            self.wallet.get_balance("A2"),
            7000
        )

    # --------------------------------------------------
    # 11. Account Creation
    # --------------------------------------------------

    def test_duplicate_account(self):

        result, message = self.wallet.create_account(
            "A1",
            "Another User",
            "5678",
            5000
        )

        self.assertFalse(result)

        self.assertEqual(
            message,
            "Account already exists"
        )

    # --------------------------------------------------
    # 12. Balance Verification
    # --------------------------------------------------

    def test_balance_verification(self):

        self.assertEqual(
            self.wallet.get_balance("A1"),
            10000
        )

        self.wallet.deposit(
            "A1",
            1000,
            "1234"
        )

        self.assertEqual(
            self.wallet.get_balance("A1"),
            11000
        )


# ------------------------------------------------------
# Run Tests
# ------------------------------------------------------

if __name__ == "__main__":

    print("========================================")
    print("       DIGITAL WALLET SECURITY QA")
    print("========================================")

    unittest.main(verbosity=2)
