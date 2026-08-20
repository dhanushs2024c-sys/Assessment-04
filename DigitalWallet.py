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

    # ---------------- ACCOUNT CREATION ----------------
    def create_account(self, account_id, name, pin, initial_balance=0.0):

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

    # ---------------- PIN VERIFICATION ----------------
    def verify_pin(self, account_id, pin):

        if account_id not in self.accounts:
            return False

        account = self.accounts[account_id]

        if str(pin) == account["pin"]:
            account["failed_pins"] = 0
            return True

        account["failed_pins"] += 1
        return False

    # ---------------- DAILY TRANSACTION TOTAL ----------------
    def get_daily_total(self, account_id):

        account = self.accounts[account_id]
        today = datetime.now().date()

        total = 0.0

        for transaction in account["transactions"]:
            if transaction["time"].date() == today:
                if transaction["type"] in [
                    "deposit",
                    "withdrawal",
                    "transfer"
                ]:
                    total += transaction["amount"]

        return total

    # ---------------- FRAUD DETECTION ----------------
    def check_fraud(self, account_id, amount):

        if account_id not in self.accounts:
            return True, ["Invalid account"]

        account = self.accounts[account_id]
        reasons = []
        now = datetime.now()

        # More than 5 transactions in 10 minutes
        recent_transactions = []

        for transaction in account["transactions"]:
            if now - transaction["time"] <= timedelta(minutes=10):
                recent_transactions.append(transaction)

        if len(recent_transactions) >= self.MAX_TRANSACTIONS_10_MIN:
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

    # ---------------- DEPOSIT ----------------
    def deposit(self, account_id, amount, pin):

        with self.lock:

            if account_id not in self.accounts:
                return False, "Invalid account"

            if amount <= 0:
                return False, "Negative/invalid amount"

            if not self.verify_pin(account_id, pin):
                return False, "Invalid PIN"

            account = self.accounts[account_id]

            # Daily limit
            if self.get_daily_total(account_id) + amount > self.DAILY_LIMIT:
                return False, "Daily transaction limit exceeded"

            fraud, reasons = self.check_fraud(account_id, amount)

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

    # ---------------- WITHDRAWAL ----------------
    def withdraw(self, account_id, amount, pin):

        with self.lock:

            if account_id not in self.accounts:
                return False, "Invalid account"

            if amount <= 0:
                return False, "Negative/invalid amount"

            if not self.verify_pin(account_id, pin):
                return False, "Invalid PIN"

            account = self.accounts[account_id]

            # Balance check
            if amount > account["balance"]:
                return False, "Insufficient balance"

            # Daily limit
            if self.get_daily_total(account_id) + amount > self.DAILY_LIMIT:
                return False, "Daily transaction limit exceeded"

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

    # ---------------- MONEY TRANSFER ----------------
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

            sender = self.accounts[sender_id]

            if amount > sender["balance"]:
                return False, "Insufficient balance"

            if self.get_daily_total(sender_id) + amount > self.DAILY_LIMIT:
                return False, "Daily transaction limit exceeded"

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

    # ---------------- BALANCE ----------------
    def get_balance(self, account_id):

        if account_id not in self.accounts:
            return None

        return self.accounts[account_id]["balance"]

    # ---------------- TRANSACTION HISTORY ----------------
    def get_transaction_history(self, account_id):

        if account_id not in self.accounts:
            return []

        return self.accounts[account_id]["transactions"]

    # ---------------- MAIN DEMO ----------------
    def display_account(self, account_id):

        if account_id not in self.accounts:
            print("Invalid account")
            return

        account = self.accounts[account_id]

        print("\nAccount ID:", account_id)
        print("Name:", account["name"])
        print("Balance:", account["balance"])


def main():

    print("====================================")
    print("        DIGITAL WALLET SYSTEM")
    print("====================================")

    wallet = DigitalWallet()

    # Account creation
    print(wallet.create_account(
        "A101",
        "Dhanush",
        "1234",
        8000
    )[1])

    print(wallet.create_account(
        "A102",
        "Rahul",
        "5678",
        5000
    )[1])

    # Deposit
    result, message = wallet.deposit(
        "A101",
        1000,
        "1234"
    )

    print("\nDeposit:", message)

    # Withdrawal
    result, message = wallet.withdraw(
        "A101",
        500,
        "1234"
    )

    print("Withdrawal:", message)

    # Transfer
    result, message = wallet.transfer(
        "A101",
        "A102",
        1000,
        "1234"
    )

    print("Transfer:", message)

    # Balance
    print("\nBalance verification:")
    print("A101:", wallet.get_balance("A101"))
    print("A102:", wallet.get_balance("A102"))

    # Transaction history
    print("\nTransaction History:")

    for transaction in wallet.get_transaction_history("A101"):
        print(transaction)

    # Fraud check
    fraud, reasons = wallet.check_fraud(
        "A101",
        6000
    )

    print("\nFraud Detection:")

    if fraud:
        print("SUSPICIOUS TRANSACTION")

        for reason in reasons:
            print("-", reason)
    else:
        print("Transaction is normal")


if __name__ == "__main__":
    main()
