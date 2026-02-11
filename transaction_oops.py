from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Optional

# Enum for transaction types
class TransactionType(Enum):
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    TRANSFER = "Transfer"

# Enum for account types
class AccountType(Enum):
    SAVINGS = "Savings"
    CHECKING = "Checking"
    BUSINESS = "Business"

# Transaction class - represents a single transaction
class Transaction:
    def __init__(self, transaction_id: int, amount: float, transaction_type: TransactionType):
        self.transaction_id = transaction_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.timestamp = datetime.now()
        self.status = "Completed"
    
    def __str__(self):
        return f"ID: {self.transaction_id}, Type: {self.transaction_type.value}, Amount: ${self.amount:.2f}, Time: {self.timestamp}"
    
    def __repr__(self):
        return self.__str__()

# Abstract base class for accounts
class BankAccount(ABC):
    _account_counter = 1000
    
    def __init__(self, account_holder: str, account_type: AccountType, initial_balance: float = 0):
        self.account_number = BankAccount._account_counter
        BankAccount._account_counter += 1
        self.account_holder = account_holder
        self.account_type = account_type
        self.balance = initial_balance
        self.transactions: List[Transaction] = []
        self.is_active = True
    
    @abstractmethod
    def calculate_interest(self):
        """Calculate interest based on account type"""
        pass
    
    def deposit(self, amount: float) -> bool:
        """Deposit money into account"""
        if amount <= 0:
            print("Invalid deposit amount!")
            return False
        
        self.balance += amount
        transaction = Transaction(len(self.transactions) + 1, amount, TransactionType.DEPOSIT)
        self.transactions.append(transaction)
        print(f"Deposit of ${amount:.2f} successful!")
        return True
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw money from account"""
        if amount <= 0:
            print("Invalid withdrawal amount!")
            return False
        
        if amount > self.balance:
            print(f"Insufficient balance! Available: ${self.balance:.2f}")
            return False
        
        self.balance -= amount
        transaction = Transaction(len(self.transactions) + 1, amount, TransactionType.WITHDRAWAL)
        self.transactions.append(transaction)
        print(f"Withdrawal of ${amount:.2f} successful!")
        return True
    
    def get_balance(self) -> float:
        """Get current balance"""
        return self.balance
    
    def print_statement(self):
        """Print account statement"""
        print(f"\n{'='*60}")
        print(f"Account Statement - {self.account_holder}")
        print(f"Account Number: {self.account_number}")
        print(f"Account Type: {self.account_type.value}")
        print(f"Current Balance: ${self.balance:.2f}")
        print(f"{'='*60}")
        print("Transaction History:")
        for transaction in self.transactions:
            print(f"  {transaction}")
        print(f"{'='*60}\n")

# Savings Account - inherits from BankAccount
class SavingsAccount(BankAccount):
    def __init__(self, account_holder: str, initial_balance: float = 0):
        super().__init__(account_holder, AccountType.SAVINGS, initial_balance)
        self.interest_rate = 0.04  # 4% annual interest
    
    def calculate_interest(self):
        """Calculate monthly interest"""
        monthly_interest = self.balance * (self.interest_rate / 12)
        self.balance += monthly_interest
        transaction = Transaction(len(self.transactions) + 1, monthly_interest, TransactionType.DEPOSIT)
        self.transactions.append(transaction)
        print(f"Interest added: ${monthly_interest:.2f}")
        return monthly_interest

# Checking Account - inherits from BankAccount
class CheckingAccount(BankAccount):
    def __init__(self, account_holder: str, initial_balance: float = 0):
        super().__init__(account_holder, AccountType.CHECKING, initial_balance)
        self.overdraft_limit = 500  # $500 overdraft protection
    
    def calculate_interest(self):
        """No interest for checking accounts"""
        return 0
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw with overdraft protection"""
        if amount <= 0:
            print("Invalid withdrawal amount!")
            return False
        
        if amount > (self.balance + self.overdraft_limit):
            print(f"Withdrawal exceeds limit! Available with overdraft: ${self.balance + self.overdraft_limit:.2f}")
            return False
        
        self.balance -= amount
        transaction = Transaction(len(self.transactions) + 1, amount, TransactionType.WITHDRAWAL)
        self.transactions.append(transaction)
        print(f"Withdrawal of ${amount:.2f} successful!")
        return True

