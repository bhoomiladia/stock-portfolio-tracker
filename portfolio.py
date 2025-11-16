import pandas as pd
import numpy as np

class Portfolio:
    def __init__(self):
        self.data = pd.DataFrame(columns=["Stock", "Quantity", "Price"])

    def add_stock(self, stock, quantity, price):
        
        
        quantity = int(quantity)
        price = float(price)

        if stock in self.data["Stock"].values:
        
            idx = self.data.index[self.data["Stock"] == stock].tolist()[0]
            
        
            old_qty = self.data.at[idx, "Quantity"]
            old_price = self.data.at[idx, "Price"]
            
            new_qty = old_qty + quantity
            
            if new_qty > 0: 
                new_avg_price = ((old_qty * old_price) + (quantity * price)) / new_qty
            else:
                new_avg_price = 0 
            
            self.data.at[idx, "Quantity"] = new_qty
            self.data.at[idx, "Price"] = new_avg_price
            
           
            if new_qty <= 0:
                self.data = self.data.drop(idx).reset_index(drop=True)
                
        elif quantity > 0:
            
            new_entry = pd.DataFrame([[stock, quantity, price]], columns=self.data.columns)
            self.data = pd.concat([self.data, new_entry], ignore_index=True)

    def calculate_total_value(self):
        """Calculates the total value of the portfolio."""
        if self.data.empty:
            return 0
       
        values = np.array(self.data["Quantity"].astype(float)) * np.array(self.data["Price"].astype(float))
        return float(np.sum(values))

    def export_csv(self, path):
       
        if not self.data.empty:
            self.data.to_csv(path, index=False)
