import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Initialize portfolio dataframe
portfolio = pd.DataFrame(columns=["Stock", "Quantity", "Price"])

# Add stock function
def add_stock():
    stock = stock_entry.get().strip().upper()
    quantity = quantity_entry.get()
    price = price_entry.get()

    if not stock or not quantity or not price:
        messagebox.showwarning("Input Error", "Please fill all fields!")
        return

    try:
        quantity = int(quantity)
        price = float(price)
    except ValueError:
        messagebox.showerror("Invalid Input", "Quantity must be integer and price must be numeric.")
        return

    global portfolio
    new_entry = pd.DataFrame([[stock, quantity, price]], columns=portfolio.columns)
    portfolio = pd.concat([portfolio, new_entry], ignore_index=True)
    update_table()
    clear_entries()

# Update Treeview
def update_table():
    for row in tree.get_children():
        tree.delete(row)
    for _, row in portfolio.iterrows():
        tree.insert("", "end", values=list(row))

# Clear inputs
def clear_entries():
    stock_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

# Calculate total portfolio value
def calculate_portfolio_value():
    if portfolio.empty:
        messagebox.showinfo("Portfolio", "No data available.")
        return
    values = np.array(portfolio["Quantity"]) * np.array(portfolio["Price"])
    total = np.sum(values)
    messagebox.showinfo("Portfolio Value", f"Total Portfolio Value: ₹{total:,.2f}")

# Export portfolio to CSV
def export_data():
    if portfolio.empty:
        messagebox.showwarning("No Data", "Portfolio is empty!")
        return
    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file:
        portfolio.to_csv(file, index=False)
        messagebox.showinfo("Export Successful", f"Portfolio saved to {file}")

# Show bar chart
def show_chart():
    if portfolio.empty:
        messagebox.showwarning("No Data", "Add some stocks first!")
        return
    plt.figure(figsize=(8, 5))
    plt.bar(portfolio["Stock"], portfolio["Quantity"] * portfolio["Price"], color="skyblue", edgecolor="black")
    plt.title("Portfolio Performance")
    plt.xlabel("Stocks")
    plt.ylabel("Total Value (₹)")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# ---- GUI ----
root = tk.Tk()
root.title("📊 Simple Stock Portfolio Tracker")
root.geometry("700x500")
root.configure(bg="#E8F0FE")

title_label = tk.Label(root, text="Simple Stock Portfolio Tracker", font=("Arial", 18, "bold"), bg="#E8F0FE")
title_label.pack(pady=10)

frame = tk.Frame(root, bg="#E8F0FE")
frame.pack(pady=5)

tk.Label(frame, text="Stock Name:", bg="#E8F0FE", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5)
stock_entry = tk.Entry(frame, width=15)
stock_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Quantity:", bg="#E8F0FE", font=("Arial", 11)).grid(row=0, column=2, padx=5, pady=5)
quantity_entry = tk.Entry(frame, width=10)
quantity_entry.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame, text="Price (₹):", bg="#E8F0FE", font=("Arial", 11)).grid(row=0, column=4, padx=5, pady=5)
price_entry = tk.Entry(frame, width=10)
price_entry.grid(row=0, column=5, padx=5, pady=5)

add_button = tk.Button(root, text="Add Stock", command=add_stock, bg="#0078D7", fg="white", width=15)
add_button.pack(pady=8)

# Treeview for portfolio
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10)
tree = ttk.Treeview(tree_frame, columns=("Stock", "Quantity", "Price"), show="headings", height=10)
tree.heading("Stock", text="Stock")
tree.heading("Quantity", text="Quantity")
tree.heading("Price", text="Price (₹)")
tree.pack()

# Buttons for actions
btn_frame = tk.Frame(root, bg="#E8F0FE")
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="💰 Calculate Value", command=calculate_portfolio_value, bg="#34A853", fg="white", width=18).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="📈 Show Chart", command=show_chart, bg="#F9AB00", fg="black", width=18).grid(row=0, column=1, padx=10)
tk.Button(btn_frame, text="💾 Export CSV", command=export_data, bg="#4285F4", fg="white", width=18).grid(row=0, column=2, padx=10)

root.mainloop()
