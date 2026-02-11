import csv
import os
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
    def __init__(self, transaction_id: int, amount: float, transaction_type: TransactionType, timestamp: str = None):
        self.transaction_id = transaction_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.timestamp = timestamp if timestamp else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = "Completed"
    
    def __str__(self):
        return f"ID: {self.transaction_id}, Type: {self.transaction_type.value}, Amount: ${self.amount:.2f}, Time: {self.timestamp}"
    
    def __repr__(self):
        return self.__str__()

# Abstract base class for accounts
class BankAccount(ABC):
    _account_counter = 1000
    
    def __init__(self, account_holder: str, account_type: AccountType, initial_balance: float = 0, account_number: int = None):
        if account_number is None:
            self.account_number = BankAccount._account_counter
            BankAccount._account_counter += 1
        else:
            self.account_number = account_number
            # Update counter if custom number is higher
            if account_number >= BankAccount._account_counter:
                BankAccount._account_counter = account_number + 1
        
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
    def __init__(self, account_holder: str, initial_balance: float = 0, account_number: int = None):
        super().__init__(account_holder, AccountType.SAVINGS, initial_balance, account_number)
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
    def __init__(self, account_holder: str, initial_balance: float = 0, account_number: int = None):
        super().__init__(account_holder, AccountType.CHECKING, initial_balance, account_number)
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
    def __init__(self, account_holder: str, initial_balance: float = 0, account_number: int = None):
        super().__init__(account_holder, AccountType.BUSINESS, initial_balance, account_number)
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
        self.accounts_file = "accounts.csv"
        self.transactions_file = "transactions.csv"
    
    def create_account(self, account_holder: str, account_type: AccountType, initial_balance: float = 0, account_number: int = None) -> BankAccount:
        """Create a new account"""
        # Check if account number already exists
        if account_number and account_number in self.accounts:
            print(f"Account number {account_number} already exists!")
            return None
        
        if account_type == AccountType.SAVINGS:
            account = SavingsAccount(account_holder, initial_balance, account_number)
        elif account_type == AccountType.CHECKING:
            account = CheckingAccount(account_holder, initial_balance, account_number)
        else:
            account = BusinessAccount(account_holder, initial_balance, account_number)
        
        self.accounts[account.account_number] = account
        print(f"Account created successfully! Account Number: {account.account_number}")
        self.save_accounts()
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
            self.save_accounts()
            self.save_all_transactions()
            return True
        return False
    
    def get_account(self, account_number: int) -> Optional[BankAccount]:
        """Retrieve account by number"""
        return self.accounts.get(account_number)
    
    def save_accounts(self):
        """Save all accounts to CSV"""
        try:
            with open(self.accounts_file, 'w', newline='') as csvfile:
                fieldnames = ['AccountNumber', 'AccountHolder', 'AccountType', 'Balance']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for account in self.accounts.values():
                    writer.writerow({
                        'AccountNumber': account.account_number,
                        'AccountHolder': account.account_holder,
                        'AccountType': account.account_type.value,
                        'Balance': account.balance
                    })
            print(f"Accounts saved to {self.accounts_file}")
        except Exception as e:
            print(f"Error saving accounts: {e}")
    
    def save_all_transactions(self):
        """Save all transactions to CSV"""
        try:
            with open(self.transactions_file, 'w', newline='') as csvfile:
                fieldnames = ['AccountNumber', 'TransactionID', 'Type', 'Amount', 'Timestamp', 'Status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for account in self.accounts.values():
                    for transaction in account.transactions:
                        writer.writerow({
                            'AccountNumber': account.account_number,
                            'TransactionID': transaction.transaction_id,
                            'Type': transaction.transaction_type.value,
                            'Amount': transaction.amount,
                            'Timestamp': transaction.timestamp,
                            'Status': transaction.status
                        })
            print(f"Transactions saved to {self.transactions_file}")
        except Exception as e:
            print(f"Error saving transactions: {e}")
    
    def load_accounts(self):
        """Load accounts from CSV"""
        if not os.path.exists(self.accounts_file):
            print("No previous account data found.")
            return
        
        try:
            with open(self.accounts_file, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    account_number = int(row['AccountNumber'])
                    account_holder = row['AccountHolder']
                    account_type_str = row['AccountType']
                    balance = float(row['Balance'])
                    
                    # Convert string to AccountType enum
                    account_type = AccountType.SAVINGS if account_type_str == "Savings" else \
                                  AccountType.CHECKING if account_type_str == "Checking" else \
                                  AccountType.BUSINESS
                    
                    # Create appropriate account type
                    if account_type == AccountType.SAVINGS:
                        account = SavingsAccount(account_holder, balance, account_number)
                    elif account_type == AccountType.CHECKING:
                        account = CheckingAccount(account_holder, balance, account_number)
                    else:
                        account = BusinessAccount(account_holder, balance, account_number)
                    
                    self.accounts[account_number] = account
                
            print(f"Loaded {len(self.accounts)} accounts from {self.accounts_file}")
        except Exception as e:
            print(f"Error loading accounts: {e}")
    
    def load_transactions(self):
        """Load transactions from CSV"""
        if not os.path.exists(self.transactions_file):
            print("No previous transaction data found.")
            return
        
        try:
            with open(self.transactions_file, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    account_number = int(row['AccountNumber'])
                    transaction_id = int(row['TransactionID'])
                    transaction_type_str = row['Type']
                    amount = float(row['Amount'])
                    timestamp = row['Timestamp']
                    status = row['Status']
                    
                    if account_number in self.accounts:
                        # Convert string to TransactionType enum
                        transaction_type = TransactionType.DEPOSIT if transaction_type_str == "Deposit" else \
                                          TransactionType.WITHDRAWAL if transaction_type_str == "Withdrawal" else \
                                          TransactionType.TRANSFER
                        
                        transaction = Transaction(transaction_id, amount, transaction_type, timestamp)
                        transaction.status = status
                        self.accounts[account_number].transactions.append(transaction)
            
            print(f"Loaded transactions from {self.transactions_file}")
        except Exception as e:
            print(f"Error loading transactions: {e}")

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
    print("8. Save Data")
    print("9. Exit")
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
        
        account_num_input = input("Enter account number (press Enter for auto-generated): ").strip()
        account_number = None
        
        if account_num_input:
            try:
                account_number = int(account_num_input)
                if account_number < 0:
                    print("Account number cannot be negative!")
                    return
            except ValueError:
                print("Invalid account number format!")
                return
        
        bank.create_account(account_holder, account_type, initial_balance, account_number)
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
        if account.deposit(amount):
            bank.save_accounts()
            bank.save_all_transactions()
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
        if account.withdraw(amount):
            bank.save_accounts()
            bank.save_all_transactions()
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
        bank.save_accounts()
        bank.save_all_transactions()
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
    
    # Load existing data
    bank.load_accounts()
    bank.load_transactions()
    
    while True:
        display_main_menu()
        choice = input("Enter your choice (1-9): ").strip()
        
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
            bank.save_accounts()
            bank.save_all_transactions()
        elif choice == "9":
            bank.save_accounts()
            bank.save_all_transactions()
            print("\nThank you for using Bank Management System!")
            break
        else:
            print("Invalid choice! Please try again.")