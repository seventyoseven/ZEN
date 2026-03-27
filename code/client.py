import socket
import tkinter as tk
import time
from tkinter import messagebox, scrolledtext
from tkinter.font import Font
from PIL import Image, ImageTk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests

DB_PATH = r"C:\Users\Eshaal\Downloads\CW2_CST1510\db\investment_platform.db"
# run this in cmd 
# cd C:\Users\Eshaal\Downloads\CW2_CST1510\Code
# python server.py

# Defining the local server and the host
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 5555

#this function holds the live prices for Bitcoin and Ethereum
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
#this one stores the value for silver and gold - live prices
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
#this updates the lives prices and calls them out together
def get_live_prices():
    return {
        "Bitcoin": crypto("bitcoin"),
        "Ethereum": crypto("ethereum"),
        "Gold": get_precious_metal_price('XAU', 'USD', '2f00eab563125757bc52895f887cc7b4'),  # Predefined price for Gold
        "Silver": get_precious_metal_price('XAG', 'USD','2f00eab563125757bc52895f887cc7b4')
        # Add other assets if needed
    }
#to either get predefined prices if live prices dont work
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

#button changes colour whrn hovered upon
def on_enter(event):
    event.widget['background'] = '#CD7F32'  #copper
    event.widget['foreground'] = 'black'     # turn black
#Function to revert the button color when the mouse leaves
def on_leave(event):
    event.widget['background'] = '#402d1d'  #dark brownish colour
    event.widget['foreground'] = 'white'
#Function to send requests to the server
def send_request(request):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
            client_socket.send(request.encode())
            client_socket.settimeout(5)  # Timeout after 5 seconds
            response = client_socket.recv(1024).decode()
            return response
    except socket.timeout:
        return "Error: Server did not respond in time."
    except ConnectionRefusedError:
        return "Error: Unable to connect to the server."
    except Exception as e:
        return f"An error occurred: {e}"
#function to log in into the crypto platform
def login(username, password):
    response = send_request(f"login,{username},{password}")
    if "Success" in response:
        messagebox.showinfo("Login Status", "Login successful!")
        open_main_menu(username)
        root.withdraw()
    else:
        messagebox.showerror("Login Failed", "Login failed. Please check your username or password.")
