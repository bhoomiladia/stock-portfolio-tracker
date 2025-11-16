import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

from utils import validate_inputs
from portfolio import Portfolio

class PortfolioApp:
    def __init__(self, root, portfolio):
        self.root = root
        self.portfolio = portfolio
        
        self.root.title("Stock Portfolio Manager")
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)
        self.style = ttk.Style()
        self.style.theme_use('clam') 
        
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 11))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Total.TLabel', font=('Arial', 14, 'bold'), foreground='#004d00')
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)
        self.style.configure('Add.TButton', background='#4CAF50', foreground='white') # Green
        self.style.map('Add.TButton', background=[('active', '#45a049')])
        self.style.configure('Export.TButton', background='#008CBA', foreground='white') # Blue
        self.style.map('Export.TButton', background=[('active', '#007a9e')])
        self.style.configure('TEntry', font=('Arial', 11))

        self.style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
        self.style.configure("Treeview", font=('Arial', 10), rowheight=25, background="#ffffff")
        self.style.map("Treeview", background=[('selected', '#0078d7')], foreground=[('selected', 'white')])
-
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.paned_window, padding="15 15 15 15", style='TFrame')
        self.paned_window.add(self.left_frame, weight=1) # Give it 40% of the space initially

        self.input_frame = ttk.Frame(self.left_frame, style='TFrame')
        self.input_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(self.input_frame, text="Manage Stocks", style='Header.TLabel').grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 15))

        ttk.Label(self.input_frame, text="Stock Symbol:").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        self.stock_entry = ttk.Entry(self.input_frame, width=20)
        self.stock_entry.grid(row=1, column=1, pady=5, sticky='w')

        ttk.Label(self.input_frame, text="Quantity:").grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        self.quantity_entry = ttk.Entry(self.input_frame, width=20)
        self.quantity_entry.grid(row=2, column=1, pady=5, sticky='w')

        ttk.Label(self.input_frame, text="Price per Share:").grid(row=3, column=0, sticky='w', padx=(0, 10), pady=5)
        self.price_entry = ttk.Entry(self.input_frame, width=20)
        self.price_entry.grid(row=3, column=1, pady=5, sticky='w')
        
        ttk.Label(self.input_frame, text="(Use negative quantity to sell)", font=('Arial', 9, 'italic'), background='#f0f0f0').grid(row=2, column=2, sticky='w', padx=10)

        self.add_button = ttk.Button(self.input_frame, text="Add/Update Stock", command=self.add_stock_action, style='Add.TButton')
        self.add_button.grid(row=4, column=0, columnspan=2, pady=(15, 0), sticky='w')

        self.tree_frame = ttk.Frame(self.left_frame, style='TFrame')
        self.tree_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))

        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("Stock", "Quantity", "Avg. Price", "Total Value"),
            show="headings",
            yscrollcommand=self.tree_scroll.set
        )
        self.tree_scroll.config(command=self.tree.yview)

        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Avg. Price", text="Avg. Price")
        self.tree.heading("Total Value", text="Total Value")

        self.tree.column("Stock", width=100, anchor=tk.W)
        self.tree.column("Quantity", width=80, anchor=tk.CENTER)
        self.tree.column("Avg. Price", width=100, anchor=tk.E)
        self.tree.column("Total Value", width=120, anchor=tk.E)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.summary_frame = ttk.Frame(self.left_frame, style='TFrame')
        self.summary_frame.pack(fill=tk.X, pady=(10, 0))

        self.total_value_var = tk.StringVar(value="Total Portfolio Value: ₹0.00")
        self.total_label = ttk.Label(self.summary_frame, textvariable=self.total_value_var, style='Total.TLabel')
        self.total_label.pack(side=tk.LEFT, anchor='w')

        self.export_button = ttk.Button(self.summary_frame, text="Export to CSV", command=self.export_csv_action, style='Export.TButton')
        self.export_button.pack(side=tk.RIGHT, anchor='e')

        self.right_frame = ttk.Frame(self.paned_window, padding="15 15 15 15", style='TFrame')
        self.paned_window.add(self.right_frame, weight=2) 


        self.fig = Figure(figsize=(6, 5), dpi=100, facecolor='#f0f0f0')
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.right_frame)
        self.toolbar.config(background='#f0f0f0')
        self.toolbar._message_label.config(background='#f0f0f0')
        for button in self.toolbar.winfo_children():
            button.config(background='#f0f0f0')
        self.toolbar.update()

        self.update_ui()

    def add_stock_action(self):
        stock = self.stock_entry.get().upper()
        quantity = self.quantity_entry.get()
        price = self.price_entry.get()

        error_message = validate_inputs(stock, quantity, price)
        if error_message:
            messagebox.showerror("Input Error", error_message)
            return

        try:
            self.portfolio.add_stock(stock.strip(), int(quantity), float(price))

            self.stock_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            
            self.stock_entry.focus()

            self.update_ui()
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def update_ui(self):
        self.update_treeview()
        self.update_total_value()
        self.update_chart()

    def update_treeview(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for _, row in self.portfolio.data.iterrows():
            total_value = row['Quantity'] * row['Price']
            self.tree.insert("", tk.END, values=(
                row['Stock'],
                f"{row['Quantity']:,}", 
                f"₹{row['Price']:,.2f}",
                f"₹{total_value:,.2f}"
            ))

    def update_total_value(self):
        total = self.portfolio.calculate_total_value()
        self.total_value_var.set(f"Total Portfolio Value: ₹{total:,.2f}")

    def update_chart(self):
        self.ax.clear() 
        df = self.portfolio.data

        if df.empty:
            self.ax.text(0.5, 0.5, "No data to display",
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes,
                         fontsize=12, color='gray')
        else:
            values = df["Quantity"] * df["Price"]
            stocks = df["Stock"]
   
            colors = plt.cm.viridis(np.linspace(0, 1, len(stocks)))
            
            self.ax.bar(stocks, values, edgecolor="black", color=colors)

            for i, val in enumerate(values):
                self.ax.text(i, val + (values.max() * 0.01), f"₹{val:,.0f}", 
                             ha='center', fontsize=9, fontweight='bold')

        self.ax.set_title("Portfolio Value by Stock", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Stocks", fontsize=11)
        self.ax.set_ylabel("Total Value (₹)", fontsize=11)
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
        self.ax.set_facecolor('#ffffff')
        
        self.fig.tight_layout(pad=2.0)

        self.canvas.draw()

    def export_csv_action(self):
        if self.portfolio.data.empty:
            messagebox.showinfo("Export Error", "There is no data to export.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Portfolio As..."
        )

        if path:
            try:
                self.portfolio.export_csv(path)
                messagebox.showinfo("Export Successful", f"Portfolio successfully exported to:\n{path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export file: {e}")


def run_gui(portfolio):
    root = tk.Tk()
    app = PortfolioApp(root, portfolio)
    root.mainloop()
