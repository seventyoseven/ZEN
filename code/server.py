import threading
import requests
import sqlite3
import socket

#this is the path defined for the database
DB_PATH = r"C:\Users\Eshaal\Downloads\CW2_CST1510\db\investment_platform.db"

def crypto(crypto_name):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": crypto_name,  # dynamically use the crypto_name to fetch the price
        "vs_currencies": "usd"      
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Extract the price directly from the JSON response
        data = response.json()
        if crypto_name in data:
            price = data[crypto_name]['usd']
            return price  # Return the price instead of printing
        else:
            print(f"Error: {crypto_name} not found in the response.")
            return None
    
    except requests.RequestException as e:
        print(f"Error fetching live price for {crypto_name}: {e}")
        return None

def get_precious_metal_price(metal='XAU', base='USD', api_key='2f00eab563125757bc52895f887cc7b4'):
    url = f"https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base={base}&symbols={metal}"
    
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            if 'rates' in data:
                return data['rates'][metal]  # Return the metal price
            else:
                print(f"Error: {metal} not found in the data.")
                return None
        else:
            print(f"Error fetching data: {data.get('error', 'Unknown error')}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching precious metal data for {metal}: {e}")
        return None
price_of_solana = crypto("solana"),
# Now, use the functions to populate live_prices
def get_live_prices(): #this function either gives out live prices or default ones if live prices fail
    return {
        "Bitcoin": crypto("bitcoin"),
        "Ethereum": crypto("ethereum"),
        "Solana": crypto("solana"),
        "Gold": get_precious_metal_price('XAU', 'USD', '2f00eab563125757bc52895f887cc7b4'),
        "Silver": get_precious_metal_price('XAG', 'USD', '2f00eab563125757bc52895f887cc7b4')
        # Add other assets if needed
    }

def get_assets():
    live_prices = get_live_prices()  # Attempt to get live prices
    if live_prices["Bitcoin"] is None or live_prices["Ethereum"] is None or live_prices["Gold"] is None or live_prices["Silver"] is None:
        # Return default values if live prices are None
        return {
            "Bitcoin": 50000,  # Default value if API fails
            "Ethereum": 3000,
            "Gold": 1800,
            "Silver": 25
        }
    return live_prices  # Return live prices if successful



"""  Loads account details from the database.

    Args:
        username (str): The username of the account.

    Returns:
        dict: A dictionary containing account details if the username exists, None otherwise.
    """
def load_account_from_db(username):
    try:
        with sqlite3.connect(DB_PATH) as conn: #connect it to the DB_PATH
            cursor = conn.cursor()
            cursor.execute("SELECT username, password, balance FROM accounts WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return {"username": row[0], "password": row[1], "balance": row[2]}
            else:
                print("Username not found.")
                return None
    except sqlite3.Error as e:
        print(f"Error querying database: {e}")
        return None

# Update balance in database
def update_balance_in_db(username, amount, action):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if action == "deposit":
                cursor.execute("UPDATE accounts SET balance = balance + ? WHERE username = ?", (amount, username))
            elif action == "withdraw":
                # Ensure balance remains >= 1000 after withdrawal
                cursor.execute("""
                    UPDATE accounts 
                    SET balance = balance - ? 
                    WHERE username = ? AND balance - ? >= 1000
                """, (amount, username, amount))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating balance: {e}")
        return False


# Update portfolio in the database
def update_portfolio_in_db(username, asset, quantity, action):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if action == "buy":
                cursor.execute("""
                    INSERT INTO portfolio (username, asset_name, quantity)
                    VALUES (?, ?, ?)
                    ON CONFLICT(username, asset_name) DO UPDATE SET quantity = quantity + excluded.quantity
                """, (username, asset, quantity))
                success = cursor.rowcount > 0
            elif action == "sell":
                # First, attempt to reduce the quantity
                cursor.execute("""
                    UPDATE portfolio
                    SET quantity = quantity - ?
                    WHERE username = ? AND asset_name = ? AND quantity >= ?
                """, (quantity, username, asset, quantity))
                
                if cursor.rowcount == 0:
                    # Log failure to sell due to insufficient quantity or nonexistent asset
                    print(f"Sell operation failed for {asset}: insufficient quantity or asset not found.")
                    success = False
                else:
                    # Optionally clean up entries with zero quantity
                    cursor.execute("DELETE FROM portfolio WHERE quantity = 0 AND username = ? AND asset_name = ?", (username, asset))
                    success = True
            conn.commit()
            return success
    except sqlite3.Error as e:
        print(f"Error updating portfolio: {e}")
        return False

# Record transaction in database
def record_transaction_in_db(username, asset, quantity, action):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (username, asset_name, quantity, action, date)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (username, asset, quantity, action))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error recording transaction: {e}")

#update the balance in the database
def update_account_balance(username, amount, action):
    return update_balance_in_db(username, amount, action)

