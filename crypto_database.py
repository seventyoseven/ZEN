import sqlite3
import os

# Base directory
BASE_DIR = r"C:\Users\Eshaal\Downloads\Year 1\CST1510 Lab tasks\CST1510 - 2\actual code\db"
DB_PATH = os.path.join(BASE_DIR, "investment_platform.db")

# Ensure the directory exists
os.makedirs(BASE_DIR, exist_ok=True)

print("Connecting to database...")
conn = sqlite3.connect(DB_PATH)

# Enable foreign key constraints
conn.execute("PRAGMA foreign_keys = ON;")

# Create a cursor object to interact with the database
cursor = conn.cursor()

print("Creating tables...")

# Create the 'accounts' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS accounts (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    balance REAL NOT NULL DEFAULT 1000.0
);
''')


# Create the 'portfolio' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS portfolio (
    username TEXT,
    asset_name TEXT,
    quantity REAL NOT NULL,
    PRIMARY KEY (username, asset_name),
    FOREIGN KEY (username) REFERENCES accounts (username) ON DELETE CASCADE
);
''')

# Create the 'transactions' table
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    username TEXT,
    asset_name TEXT,
    quantity REAL NOT NULL,
    action TEXT CHECK(action IN ('buy', 'sell')) NOT NULL,
    date TEXT NOT NULL,
    PRIMARY KEY (username, asset_name, date),
    FOREIGN KEY (username) REFERENCES accounts (username) ON DELETE CASCADE
);
''')

print("Committing changes...")
conn.commit()

print("Closing connection...")
conn.close()

print(f"Database setup complete. Database saved at: {DB_PATH}")