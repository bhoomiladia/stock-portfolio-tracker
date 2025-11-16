def validate_inputs(stock, quantity, price):
    """Validates the user inputs from the GUI."""
    if not stock or not quantity or not price:
        return "Please fill all fields!"

    try:
        # We allow negative quantity for selling stocks
        q = int(quantity)
    except ValueError:
        return "Quantity must be an integer (e.g., 100 or -50)."
        
    try:
        p = float(price)
        if p <= 0:
             return "Price must be a positive number."
    except ValueError:
        return "Price must be a numeric value (e.g., 150.75)."

    if not stock.strip():
        return "Stock symbol cannot be empty."

    return None
