



product = ["Shells", "Snowball", "Wasabi Root", "Pizza Slice"]
shell_to = {"Pizza Slice": 1.41, "Wasabi Root": 0.61, "Snowball": 2.08, "Shells": 1}
snowball_to = {"Pizza Slice": 0.64, "Wasabi Root": 0.3, "Shells": 0.46, "Snowball": 1}
wasabi_to = {"Pizza Slice": 2.05, "Snowball": 3.26, "Shells": 1.56, "Wasabi Root": 1}
pizza_to = {"Wasabi Root": 0.48, "Snowball": 1.52, "Shells": 0.71, "Pizza Slice": 1}
result = []
trades_to_process = []

for trade1 in product:
    for trade2 in product: 
        for trade3 in product: 
            for trade4 in product: 
                trades_to_process.append([trade1, trade2, trade3, trade4])
                
best_trade = 1
best_sequence = ""

for trades in trades_to_process:
    capital = 1
    current_product = "Shells"
    for next_product in trades: 
        if current_product == "Shells":
            current_product = next_product
            capital = capital * shell_to[next_product] 
        elif current_product == "Snowball":
            current_product = next_product
            capital = capital * snowball_to[next_product]  
        elif current_product == "Wasabi Root":
            current_product = next_product
            capital = capital * wasabi_to[next_product]  
        elif current_product == "Pizza Slice":
            current_product = next_product
            capital = capital * pizza_to[next_product]  
        else: 
            print("ERROR")
    
    #Convert back to seashells 
    if current_product == "Shells":
        capital = capital * shell_to["Shells"]
    if current_product == "Snowball":
        capital = capital * snowball_to["Shells"]
    if current_product == "Wasabi Root":
        capital = capital * wasabi_to["Shells"]
    if current_product == "Pizza Slice":
        capital = capital * pizza_to["Shells"]
        
    if capital > best_trade: 
        best_sequence = trades
        best_trade = capital

print(f"From $1, we can make ${best_trade} with a trade sequence of {best_sequence}")