def process_trade(username, asset, quantity, action):
    assets = get_assets()  # Fetch live prices
    asset_price = assets.get(asset)

    if not asset_price:
        print(f"Asset {asset} not found in live prices.")
        return False  # Asset not available

    if action == 'buy':
        total_cost = asset_price * quantity
        account = load_account_from_db(username)  # Get theuser account details
        if account['balance'] < total_cost:
            print(f"Insufficient balance for {username}. Needed: {total_cost}, Available: {account['balance']}")
            return False  # Not enough balance so it throws an error

        if update_balance_in_db(username, total_cost, 'withdraw'): #updates in the database with the buy/sell action
            if update_portfolio_in_db(username, asset, quantity, 'buy'):
                record_transaction_in_db(username, asset, quantity, 'buy')
                return True
            else:
                print(f"Failed to update portfolio for {username} while buying {asset}.")
        else:
            print(f"Failed to withdraw {total_cost} for {username} during buy.")
    
    elif action == 'sell':
        if update_portfolio_in_db(username, asset, quantity, 'sell'):
            total_earnings = asset_price * quantity
            if update_balance_in_db(username, total_earnings, 'deposit'): #updates in the database with the buy/sell action
                record_transaction_in_db(username, asset, quantity, 'sell')
                return True
            else:
                print(f"Failed to deposit earnings for {username} while selling {asset}.") #error 
        else:
            print(f"Failed to update portfolio for {username} while selling {asset}.")

    return False

def adds_acc_from_db(username):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, password, balance FROM accounts WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return {"username": row[0], "password": row[1], "balance": row[2]}
            else:
                print("Username not found.")
                return None
    except sqlite3.Error as e:
        print(f"Error querying database: {e}")
        return None

# Handle client requests from client GUI
def handle_client(client_socket):
    # Loop to handle continuous client requests
    while True:
        try:
            # Receive data from the client
            data = client_socket.recv(1024).decode()
            if not data:  # Exit if no data is received
                break
            # Split the received data into commands
            command = data.split(',')

            # Handle account creation
            if command[0] == 'create':
                username = command[1]
                password = command[2]
                try:
                    balance = float(command[3])  # Ensure balance is a valid number
                except ValueError:
                    # Notify client of an invalid balance
                    client_socket.send("Error: Invalid balance amount.".encode())
                    continue

                # Add the account to the database
                response = adds_acc_from_db(username, password, balance)
                client_socket.send(response.encode())
            
            # Handle login request
            if command[0] == 'login':
                username, password = command[1], command[2]
                account = load_account_from_db(username)  # Retrieve account from the database
                if account and account['password'] == password:
                    client_socket.send("Success: Login successful.".encode())
                else:
                    client_socket.send("Error: Invalid username or password.".encode())
                
            # Handle balance inquiry
            elif command[0] == 'balance':
                username = command[1]
                account = load_account_from_db(username)  # Retrieve account info
                if account:
                    client_socket.send(f"Balance: {account['balance']}".encode())
                else:
                    client_socket.send("Username not found.".encode())

            # Handle deposit requests
            elif command[0] == 'deposit':
                username = command[1]
                try:
                    amount = float(command[2])
                    if amount <= 0:  # Ensure deposit amount is positive
                        raise ValueError("Amount must be a positive number.")
                except ValueError:
                    client_socket.send("Error: Invalid deposit amount. It must be a positive number.".encode())
                    continue

                # Update the balance in the database
                if update_balance_in_db(username, amount, 'deposit'):
                    client_socket.send("Deposit successful.".encode())
                else:
                    client_socket.send("Deposit failed.".encode())

            # Handle withdrawal requests
            elif command[0] == 'withdraw':
                username = command[1]
                try:
                    amount = float(command[2])
                    if amount <= 0:  # Ensure withdrawal amount is positive
                        raise ValueError("Amount must be a positive number.")
                    
                except ValueError:
                    client_socket.send("Error: Invalid withdrawal amount. It must be a positive number.".encode())
                    continue

                # Update the balance in the database
                if update_balance_in_db(username, amount, 'withdraw'):
                    client_socket.send("Withdrawal successful.".encode())
                else:
                    client_socket.send("Withdrawal failed. Insufficient balance or minimum balance constraint violated.".encode())

            # Handle asset purchase requests
            elif command[0] == 'buy':
                username, asset, quantity = command[1], command[2], float(command[3])
                # Process the buy trade
                if process_trade(username, asset, quantity, 'buy'):
                    client_socket.send("Buy successful.".encode())
                else:
                    client_socket.send("Buy failed.".encode())

            # Handle asset sale requests
            elif command[0] == 'sell':
                username, asset, quantity = command[1], command[2], float(command[3])
                # Process the sell trade
                if process_trade(username, asset, quantity, 'sell'):
                    client_socket.send("Sell successful.".encode())
                else:
                    client_socket.send("Sell failed.".encode())

            # Handle asset price request
            elif command[0] == 'assets':
                # Retrieve the latest asset prices
                assets = get_assets()
                client_socket.send(str(assets).encode())  # Send the asset prices

            # Handle portfolio requests
            elif command[0] == 'portfolio':
                username = command[1]
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        cursor = conn.cursor()
                        # Retrieve the user's portfolio
                        cursor.execute("SELECT asset_name, quantity FROM portfolio WHERE username = ?", (username,))
                        portfolio = {row[0]: row[1] for row in cursor.fetchall()}

                    if portfolio:
                        # Calculate the portfolio value
                        assets = get_assets()
                        portfolio_value = {
                            asset: {
                                "quantity": quantity,
                                "value": quantity * assets.get(asset, 0)
                            } for asset, quantity in portfolio.items()
                        }
                        client_socket.send(eval(portfolio_value).encode())
                    else:
                        client_socket.send("Error: Portfolio not found or empty.".encode())
                except sqlite3.Error as e:
                    client_socket.send(f"Error: {e}".encode())
        except Exception as e:
            # Handle unexpected errors
            print(f"Error: {e}")
            break

    # Close the client socket when the session ends
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen(5)
    print("Server is running...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    main()
