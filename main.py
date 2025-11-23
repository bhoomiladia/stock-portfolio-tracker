import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
import requests
import os
import random # For Mock Data
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
# CONFIGURATION
# ==========================================
FILE_NAME = "portfolio.csv"
BASE_URL = "https://api.twelvedata.com/price"

# --- CONFIGURATION TOGGLES ---

API_KEY = os.getenv("TWELVEDATA_API_KEY", API_KEY)
USE_MOCK_DATA = False
# -----------------------------
# List of stocks for the Dropdown
POPULAR_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", 
    "AMD", "INTC", "IBM", "ORCL", "CSCO", "DIS", "NKE", "KO", "PEP", 
    "WMT", "TGT", "COST", "JPM", "BAC", "V", "MA", "PYPL", "BTC/USD"
]

class PortfolioDashboard(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("Pro Stock Tracker v3.0 (Auto-Fill)")
        self.geometry("1200x800")
        
        self.df = self.load_data()
        self.calculated_data = [] 

        self.setup_ui()
        self.refresh_data()

    # ==========================================
    # DATA LAYER
    # ==========================================
    def load_data(self):
        if os.path.exists(FILE_NAME):
            try:
                return pd.read_csv(FILE_NAME)
            except:
                return pd.DataFrame(columns=["Symbol", "Qty", "Buy_Price"])
        return pd.DataFrame(columns=["Symbol", "Qty", "Buy_Price"])

    def save_data(self):
        self.df.to_csv(FILE_NAME, index=False)

    def get_price(self, symbol):
        """Fetches price (Mock or Real)."""
        if USE_MOCK_DATA:
            # Simulate slight randomness based on symbol length to keep it consistent-ish
            base = 100 + (len(symbol) * 10) 
            return round(base + random.uniform(-5, 5), 2)
        
        try:
            params = {'symbol': symbol, 'apikey': API_KEY}
            response = requests.get(BASE_URL, params=params)
            data = response.json()
            if 'price' in data:
                return float(data['price'])
        except:
            pass
        return 0.0

    def calculate_portfolio(self):
        if self.df.empty:
            return [], 0, 0, 0

        rows = []
        inv_total = 0
        curr_total = 0

        for _, row in self.df.iterrows():
            sym = row['Symbol']
            qty = float(row['Qty'])
            buy = float(row['Buy_Price'])
            
            curr = self.get_price(sym)
            if curr == 0: curr = buy 

            inv = qty * buy
            val = qty * curr
            pl = val - inv
            pl_pct = (pl / inv * 100) if inv else 0

            inv_total += inv
            curr_total += val

            rows.append({
                "Symbol": sym,
                "Qty": int(qty),
                "Buy Price": f"${buy:.2f}",
                "Curr Price": f"${curr:.2f}",
                "Invested": inv, 
                "Current Val": val,
                "P/L": pl,
                "P/L %": pl_pct
            })

        pl_total = curr_total - inv_total
        self.calculated_data = rows
        return rows, inv_total, curr_total, pl_total

    # ==========================================
    # UI SETUP
    # ==========================================
    def setup_ui(self):
        # Metrics Header
        self.metrics_frame = ttk.Frame(self, padding=20, bootstyle="secondary")
        self.metrics_frame.pack(fill=X)
        
        self.lbl_invested = ttk.Label(self.metrics_frame, text="Inv: $0", font=("Helvetica", 16))
        self.lbl_invested.pack(side=LEFT, padx=20)
        self.lbl_val = ttk.Label(self.metrics_frame, text="Val: $0", font=("Helvetica", 20, "bold"))
        self.lbl_val.pack(side=LEFT, padx=20)
        self.lbl_pl = ttk.Label(self.metrics_frame, text="P/L: $0", font=("Helvetica", 16))
        self.lbl_pl.pack(side=LEFT, padx=20)

        # Tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.tab_tracker = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_tracker, text="Portfolio Tracker")
        self.setup_tracker_tab()

        self.tab_charts = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_charts, text="Visual Analytics")
        self.setup_chart_tab()

    def setup_tracker_tab(self):
        tool_frame = ttk.Frame(self.tab_tracker, padding=10)
        tool_frame.pack(fill=X)
        
        # CHANGED: "Add Stock" now calls custom_add_dialog
        ttk.Button(tool_frame, text="+ Add Stock", command=self.custom_add_dialog, bootstyle="success").pack(side=LEFT, padx=5)
        ttk.Button(tool_frame, text="Remove Selected", command=self.remove_stock, bootstyle="danger").pack(side=LEFT, padx=5)
        ttk.Button(tool_frame, text="Import CSV", command=self.import_csv, bootstyle="info").pack(side=LEFT, padx=5)
        ttk.Button(tool_frame, text="Refresh Data", command=self.refresh_data, bootstyle="primary-outline").pack(side=RIGHT, padx=5)

        cols = ["Symbol", "Qty", "Buy Price", "Curr Price", "Invested", "Current Val", "P/L", "P/L %"]
        self.tree = ttk.Treeview(self.tab_tracker, columns=cols, show="headings", height=15)
        
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor=CENTER)
            
        sb = ttk.Scrollbar(self.tab_tracker, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)
        sb.pack(side=RIGHT, fill=Y)
        self.tree.pack(fill=BOTH, expand=True)

        self.tree.tag_configure('up', foreground='#00ff00')
        self.tree.tag_configure('down', foreground='#ff4444')

    def setup_chart_tab(self):
        self.chart_frame = ttk.Frame(self.tab_charts)
        self.chart_frame.pack(fill=BOTH, expand=True)
        self.left_chart = ttk.Frame(self.chart_frame)
        self.left_chart.pack(side=LEFT, fill=BOTH, expand=True)
        self.right_chart = ttk.Frame(self.chart_frame)
        self.right_chart.pack(side=RIGHT, fill=BOTH, expand=True)

    # ==========================================
    # LOGIC: REFRESH & CHARTS
    # ==========================================
    def refresh_data(self):
        rows, inv, val, pl = self.calculate_portfolio()
        
        self.lbl_invested.config(text=f"Invested: ${inv:,.0f}")
        self.lbl_val.config(text=f"Value: ${val:,.0f}")
        pl_color = "success" if pl >= 0 else "danger"
        self.lbl_pl.config(text=f"P/L: ${pl:,.2f}", bootstyle=pl_color)

        for i in self.tree.get_children(): self.tree.delete(i)
        
        for r in rows:
            tag = 'up' if r['P/L'] >= 0 else 'down'
            values = (
                r['Symbol'], r['Qty'], r['Buy Price'], r['Curr Price'],
                f"${r['Invested']:,.2f}", f"${r['Current Val']:,.2f}",
                f"${r['P/L']:,.2f}", f"{r['P/L %']:.2f}%"
            )
            self.tree.insert("", END, values=values, tags=(tag,))

        self.draw_charts(rows)

    def draw_charts(self, rows):
        if not rows: return
        df_chart = pd.DataFrame(rows)
        
        # Pie Chart
        for widget in self.left_chart.winfo_children(): widget.destroy()
        fig1, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        fig1.patch.set_facecolor('#2b3e50') 
        ax1.pie(df_chart['Current Val'], labels=df_chart['Symbol'], autopct='%1.1f%%', startangle=90)
        ax1.set_title("Portfolio Allocation", color='white')
        canvas1 = FigureCanvasTkAgg(fig1, self.left_chart)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=BOTH, expand=True)

        # Bar Chart
        for widget in self.right_chart.winfo_children(): widget.destroy()
        fig2, ax2 = plt.subplots(figsize=(5, 4), dpi=100)
        fig2.patch.set_facecolor('#2b3e50')
        ax2.set_facecolor('#2b3e50')
        colors = ['green' if x >= 0 else 'red' for x in df_chart['P/L']]
        ax2.bar(df_chart['Symbol'], df_chart['P/L'], color=colors)
        ax2.set_title("Profit / Loss per Asset", color='white')
        ax2.tick_params(axis='x', colors='white')
        ax2.tick_params(axis='y', colors='white')
        ax2.axhline(0, color='white', linewidth=0.8)
        canvas2 = FigureCanvasTkAgg(fig2, self.right_chart)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=BOTH, expand=True)

    # ==========================================
    # NEW FEATURE: CUSTOM DIALOG WITH DROPDOWN
    # ==========================================
    def custom_add_dialog(self):
        """Creates a popup window with Dropdown and Auto-Price Fill"""
        popup = ttk.Toplevel(self)
        popup.title("Add Stock")
        popup.geometry("350x300")
        
        # Helper to center popup
        x = self.winfo_x() + 100
        y = self.winfo_y() + 100
        popup.geometry(f"+{x}+{y}")

        ttk.Label(popup, text="Select Symbol:", bootstyle="info").pack(pady=(10,0))
        
        # 1. Dropdown (Combobox)
        combo_symbol = ttk.Combobox(popup, values=POPULAR_STOCKS)
        combo_symbol.pack(pady=5, padx=20, fill=X)
        
        ttk.Label(popup, text="Quantity:", bootstyle="info").pack(pady=(10,0))
        entry_qty = ttk.Entry(popup)
        entry_qty.pack(pady=5, padx=20, fill=X)
        entry_qty.insert(0, "1") # Default 1

        ttk.Label(popup, text="Buy Price (Auto-Filled):", bootstyle="info").pack(pady=(10,0))
        entry_price = ttk.Entry(popup)
        entry_price.pack(pady=5, padx=20, fill=X)

        # --- AUTO FILL LOGIC ---
        def on_symbol_select(event):
            selected_sym = combo_symbol.get()
            if selected_sym:
                # Indicate loading
                entry_price.delete(0, END)
                entry_price.insert(0, "Fetching...")
                popup.update()
                
                # Fetch price
                price = self.get_price(selected_sym)
                
                # Update field
                entry_price.delete(0, END)
                entry_price.insert(0, str(price))
        
        # Bind the event (Trigger when user picks from list)
        combo_symbol.bind("<<ComboboxSelected>>", on_symbol_select)
        # -----------------------

        def save_and_close():
            s = combo_symbol.get()
            q = entry_qty.get()
            p = entry_price.get()

            if not s or not q or not p:
                messagebox.showerror("Error", "All fields are required!", parent=popup)
                return

            try:
                new_row = {"Symbol": s.upper(), "Qty": int(q), "Buy_Price": float(p)}
                self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
                self.save_data()
                self.refresh_data()
                popup.destroy() # Close window
                messagebox.showinfo("Success", f"{s} Added!")
            except ValueError:
                messagebox.showerror("Error", "Qty and Price must be numbers", parent=popup)

        ttk.Button(popup, text="ADD TO PORTFOLIO", command=save_and_close, bootstyle="success").pack(pady=20, fill=X, padx=20)

    def remove_stock(self):
        sel = self.tree.selection()
        if not sel: return
        sym = self.tree.item(sel[0])['values'][0]
        self.df = self.df[self.df.Symbol != sym]
        self.save_data()
        self.refresh_data()

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path: return
        try:
            imported_df = pd.read_csv(file_path)
            self.df = pd.concat([self.df, imported_df], ignore_index=True)
            self.save_data()
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = PortfolioDashboard()
    app.mainloop()