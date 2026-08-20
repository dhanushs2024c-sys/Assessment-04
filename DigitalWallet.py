from datetime import datetime, timedelta
import threading


class DigitalWallet:

    DAILY_LIMIT = 10000.0
    LARGE_TRANSACTION = 5000.0
    MAX_TRANSACTIONS_10_MIN = 5
    MAX_FAILED_PINS = 3

    def __init__(self):
        self.accounts = {}
        self.lock = threading.Lock()

    # Account Creation
    def create_account(self, account_id, name, pin, initial_balance=0):

        if account_id in self.accounts:
            return False, "Account already exists"

        if initial_balance < 0:
            return False, "Invalid initial balance"

        if not str(pin).isdigit() or len(str(pin)) != 4:
            return False, "PIN must contain 4 digits"

        self.accounts[account_id] = {
            "name": name,
            "pin": str(pin),
            "balance": float(initial_balance),
            "transactions": [],
            "failed_pins": 0
        }

        return True, "Account created successfully"

    # PIN Verification
    def verify_pin(self, account_id, pin):

        if account_id not in self.accounts:
            return False

        account = self.accounts[account_id]

        if str(pin) == account["pin"]:
            account["failed_pins"] = 0
            return True

        account["failed_pins"] += 1
        return False

    # Daily Transaction Total
    def get_daily_total(self, account_id):

        account = self.accounts[account_id]
        today = datetime.now().date()

        total = 0

        for transaction in account["transactions"]:

            if transaction["time"].date() == today:

                if transaction["type"] in [
                    "deposit",
                    "withdrawal",
                    "transfer"
                ]:
                    total += transaction["amount"]

        return total

    # Fraud Detection
    def check_fraud(self, account_id, amount):

        if account_id not in self.accounts:
            return True, ["Invalid account"]

        account = self.accounts[account_id]
        reasons = []

        current_time = datetime.now()

        recent_transactions = []

        for transaction in account["transactions"]:

            if current_time - transaction["time"] <= timedelta(minutes=10):
                recent_transactions.append(transaction)

        # More than 5 transactions in 10 minutes
        if len(recent_transactions) >= 5:
            reasons.append(
                "More than 5 transactions in 10 minutes"
            )

        # Large transaction
        if amount >= self.LARGE_TRANSACTION:
            reasons.append("Large transaction")

        # Multiple failed PIN attempts
        if account["failed_pins"] >= self.MAX_FAILED_PINS:
            reasons.append("Multiple failed PIN attempts")

        # Unusual transaction amount
        if account["balance"] > 0:

            if amount > account["balance"] * 0.8:
                reasons.append("Unusual transaction amount")

        if reasons:
            return True, reasons

        return False, []

    # Deposit
    def deposit(self, account_id, amount, pin):

        with self.lock:

            if account_id not in self.accounts:
                return False, "Invalid account"

            if amount <= 0:
                return False, "Negative/invalid amount"

            if not self.verify_pin(account_id, pin):
                return False, "Invalid PIN"

            # Daily limit check
            if self.get_daily_total(account_id) + amount > self.DAILY_LIMIT:
                return False, "Daily transaction limit exceeded"

            fraud, reasons = self.check_fraud(account_id, amount)

            account = self.accounts[account_id]

            account["balance"] += amount

            account["transactions"].append({
                "type": "deposit",
                "amount": amount,
                "time": datetime.now(),
                "suspicious": fraud,
                "reasons": reasons
            })

            if fraud:
                return True, "Deposit successful - SUSPICIOUS: " + \
                    ", ".join(reasons)

            return True, "Deposit successful"

    # Withdrawal
    def withdraw(self, account_id, amount, pin):

        with self.lock:

            if account_id not in self.accounts:
                return False, "Invalid account"

            if amount <= 0:
                return False, "Negative/invalid amount"

            if not self.verify_pin(account_id, pin):
                return False, "Invalid PIN"

            # Daily limit is checked BEFORE balance
            if self.get_daily_total(account_id) + amount > self.DAILY_LIMIT:
                return False, "Daily transaction limit exceeded"

            account = self.accounts[account_id]

            # Balance check
            if amount > account["balance"]:
                return False, "Insufficient balance"

            fraud, reasons = self.check_fraud(account_id, amount)

            account["balance"] -= amount

            account["transactions"].append({
                "type": "withdrawal",
                "amount": amount,
                "time": datetime.now(),
                "suspicious": fraud,
                "reasons": reasons
            })

            if fraud:
                return True, "Withdrawal successful - SUSPICIOUS: " + \
                    ", ".join(reasons)

            return True, "Withdrawal successful"

    # Money Transfer
    def transfer(self, sender_id, receiver_id, amount, pin):

        with self.lock:

            if sender_id not in self.accounts:
                return False, "Sender account not found"

            if receiver_id not in self.accounts:
                return False, "Receiver account not found"

            if sender_id == receiver_id:
                return False, "Cannot transfer to same account"

            if amount <= 0:
                return False, "Negative/invalid amount"

            if not self.verify_pin(sender_id, pin):
                return False, "Invalid PIN"

            # Daily limit
            if self.get_daily_total(sender_id) + amount > self.DAILY_LIMIT:
                return False, "Daily transaction limit exceeded"

            sender = self.accounts[sender_id]

            if amount > sender["balance"]:
                return False, "Insufficient balance"

            fraud, reasons = self.check_fraud(sender_id, amount)

            sender["balance"] -= amount
            self.accounts[receiver_id]["balance"] += amount

            sender["transactions"].append({
                "type": "transfer",
                "amount": amount,
                "receiver": receiver_id,
                "time": datetime.now(),
                "suspicious": fraud,
                "reasons": reasons
            })

            if fraud:
                return True, "Transfer successful - SUSPICIOUS: " + \
                    ", ".join(reasons)

            return True, "Transfer successful"

    # Balance Verification
    def get_balance(self, account_id):

        if account_id not in self.accounts:
            return None

        return self.accounts[account_id]["balance"]

    # Transaction History
    def get_transaction_history(self, account_id):

        if account_id not in self.accounts:
            return []

        return self.accounts[account_id]["transactions"]


if __name__ == "__main__":

    wallet = DigitalWallet()

    print("===== DIGITAL WALLET =====")

    print(
        wallet.create_account(
            "A101",
            "Dhanush",
            "1234",
            10000
        )[1]
    )

    print(
        wallet.deposit(
            "A101",
            1000,
            "1234"
        )[1]
    )

    print(
        wallet.withdraw(
            "A101",
            500,
            "1234"
        )[1]
    )

    print(
        "Balance:",
        wallet.get_balance("A101")
    )
