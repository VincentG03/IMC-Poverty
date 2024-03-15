from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import statistics

class RsiStrategy:
    
    def run(self, state: TradingState):
        """
        Trading strategy based on RSI (Relative Strength Index)
        """
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        traderData = state.traderData
        traderData_list = []
        if state.traderData != "":
            traderData_list = state.traderData.split(" ")
        
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders = []
            
            # Calculate RSI
            RSI = self.calculate_rsi(traderData_list)
            print(f"RSI: {RSI}")
            
            # Check existing positions
            existing_positions = self.get_existing_positions(order_depth)
            
            if RSI <= 40:
                if not existing_positions["BUY"]:
                    # Buy 10 units immediately
                    print("BUY 10 units immediately")
                    orders.append(Order(product, "BUY", 10))
                    existing_positions["BUY"] = True
                
                # Buy 2 units whenever RSI is lower than previous period
                if len(existing_positions["BUY"]) < 20 and RSI < traderData_list[-1]:
                    print("BUY 2 units")
                    orders.append(Order(product, "BUY", 2))
                    existing_positions["BUY"].append(2)
                
                if RSI >= 60:
                    # Exit all "BUY" positions when RSI is Greater than or equals to 60
                    print("Exit all BUY positions")
                    orders.extend(self.exit_positions(existing_positions["BUY"], product))
                    existing_positions["BUY"] = []

            elif RSI >= 60:
                if not existing_positions["SELL"]:
                    # Sell 10 units immediately
                    print("SELL 10 units immediately")
                    orders.append(Order(product, "SELL", 10))
                    existing_positions["SELL"] = True
                
                # Sell 2 units whenever RSI is higher than previous period
                if len(existing_positions["SELL"]) < 20 and RSI > traderData_list[-1]:
                    print("SELL 2 units")
                    orders.append(Order(product, "SELL", 2))
                    existing_positions["SELL"].append(2)
                
                if RSI <= 40:
                    # Exit all "SELL" positions when RSI is Lesser than or equals to 40
                    print("Exit all SELL positions")
                    orders.extend(self.exit_positions(existing_positions["SELL"], product))
                    existing_positions["SELL"] = []

            result[product] = orders

            # Update traderData
            if len(traderData) < 15:
                mid_price = (order_depth.best_bid + order_depth.best_ask) / 2
                traderData = traderData + f"{mid_price} "
            else:
                traderData = " ".join(traderData_list)

        conversions = 1
        return result, conversions, traderData
    
    def calculate_rsi(self, prices):
        """
        Calculate RSI (Relative Strength Index)
        """
        gains_up = []
        loss_down = []
        
        if len(prices) > 1:
            for i in range(1, len(prices)):
                if prices[i] > prices[i-1]:
                    gains_up.append(prices[i] - prices[i-1])
                elif prices[i] < prices[i-1]:
                    loss_down.append(prices[i-1] - prices[i])
        
            if len(gains_up) > 0 and len(loss_down) > 0:
                avg_gain = statistics.mean(gains_up)
                avg_loss = statistics.mean(loss_down)
                RS = avg_gain / avg_loss
                RSI = 100 - (100 / (1 + RS))
                return RSI
        return 50  # Return 50 if not enough data to calculate RSI
    
    def get_existing_positions(self, order_depth):
        """
        Check existing positions
        """
        existing_positions = {"BUY": [], "SELL": []}
        # Implement logic to check existing positions from order_depth
        # and update existing_positions dictionary accordingly
        return existing_positions
    
    def exit_positions(self, positions, product):
        """
        Exit positions
        """
        exit_orders = []
        for position in positions:
            # Implement logic to create exit orders for each position
            # and append them to exit_orders list
            exit_orders.append(Order(product, "EXIT", position))
        return exit_orders
