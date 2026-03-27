import datetime
import time
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Define paths for accounts.txt and portfolio.txt
ACCOUNTS_FILE_PATH = r"C:\Users\Eshaal\Downloads\CW2_CST1510\Textfiles\accounts.txt"
PORTFOLIO_FILE_PATH = r"C:\Users\Eshaal\Downloads\CW2_CST1510\Textfiles\portfolio.txt"

def load_Accounts():
    accounts = []
    try:
        with open(ACCOUNTS_FILE_PATH, 'r') as file:
            for line in file:
                if not line.strip():
                    continue

                parts = line.strip().split(', ')

                if len(parts) != 3:
                    print(f"Skipping malformed line: {line.strip()}")
                    continue

                username, password, balance = parts
                try:
                    accounts.append(Account(username, password, float(balance)))
                except ValueError:
                    print(f"Invalid balance value for account: {line.strip()}")
                    
    except FileNotFoundError:
        print("No accounts file found, starting fresh.")

    return accounts

def save_accounts(accounts):
    try:
        with open(ACCOUNTS_FILE_PATH, 'w') as file:
            for account in accounts:
                file.write(f"{account.username}, {account.password}, {account.balance}\n")
    except Exception as e:
        print(f"Error saving accounts: {e}")

def save_portfolio(portfolio):
    try:
        with open(PORTFOLIO_FILE_PATH, 'w') as file:
            for asset, quantity in portfolio.holdings.items():
                file.write(f"{asset}, {quantity}\n")
    except Exception as e:
        print(f"Error saving portfolio: {e}")

def load_portfolio():
    portfolio = Portfolio()
    try:
        with open(PORTFOLIO_FILE_PATH, 'r') as file:
            for line in file:
                if not line.strip():
                    continue

                parts = line.strip().split(', ')

                if len(parts) != 2:
                    print(f"Skipping malformed line: {line.strip()}")
                    continue

                asset, quantity = parts
                try:
                    portfolio.add_asset(asset, float(quantity))
                except ValueError:
                    print(f"Invalid quantity for asset: {line.strip()}")
                    
    except FileNotFoundError:
        print("No portfolio file found, starting fresh.")

    return portfolio

assets = {
    "Bitcoin": 50000,
    "Ethereum": 3000,
    "Gold": 1800,
    "Silver": 25
}

class Account:
    def __init__(self, username, password, balance=0):
        self.username = username
        self.password = password
        self.balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print(f"Successfully deposited ${amount}. New balance: ${self.balance}")
            self.update_accounts_file()
        else:
            print("Deposit amount must be positive.")

    def withdraw(self, amount):
        if amount > 0:
            if self.balance < amount:
                print("Insufficient funds!")
            else:
                self.balance -= amount
                print(f"Successfully withdrew ${amount}. New balance: ${self.balance}")
                self.update_accounts_file()
        else:
            print("Withdrawal amount must be positive!")

    def update_accounts_file(self):
        accounts = load_Accounts()
        for account in accounts:
            if account.username == self.username and account.password == self.password:
                account.balance = self.balance
                break
        save_accounts(accounts)

    def view_balance(self):
        print(f"Current balance: ${self.balance}")

class Portfolio:
    def __init__(self):
        self.holdings = {}

    def add_asset(self, asset, quantity):
        if quantity > 0:
            if asset in self.holdings:
                self.holdings[asset] += quantity
            else:
                self.holdings[asset] = quantity
        else:
            print("Quantity should be positive!")

    def remove_asset(self, asset, quantity):
        if asset in self.holdings:
            if quantity > 0 and self.holdings[asset] >= quantity:
                self.holdings[asset] -= quantity
                print(f"Removed {quantity} of {asset} from your portfolio")

                if self.holdings[asset] == 0:
                    del self.holdings[asset]
                    print(f"Removed all quantity of {asset} from your portfolio!")
            else:
                print(f"Insufficient quantity of {asset} to remove.")
        else:
            print(f"{asset} not found in your portfolio.")

    def view_holdings(self):
        if not self.holdings:
            print("Your portfolio is empty.")
            return
        total_value = 0
        print("\nCurrent Portfolio Holdings:")
        print(f"{'Asset':<10}{'Quantity':<10}{'Value ($)':<10}")
        print("-" * 30)

        for asset, quantity in self.holdings.items():
            if asset in assets:
                value = assets[asset] * quantity
                total_value += value
                print(f"{asset:<10}{quantity:<10}{value:<10.2f}")
            else:
                print(f"{asset:<10}{quantity:<10}Price not available")

        print("-" * 30)
        print(f"Total Portfolio Value: ${total_value:.2f}")

        save_portfolio(self)

def main():
    accounts = load_Accounts()
    portfolio = load_portfolio()

    print("Welcome to the Crypto Investment Platform!")
    print("-" * 40)

    username = input("Enter your username: ")
    password = input("Enter your password: ")

    current_account = None
    for account in accounts:
        if account.username == username and account.password == password:
            current_account = account
            break

    if not current_account:
        print("Account not found, creating a new one.")
        initial_balance = float(input("Enter your initial deposit amount: "))
        current_account = Account(username, password, initial_balance)
        accounts.append(current_account)
        save_accounts(accounts)

    while True:
        print("\n=== Main Menu ===")
        print("1. Deposit Funds")
        print("2. Withdraw Funds")
        print("3. View Balance")
        print("4. View Portfolio")
        print("5. Buy Asset")
        print("6. Sell Asset")
        print("7. Exit")
        choice = input("Choose an option (1-7): ").strip()

        if choice == '1':
            try:
                amount = float(input("Enter amount to deposit: "))
                current_account.deposit(amount)
            except ValueError:
                print("Invalid amount. Please enter a number.")

        elif choice == '2':
            try:
                amount = float(input("Enter amount to withdraw: "))
                current_account.withdraw(amount)
            except ValueError:
                print("Invalid amount. Please enter a number.")

        elif choice == '3':
            current_account.view_balance()

        elif choice == '4':
            portfolio.view_holdings()

        elif choice == '5':
            print(f"{'Asset':<10} {'Price ($)':<10}")
            print("-" * 20)
            for asset, price in assets.items():
                print(f"{asset:<10}{price:<10}")
            print("-" * 20)
            asset = input("Enter asset name: ").strip()
            try:
                quantity = float(input(f"Enter quantity of {asset} to buy: "))
                if asset in assets:
                    cost = assets[asset] * quantity
                    if current_account.balance >= cost:
                        current_account.withdraw(cost)
                        portfolio.add_asset(asset, quantity)
                    else:
                        print("Insufficient funds to buy this asset.")
                else:
                    print("Asset not recognized.")
            except ValueError:
                print("Invalid quantity. Please enter a number.")

        elif choice == '6':
            asset = input("Enter asset name: ").strip()
            try:
                quantity = float(input(f"Enter quantity of {asset} to sell: "))
                portfolio.remove_asset(asset, quantity)
            except ValueError:
                print("Invalid quantity. Please enter a number.")

        elif choice == '7':
            print("Exiting the platform. Goodbye!")
            break

        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
