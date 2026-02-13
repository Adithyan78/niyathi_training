import csv
import os
from datetime import datetime
import uuid

ACCOUNTS_FILE = "accounts.csv"
TRANSACTIONS_FILE = "transactions.csv"
NOTIFICATIONS_FILE = "notifications.csv"


# ==============================
# Utility: Initialize CSV Files
# ==============================

def initialize_files():
    if not os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["account_number", "name", "balance", "status"])

    if not os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["transaction_id", "account_number", "type", "amount", "date", "status"])

    if not os.path.exists(NOTIFICATIONS_FILE):
        with open(NOTIFICATIONS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["notification_id", "account_number", "message", "date"])


# ==============================
# 1️⃣ Transaction Base Class
# ==============================

class Transaction:
    def __init__(self, account_number, amount, t_type):
        self.transaction_id = str(uuid.uuid4())[:8]
        self.account_number = account_number
        self.amount = amount
        self.type = t_type
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "SUCCESS"

    def log_transaction(self):
        with open(TRANSACTIONS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                self.transaction_id,
                self.account_number,
                self.type,
                self.amount,
                self.date,
                self.status
            ])


# ==============================
# 2️⃣ Account Validation Module
# ==============================

class AccountValidator:
    @staticmethod
    def validate(account_number):
        with open(ACCOUNTS_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["account_number"] == account_number and row["status"] == "active":
                    return row
        return None


# ==============================
# 3️⃣ Balance Management Module
# ==============================

class BalanceManager:
    @staticmethod
    def update_balance(account_number, new_balance):
        rows = []
        with open(ACCOUNTS_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["account_number"] == account_number:
                    row["balance"] = str(new_balance)
                rows.append(row)

        with open(ACCOUNTS_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["account_number", "name", "balance", "status"])
            writer.writeheader()
            writer.writerows(rows)


# ==============================
# 4️⃣ Deposit Module
# ==============================

class Deposit(Transaction):
    def process(self):
        account = AccountValidator.validate(self.account_number)
        if not account:
            print("Invalid Account!")
            return

        new_balance = float(account["balance"]) + self.amount
        BalanceManager.update_balance(self.account_number, new_balance)
        self.log_transaction()
        Notification.send(self.account_number, f"Deposit of {self.amount} successful.")
        print("Deposit Successful!")


# ==============================
# 5️⃣ Withdrawal Module
# ==============================

class Withdrawal(Transaction):
    def process(self):
        account = AccountValidator.validate(self.account_number)
        if not account:
            print("Invalid Account!")
            return

        if float(account["balance"]) < self.amount:
            print("Insufficient Balance!")
            return

        new_balance = float(account["balance"]) - self.amount
        BalanceManager.update_balance(self.account_number, new_balance)
        self.log_transaction()
        Notification.send(self.account_number, f"Withdrawal of {self.amount} successful.")
        print("Withdrawal Successful!")


# ==============================
# 6️⃣ Fund Transfer Module
# ==============================

class FundTransfer(Transaction):
    def __init__(self, sender, receiver, amount):
        super().__init__(sender, amount, "TRANSFER")
        self.receiver = receiver

    def process(self):
        sender_acc = AccountValidator.validate(self.account_number)
        receiver_acc = AccountValidator.validate(self.receiver)

        if not sender_acc or not receiver_acc:
            print("Invalid Sender or Receiver!")
            return

        if float(sender_acc["balance"]) < self.amount:
            print("Insufficient Balance!")
            return

        # Debit Sender
        BalanceManager.update_balance(self.account_number,
                                      float(sender_acc["balance"]) - self.amount)

        # Credit Receiver
        BalanceManager.update_balance(self.receiver,
                                      float(receiver_acc["balance"]) + self.amount)

        self.log_transaction()
        Notification.send(self.account_number, f"Transferred {self.amount} to {self.receiver}.")
        print("Transfer Successful!")


# ==============================
# 7️⃣ Transaction History Module
# ==============================

class TransactionHistory:
    @staticmethod
    def show(account_number):
        with open(TRANSACTIONS_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["account_number"] == account_number:
                    print(row)


# ==============================
# 8️⃣ Fraud Detection Module
# ==============================

class FraudDetection:
    @staticmethod
    def check(amount):
        if amount > 100000:
            print("⚠️ High Value Transaction Flagged!")
            return True
        return False


# ==============================
# 9️⃣ Transaction Reversal Module
# ==============================

class TransactionReversal:
    @staticmethod
    def reverse(transaction_id):
        print(f"Transaction {transaction_id} marked for reversal (manual verification needed).")


# ==============================
# 🔟 Transaction Report Module
# ==============================

class TransactionReport:
    @staticmethod
    def generate():
        total_deposit = total_withdraw = total_transfer = 0

        with open(TRANSACTIONS_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["type"] == "DEPOSIT":
                    total_deposit += float(row["amount"])
                elif row["type"] == "WITHDRAW":
                    total_withdraw += float(row["amount"])
                elif row["type"] == "TRANSFER":
                    total_transfer += float(row["amount"])

        print("=== Transaction Report ===")
        print("Total Deposits:", total_deposit)
        print("Total Withdrawals:", total_withdraw)
        print("Total Transfers:", total_transfer)


# ==============================
# 1️⃣1️⃣ Notification Module
# ==============================

class Notification:
    @staticmethod
    def send(account_number, message):
        with open(NOTIFICATIONS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                str(uuid.uuid4())[:8],
                account_number,
                message,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])


# ==============================
# Sample Run
# ==============================

if __name__ == "__main__":
    initialize_files()

    # Sample deposit
    d = Deposit("1001", 5000, "DEPOSIT")
    d.process()

    # Sample withdrawal
    w = Withdrawal("1001", 2000, "WITHDRAW")
    w.process()

    # Sample transfer
    t = FundTransfer("1001", "1002", 1000)
    t.process()

    # Show history
    TransactionHistory.show("1001")

    # Generate report
    TransactionReport.generate()
