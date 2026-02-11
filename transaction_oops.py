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

# Example usage
if __name__ == "__main__":
    # Create a bank
    bank = Bank("National Bank")
    
    # Create accounts
    savings = bank.create_account("Alice", AccountType.SAVINGS, 1000)
    checking = bank.create_account("Bob", AccountType.CHECKING, 500)
    business = bank.create_account("XYZ Corp", AccountType.BUSINESS, 5000)
    
    # Perform transactions
    savings.deposit(500)
    savings.withdraw(100)
    savings.calculate_interest()
    
    checking.deposit(200)
    checking.withdraw(150)
    
    business.deposit(1000)
    business.withdraw(500)
    business.calculate_interest()
    
    # Transfers
    bank.transfer(savings.account_number, checking.account_number, 200)
    
    # Print statements
    savings.print_statement()
    checking.print_statement()
    business.print_statement()