#Function to open the main menu after a successful login
def open_main_menu(username):
    main_menu_window = tk.Toplevel()  # Create a new top-level window
    main_menu_window.geometry("800x460")  # Example dimensions
    main_menu_window.title(f"Main Menu - {username}")
    main_menu_window.configure(bg="#2C2A2A")

    # Load and display the image
    # Create a frame for the image on the right
    image_frame = tk.Frame(main_menu_window, bg="#2C2A2A")
    image_frame.pack(side=tk.RIGHT, padx=20, pady=20, fill=tk.BOTH, expand=True)

    # Load and display the image
    img = Image.open(r"C:\Users\Eshaal\Downloads\CW2_CST1510\images\bgbit.jpg")
    img = img.resize((600, 430), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    img_label = tk.Label(image_frame, image=img_tk, bg="#2C2A2A")
    img_label.image = img_tk
    img_label.pack(fill=tk.BOTH, expand=True)
    # Button hover color change functions
    def on_enterr(event):
        event.widget['background'] = '#8B7E66'  # dusty rose
        event.widget['foreground'] = 'white'     # Turn text black

    def on_leavee(event):
        event.widget['background'] = '#2C3E50'  # midnight blue
        event.widget['foreground'] = 'white'

    label_font = ("Georgia", 16)  # Font family and 

    def open_view_balance():
        view_balance(username)

    def open_view_assets():
        view_assets()

    def open_view_portfolio():
        view_portfolio(username)

    def open_deposit():
        deposit(username)

    def open_withdraw():
        withdraw(username)

    def open_buy_sell():
        buy_sell(username)
    
    def plot_graph():
        LivePriceApp()

    # Buttons with hover effects
    b = tk.Button(main_menu_window, text="View Balance", command=open_view_balance, font=label_font)
    b.pack(pady=10, anchor="w")
    b.bind("<Enter>", on_enterr)
    b.bind("<Leave>", on_leavee)

    a = tk.Button(main_menu_window, text="View Assets", command=open_view_assets, font=label_font)
    a.pack(pady=10, anchor="w")
    a.bind("<Enter>", on_enterr)
    a.bind("<Leave>", on_leavee)

    p = tk.Button(main_menu_window, text="View Portfolio", command=open_view_portfolio, font=label_font)
    p.pack(pady=10, anchor="w")
    p.bind("<Enter>", on_enterr)
    p.bind("<Leave>", on_leavee)

    d = tk.Button(main_menu_window, text="Deposit Funds", command=open_deposit, font=label_font)
    d.pack(pady=10, anchor="w")
    d.bind("<Enter>", on_enterr)
    d.bind("<Leave>", on_leavee)

    w = tk.Button(main_menu_window, text="Withdraw Funds", command=open_withdraw, font=label_font)
    w.pack(pady=10, anchor="w")
    w.bind("<Enter>", on_enterr)
    w.bind("<Leave>", on_leavee)

    bs = tk.Button(main_menu_window, text="Buy/Sell Assets", command=open_buy_sell, font=label_font)
    bs.pack(pady=10, anchor="w")
    bs.bind("<Enter>", on_enterr)
    bs.bind("<Leave>", on_leavee)

    pl = tk.Button(main_menu_window, text="View Graph", command=plot_graph, font=label_font)
    pl.pack(pady=10, anchor="w")
    pl.bind("<Enter>", on_enterr)
    pl.bind("<Leave>", on_leavee)
#this is for viewing the balance of each user, depends on which one you logged in as
def view_balance(username):
    balance_window = tk.Toplevel()
    balance_window.title("View Account Balance")
    balance_window.configure(bg="lightblue")
    balance_window.geometry("500x400")

    output_widget = tk.Label(balance_window, text="Fetching balance...", width=60, height=10, bg="#8B7E66")
    output_widget.pack()

    response = send_request(f"balance,{username}")
    if response.startswith("Error"):
        output_widget.config(text=f"Error: {response}")
    else:
        output_widget.config(text=f"Account Balance: ${response}",font=label_font_p)

def view_assets():
    assets_window = tk.Toplevel()
    assets_window.title("View Assets")
    assets_window.geometry("400x400")
    assets_window.configure(bg="#2C2A2A")

    canvas = tk.Canvas(assets_window, width=400, height=400, bg="#2C2A2A", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Load and display the image as the background
    og_img = Image.open(r"C:\Users\Eshaal\Downloads\CW2_CST1510\images\sea.jpg")
    rs_img = og_img.resize((400, 400))  # Resize if needed
    bg_image = ImageTk.PhotoImage(rs_img)
    canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)
    
    # Create a font object to specify font size
    large_font = Font(family="Arial", size=12)  # Choose a suitable size
    # Create the output text area with the large font
    output_widget = scrolledtext.ScrolledText(assets_window, width=40, height=15, bg="#F0F0F0", wrap=tk.WORD, font=large_font)
    output_middle = canvas.create_window(200, 200, window=output_widget)  # Position at the center of the canvas
    canvas.image = bg_image

    response = send_request("assets")
    if response.startswith("Error"):
        output_widget.insert(tk.END, f"{response}\n")
    else:
        assets = eval(response)  # assuming response is a valid dictionary-like string
        for asset, price in assets.items():
            output_widget.insert(tk.END, f"{asset}: ${price}\n")
    output_widget.insert(tk.END, '-'*30 + '\n')

def view_portfolio(username):
    portfolio_window = tk.Toplevel()
    portfolio_window.title("Your Portfolio")
    portfolio_window.configure(bg="#2C2A2A")
    portfolio_window.geometry("400x400")

    # Create a Canvas to manage layering
    canvas = tk.Canvas(portfolio_window, width=400, height=400, bg="#2C2A2A", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Load and display the image as the background
    og_img = Image.open(r"C:\Users\Eshaal\Downloads\CW2_CST1510\images\artbg.jpg")
    rs_img = og_img.resize((400, 400))  # Resize if needed
    bg_image = ImageTk.PhotoImage(rs_img)
    canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)

    # Keep a reference to the image
    canvas.image = bg_image

    # Add the scrolled text widget on top of the image
    output_widget = scrolledtext.ScrolledText(portfolio_window, width=48, height=15, bg="#F0F0F0", wrap=tk.WORD)
    output_widget.window = canvas.create_window(200, 200, window=output_widget)

    # Fetch portfolio data directly from the client-side database
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT asset_name, quantity FROM portfolio WHERE username = ?", (username,))
            portfolio = {row[0]: row[1] for row in cursor.fetchall()}
            
            if portfolio:
                assets = get_assets()
                portfolio_value = {
                    asset: {
                        "quantity": quantity,
                        "value": quantity * assets.get(asset, 0)
                    } for asset, quantity in portfolio.items()
                }

                output_widget.insert(tk.END, f"{username}'s Portfolio Data:\n")
                for asset, details in portfolio_value.items():
                    output_widget.insert(
                        tk.END, 
                        f"Asset: {asset}, Quantity: {details['quantity']}, Value: {details['value']:.2f}\n"
                    )
            else:
                output_widget.insert(tk.END, "No Assets bought yet.\n")

    except sqlite3.Error as db_error:
        output_widget.insert(tk.END, f"Database error occurred: {db_error}\n")

    except Exception as e:
        output_widget.insert(tk.END, f"An unexpected error occurred: {e}\n")

def deposit(username):
    deposit_window = tk.Toplevel()
    deposit_window.title("Deposit Funds")
    deposit_window.geometry("400x400")
    deposit_window.configure(bg="#2C2A2A")

    canvas = tk.Canvas(deposit_window, width=400, height=400, bg="#2C2A2A", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Load and display the image as the background
    og_img = Image.open(r"C:\Users\Eshaal\Downloads\CW2_CST1510\images\candle.jpg")
    rs_img = og_img.resize((400, 400))  # Resize if needed
    bg_image = ImageTk.PhotoImage(rs_img)
    canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)

    # Keep a reference to the image
    canvas.image = bg_image
    
    tk.Label(canvas, text="Amount to deposit:", font=label_font_p).pack(pady=10)
    amount_entry = tk.Entry(canvas,font=label_font)
    amount_entry.pack(pady=10)

    def submit_deposit():
        try:
            amount = float(amount_entry.get())
            if amount <= 0:
                raise ValueError("The amount must be positive.")
            response = send_request(f"deposit,{username},{amount}")
            messagebox.showinfo("Deposit Response", response)
            deposit_window.withdraw()
        except ValueError as ve:
            messagebox.showerror("Input Error", f"Invalid amount entered: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Please enter a valid amount consisting of numbers: {e}")


    dep = tk.Button(canvas, text="Submit", command=submit_deposit, font=button_font)
    dep.pack(pady=10)
    dep.bind("<Enter>",on_enter)
    dep.bind("<Leave>",on_leave)

def withdraw(username):
    withdraw_window = tk.Toplevel()
    withdraw_window.geometry("400x400")
    withdraw_window.title("Withdraw Funds")
    withdraw_window.configure(bg="#2C2A2A")

    # Create a Canvas to manage layering
    canvas = tk.Canvas(withdraw_window, width=400, height=400, bg="#2C2A2A", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Load and display the image as the background
    og_img = Image.open(r"C:\Users\Eshaal\Downloads\CW2_CST1510\images\candle.jpg")
    rs_img = og_img.resize((400, 400))  # Resize if needed
    bg_image = ImageTk.PhotoImage(rs_img)
    canvas.create_image(0, 0, anchor=tk.NW, image=bg_image)

    # Keep a reference to the image
    canvas.image = bg_image

    tk.Label(canvas, text="Amount to withdraw:",font=label_font_p).pack(pady=10)
    amount_entry = tk.Entry(canvas,font=label_font)
    amount_entry.pack(pady=10)

    def submit_withdrawal():
        try:
            amount = float(amount_entry.get())
            if amount <= 0:
                raise ValueError("The amount must be positive.")
            response = send_request(f"withdraw,{username},{amount}")
            messagebox.showinfo("Withdraw Response", response)
            withdraw_window.withdraw()
        except ValueError as ve:
            messagebox.showerror("Input Error", f"Invalid amount entered: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"Please enter a valid amount consisting of numbers! {e}")


    wi= tk.Button(canvas, text="Submit", command=submit_withdrawal,font=button_font)
    wi.pack(pady=10)
    wi.bind("<Enter>",on_enter)
    wi.bind("<Leave>",on_leave)

def buy_sell(username):
    trade_window = tk.Toplevel()
    trade_window.title("Buy/Sell Assets")
    trade_window.geometry("400x400")
    trade_window.configure(bg="#2C2A2A")

    tk.Label(trade_window, text="Asset name:",font=label_font_p).pack(pady=10)
    asset_entry = tk.Entry(trade_window,font=label_font_p)
    asset_entry.pack(pady=10)

    tk.Label(trade_window, text="Quantity:",font=label_font).pack(pady=10)
    quantity_entry = tk.Entry(trade_window,font=label_font)
    quantity_entry.pack(pady=10)

    def submit_trade(action):
        asset = asset_entry.get()
        quantity = float(quantity_entry.get())
        response = send_request(f"{action},{username},{asset},{quantity}")
        messagebox.showinfo(f"{action.capitalize()} Response", response)

    abuys =tk.Button(trade_window, text="Buy", command=lambda: submit_trade("buy"),font=button_font,bg="#800020",fg="white")
    abuys.pack(pady=10)
    abuys.bind("<Enter>",on_enter)
    abuys.bind("<Leave>",on_leave)
    asells= tk.Button(trade_window, text="Sell", command=lambda: submit_trade("sell"),font=button_font,bg="#800020",fg="white")
    asells.pack(pady=10)
    asells.bind("<Enter>",on_enter)
    asells.bind("<Leave>",on_leave)

def on_login():
    username = username_entry.get()
    password = password_entry.get()
    login(username, password)

def create_account_window():
    create_window = tk.Toplevel()
    create_window.title("Create Account")
    create_window.geometry("800x400")
    create_window.configure(bg="#2C2A2A")

    tk.Label(create_window, text="Username:", bg="#77815C", font=label_font, fg="white").pack(pady=10)
    username_entry = tk.Entry(create_window, font=16)
    username_entry.pack(pady=5)

    tk.Label(create_window, text="Password:", bg="#77815C", font=label_font, fg="white").pack(pady=10)
    password_entry = tk.Entry(create_window, show="*", font=16)
    password_entry.pack(pady=5)

    def submit_account():
        # Retrieve values from the entry fields
        username = username_entry.get()
        password = password_entry.get()

        # Validate inputs
        if not username or not password:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        def pass_check(password):
            if (
                len(password) < 8 or
                not any(char.isdigit() for char in password) or
                not any(char.isupper() for char in password) or
                not any(char in "!@#$%^&*()-_=+[{]}|;:'\",<.>/?`~" for char in password)
            ):
                return False, (
                    "Password must be at least 8 characters long, include at least one digit, "
                    "one uppercase letter, and one special character!"
                )
            return True, ""

        #calling password check for creating account
        valid, error_message = pass_check(password)
        if not valid:
            messagebox.showerror("Error", error_message)
            return

        # Save to the database
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                balance = float(1000)
                cursor.execute(
                    "INSERT INTO accounts(username, password, balance) VALUES (?, ?, ?)",
                    (username, password, balance)
                )
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully!")
                create_window.destroy()  # Close the window after successful creation
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {e}")

    submit =tk.Button(create_window, text="Submit", command=submit_account, bg="#77815C", font=label_font, fg="white")
    submit.pack(pady=65,padx=300)
    submit.bind("<Enter>",on_enter)
    submit.bind("<Leave>",on_leave)

# GUI with Tkinter
class LivePriceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Live Price Tracker")
        self.geometry("800x600")
        
        # Setup matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Prices storage for graph
        self.time_points = []
        self.bitcoin_prices = []
        self.ethereum_prices = []
        self.gold_prices = []
        self.silver_prices = []

        # Start the update loop
        self.update_graph()

    def update_graph(self):
        prices = get_live_prices()
        
        if all(value is not None for value in prices.values()):
            # Append new data
            current_time = time.strftime('%H:%M:%S')
            self.time_points.append(current_time)
            self.bitcoin_prices.append(prices["Bitcoin"])
            self.ethereum_prices.append(prices["Ethereum"])
            self.gold_prices.append(prices["Gold"])
            self.silver_prices.append(prices["Silver"])

            # Limit data points to avoid clutter
            if len(self.time_points) > 20:
                self.time_points.pop(0)
                self.bitcoin_prices.pop(0)
                self.ethereum_prices.pop(0)
                self.gold_prices.pop(0)
                self.silver_prices.pop(0)

            # Clear and redraw the graph
            self.ax.clear()
            self.ax.plot(self.time_points, self.bitcoin_prices, label="Bitcoin (USD)")
            self.ax.plot(self.time_points, self.ethereum_prices, label="Ethereum (USD)")
            self.ax.plot(self.time_points, self.gold_prices, label="Gold (USD)")
            self.ax.plot(self.time_points, self.silver_prices, label="Silver (USD)")
            self.ax.set_title("Live Prices")
            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("Price (USD)")
            self.ax.legend()
            self.ax.grid(True, linestyle="--", alpha=0.5)
            self.fig.autofmt_xdate()
            self.ax.relim()
            self.ax.autoscale_view()

            # Redraw the canvas
            self.canvas.draw()

        # Schedule the next update
        self.after(5000, self.update_graph)  # Update every 5 seconds


# Main GUI window
root = tk.Tk()
root.title("Crypto Investment Platform")
root.geometry("873x400")
root.configure(bg="#2C2A2A")  # Dark Brown background

ffxv = Image.open(r"C:\Users\Eshaal\Downloads\CW2_CST1510\images\ffxvn.png")
# Convert the image to a format that Tkinter can use
bg_image = ImageTk.PhotoImage(ffxv)

# Create a label to hold the background image
background_label = tk.Label(root, image=bg_image)
background_label.place(relwidth=1, relheight=1)  # Make the image fill the window

# Load and display the image
original_img = Image.open(r"C:\Users\Eshaal\Downloads\CW2_CST1510\images\book.jpg")
resized_img = original_img.resize((900, 150))  # Resize if needed
img = ImageTk.PhotoImage(resized_img)
img_label = tk.Label(root, image=img, bg="#2C2A2A")
img_label.grid(row=0, column=0, columnspan=6)  # Use `grid` for layout
img_label.image = img  # Keep a reference to the image object

# Labels and Entry Widgets with Bigger Font
label_font = ("Georgia", 16)  # Font family and size
label_font_p = ("Georgia", 17)
entry_font = ("Georgia", 14)  # Font for entry fields
button_font = ("Georgia", 16, "bold")  # Font for buttons
label_wel = ("Georgia",23, "italic")
label_sub = ("Georgia", 16, "italic")

welcome_label = tk.Label(root, text="Welcome to the Crypto Investment Platform", font=label_wel, fg="Burlywood3", bg="#2C2A2A")
welcome_label.place(relx=0.5, rely=0.2, anchor="center")  # Centered at 20% vertical position

subtext_label = tk.Label(root, text="Please log in with your username and password", font=label_sub, fg="#CD7F32", bg="#2C2A2A")
subtext_label.place(relx=0.5, rely=0.3, anchor="center")  # Centered below the welcome label

tk.Label(root, text="Username:", bg="#402d1d", font=label_font, fg="white").grid(row=1, column=0, padx=0, pady=25, sticky="e")
username_entry = tk.Entry(root, font=entry_font)
username_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Password:", bg="#402d1d", font=label_font_p, fg="white").grid(row=2, column=0, padx=0, pady=5, sticky="e")
password_entry = tk.Entry(root, show="*", font=entry_font)
password_entry.grid(row=2, column=1, padx=10, pady=10)

logins = tk.Button(root, text="Login", command=on_login, bg="#402d1d", font=button_font, fg="white")
logins.grid(row=4, column=0, pady=45, padx=5)
logins.bind("<Enter>", on_enter)
logins.bind("<Leave>", on_leave)

signups = tk.Button(root, text="Sign Up", command=create_account_window, bg="#402d1d", font=button_font, fg="white")
signups.grid(row=4, column=5, pady=5)
signups.bind("<Enter>",on_enter)
signups.bind("<Leave>",on_leave)

root.mainloop()
