import pandas as pd
import numpy as np

class Portfolio:
    def __init__(self):
        self.data = pd.DataFrame(columns=["Stock", "Quantity", "Price"])

    def add_stock(self, stock, quantity, price):
        """Adds a new stock or updates quantity/price if it already exists."""
        
        # Convert types for consistency
        quantity = int(quantity)
        price = float(price)

        if stock in self.data["Stock"].values:
            # Stock exists, update it
            idx = self.data.index[self.data["Stock"] == stock].tolist()[0]
            
            # Calculate new weighted average price
            old_qty = self.data.at[idx, "Quantity"]
            old_price = self.data.at[idx, "Price"]
            
            new_qty = old_qty + quantity
            
            if new_qty > 0: # Avoid division by zero if removing shares
                new_avg_price = ((old_qty * old_price) + (quantity * price)) / new_qty
            else:
                new_avg_price = 0 # Price is irrelevant if quantity is zero
            
            self.data.at[idx, "Quantity"] = new_qty
            self.data.at[idx, "Price"] = new_avg_price
            
            # Remove stock if quantity is zero or less
            if new_qty <= 0:
                self.data = self.data.drop(idx).reset_index(drop=True)
                
        elif quantity > 0:
            # New stock, add it
            new_entry = pd.DataFrame([[stock, quantity, price]], columns=self.data.columns)
            self.data = pd.concat([self.data, new_entry], ignore_index=True)

    def calculate_total_value(self):
        """Calculates the total value of the portfolio."""
        if self.data.empty:
            return 0
        # Ensure columns are numeric for calculation
        values = np.array(self.data["Quantity"].astype(float)) * np.array(self.data["Price"].astype(float))
        return float(np.sum(values))

    def export_csv(self, path):
        """Exports the portfolio data to a CSV file."""
        if not self.data.empty:
            self.data.to_csv(path, index=False)
