class DigitalWallet:

    DAILY_LIMIT = 5
    LARGE_TRANSACTION = 50000

    def __init__(self):
        self.accounts = {}
        self.transactions = {}

    def create_account(self, account_id, name, pin, balance=0):
        if account_id in self.accounts:
            return False, "Account already exists"

        if balance < 0:
            return False, "Invalid opening balance"

        self.accounts[account_id] = {
            "name": name,
            "pin": str(pin),
            "balance": float(balance),
            "failed_pins": 0,
            "transaction_count": 0
        }

        self.transactions[account_id] = []

        return True, "Account created successfully"

    def verify_pin(self, account_id, pin):
        if account_id not in self.accounts:
            return False

        if self.accounts[account_id]["pin"] == str(pin):
            self.accounts[account_id]["failed_pins"] = 0
            return True

        self.accounts[account_id]["failed_pins"] += 1
        return False

    def deposit(self, account_id, amount):
        if account_id not in self.accounts:
            return False, "Invalid account"

        if amount <= 0:
            return False, "Negative or zero amount"

        self.accounts[account_id]["balance"] += amount
        self.record_transaction(account_id, "DEPOSIT", amount)

        return True, "Deposit successful"

    def withdraw(self, account_id, amount):
        if account_id not in self.accounts:
            return False, "Invalid account"

        if amount <= 0:
            return False, "Negative or zero amount"

        if amount > self.accounts[account_id]["balance"]:
            return False, "Insufficient balance"

        self.accounts[account_id]["balance"] -= amount
        self.record_transaction(account_id, "WITHDRAW", amount)

        return True, "Withdrawal successful"

    def transfer(self, sender, receiver, amount):
        if sender not in self.accounts or receiver not in self.accounts:
            return False, "Invalid account"

        if sender == receiver:
            return False, "Cannot transfer to same account"

        if amount <= 0:
            return False, "Negative or zero amount"

        if amount > self.accounts[sender]["balance"]:
            return False, "Insufficient balance"

        self.accounts[sender]["balance"] -= amount
        self.accounts[receiver]["balance"] += amount

        self.record_transaction(sender, "TRANSFER", amount)
        self.record_transaction(receiver, "RECEIVED", amount)

        return True, "Transfer successful"

    def record_transaction(self, account_id, transaction_type, amount):
        self.accounts[account_id]["transaction_count"] += 1

        self.transactions[account_id].append({
            "type": transaction_type,
            "amount": amount
        })

    def get_balance(self, account_id):
        if account_id not in self.accounts:
            return None

        return self.accounts[account_id]["balance"]

    def get_transaction_history(self, account_id):
        return self.transactions.get(account_id, [])

    def check_fraud(self, account_id, amount):
        if account_id not in self.accounts:
            return True, ["Invalid account"]

        account = self.accounts[account_id]
        reasons = []

        if account["transaction_count"] > self.DAILY_LIMIT:
            reasons.append("More than 5 transactions in 10 minutes")

        if amount > self.LARGE_TRANSACTION:
            reasons.append("Large transaction")

        if account["failed_pins"] >= 3:
            reasons.append("Multiple failed PIN attempts")

        if account["balance"] > 0 and amount > account["balance"] * 0.8:
            reasons.append("Unusual transaction amount")

        if reasons:
            return True, reasons

        return False, []


def main():

    print("===== DIGITAL WALLET =====")

    wallet = DigitalWallet()

    print(wallet.create_account(
        "A101", "Abinesh", "1234", 100000
    )[1])

    print(wallet.create_account(
        "A102", "Rahul", "5678", 50000
    )[1])

    print(wallet.deposit("A101", 10000)[1])

    print(wallet.withdraw("A101", 5000)[1])

    print(wallet.transfer("A101", "A102", 10000)[1])

    print("\nTransaction History:")

    for transaction in wallet.get_transaction_history("A101"):
        print(transaction)

    fraud, reasons = wallet.check_fraud("A101", 90000)

    if fraud:
        print("\nSUSPICIOUS TRANSACTION")
        for reason in reasons:
            print("-", reason)
    else:
        print("\nTransaction is normal")

    print("\nBalance:", wallet.get_balance("A101"))


if __name__ == "__main__":
    main()