# Business Account - inherits from BankAccount
class BusinessAccount(BankAccount):
    def __init__(self, account_holder: str, initial_balance: float = 0):
        super().__init__(account_holder, AccountType.BUSINESS, initial_balance)
        self.interest_rate = 0.02  # 2% annual interest
        self.transaction_fee = 0.50  # $0.50 per transaction
    
    def calculate_interest(self):
        """Calculate monthly interest"""
        monthly_interest = self.balance * (self.interest_rate / 12)
        self.balance += monthly_interest
        transaction = Transaction(len(self.transactions) + 1, monthly_interest, TransactionType.DEPOSIT)
        self.transactions.append(transaction)
        print(f"Interest added: ${monthly_interest:.2f}")
        return monthly_interest
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw with transaction fee"""
        if super().withdraw(amount):
            self.balance -= self.transaction_fee
            print(f"Transaction fee: ${self.transaction_fee:.2f}")
            return True
        return False

# Bank class - manages all accounts
class Bank:
    def __init__(self, bank_name: str):
        self.bank_name = bank_name
        self.accounts: dict = {}
    
    def create_account(self, account_holder: str, account_type: AccountType, initial_balance: float = 0) -> BankAccount:
        """Create a new account"""
        if account_type == AccountType.SAVINGS:
            account = SavingsAccount(account_holder, initial_balance)
        elif account_type == AccountType.CHECKING:
            account = CheckingAccount(account_holder, initial_balance)
        else:
            account = BusinessAccount(account_holder, initial_balance)
        
        self.accounts[account.account_number] = account
        print(f"Account created successfully! Account Number: {account.account_number}")
        return account
    
    def transfer(self, from_account: int, to_account: int, amount: float) -> bool:
        """Transfer money between accounts"""
        if from_account not in self.accounts or to_account not in self.accounts:
            print("Invalid account number!")
            return False
        
        source = self.accounts[from_account]
        destination = self.accounts[to_account]
        
        if source.withdraw(amount):
            destination.balance += amount
            transaction = Transaction(len(destination.transactions) + 1, amount, TransactionType.TRANSFER)
            destination.transactions.append(transaction)
            print(f"Transfer of ${amount:.2f} from {source.account_holder} to {destination.account_holder} successful!")
            return True
        return False
    
    def get_account(self, account_number: int) -> Optional[BankAccount]:
        """Retrieve account by number"""
        return self.accounts.get(account_number)

# Interactive menu system
def display_main_menu():
    print("\n" + "="*60)
    print(f"{'BANK MANAGEMENT SYSTEM':^60}")
    print("="*60)
    print("1. Create Account")
    print("2. Deposit Money")
    print("3. Withdraw Money")
    print("4. Check Balance")
    print("5. Transfer Money")
    print("6. Calculate Interest")
    print("7. View Account Statement")
    print("8. Exit")
    print("="*60)

def get_account_type():
    print("\nSelect Account Type:")
    print("1. Savings Account")
    print("2. Checking Account")
    print("3. Business Account")
    choice = input("Enter choice (1-3): ").strip()
    
    account_types = {
        "1": AccountType.SAVINGS,
        "2": AccountType.CHECKING,
        "3": AccountType.BUSINESS
    }
    return account_types.get(choice)

def create_account(bank):
    account_holder = input("Enter account holder name: ").strip()
    account_type = get_account_type()
    
    if account_type is None:
        print("Invalid account type!")
        return
    
    try:
        initial_balance = float(input("Enter initial balance: $"))
        if initial_balance < 0:
            print("Balance cannot be negative!")
            return
        bank.create_account(account_holder, account_type, initial_balance)
    except ValueError:
        print("Invalid amount!")

def deposit_money(bank):
    try:
        account_num = int(input("Enter account number: "))
        account = bank.get_account(account_num)
        
        if not account:
            print("Account not found!")
            return
        
        amount = float(input("Enter deposit amount: $"))
        account.deposit(amount)
    except ValueError:
        print("Invalid input!")

def withdraw_money(bank):
    try:
        account_num = int(input("Enter account number: "))
        account = bank.get_account(account_num)
        
        if not account:
            print("Account not found!")
            return
        
        amount = float(input("Enter withdrawal amount: $"))
        account.withdraw(amount)
    except ValueError:
        print("Invalid input!")

def check_balance(bank):
    try:
        account_num = int(input("Enter account number: "))
        account = bank.get_account(account_num)
        
        if not account:
            print("Account not found!")
            return
        
        print(f"\nAccount: {account.account_holder}")
        print(f"Balance: ${account.get_balance():.2f}")
    except ValueError:
        print("Invalid account number!")

def transfer_money(bank):
    try:
        from_account = int(input("Enter source account number: "))
        to_account = int(input("Enter destination account number: "))
        amount = float(input("Enter transfer amount: $"))
        bank.transfer(from_account, to_account, amount)
    except ValueError:
        print("Invalid input!")

def calculate_interest(bank):
    try:
        account_num = int(input("Enter account number: "))
        account = bank.get_account(account_num)
        
        if not account:
            print("Account not found!")
            return
        
        account.calculate_interest()
    except ValueError:
        print("Invalid account number!")

def view_statement(bank):
    try:
        account_num = int(input("Enter account number: "))
        account = bank.get_account(account_num)
        
        if not account:
            print("Account not found!")
            return
        
        account.print_statement()
    except ValueError:
        print("Invalid account number!")

# Main program
if __name__ == "__main__":
    # Get bank name from user
    bank_name = input("Enter bank name: ").strip()
    if not bank_name:
        bank_name = "National Bank"
    
    bank = Bank(bank_name)
    
    while True:
        display_main_menu()
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == "1":
            create_account(bank)
        elif choice == "2":
            deposit_money(bank)
        elif choice == "3":
            withdraw_money(bank)
        elif choice == "4":
            check_balance(bank)
        elif choice == "5":
            transfer_money(bank)
        elif choice == "6":
            calculate_interest(bank)
        elif choice == "7":
            view_statement(bank)
        elif choice == "8":
            print("\nThank you for using Bank Management System!")
            break
        else:
            print("Invalid choice! Please try again.")