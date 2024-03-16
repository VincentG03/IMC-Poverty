from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import statistics

class Trader:
    
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

            if RSI is not None:
                if RSI <= 40:
                    # Buy Condition
                    if not self.has_active_positions(orders, "BUY"):
                        # No active buy positions, initiate buy
                        print("Initiating buy position")
                        orders.append(BuyOrder(product, 10))  # Initial buy of 10 units
                        
                    elif len(orders) < 20 and traderData != "" and float(traderData_list[-1]) < float(traderData_list[-2]):
                        # Buy 2 units whenever RSI is lower than previous period
                        print("Buying 2 units")
                        orders.append(BuyOrder(product, 2))
                    
                    if RSI >= 60:
                        # Exit all buy positions
                        print("Exiting buy positions")
                        orders = [order for order in orders if order.type != "BUY"]
                
                elif RSI >= 60:
                    # Sell Condition
                    if not self.has_active_positions(orders, "SELL"):
                        # No active sell positions, initiate sell
                        print("Initiating sell position")
                        orders.append(SellOrder(product, 10))  # Initial sell of 10 units
                        
                    elif len(orders) < 20 and traderData != "" and float(traderData_list[-1]) > float(traderData_list[-2]):
                        # Sell 2 units whenever RSI is higher than previous period
                        print("Selling 2 units")
                        orders.append(SellOrder(product, 2))
                    
                    if RSI <= 40:
                        # Exit all sell positions
                        print("Exiting sell positions")
                        orders = [order for order in orders if order.type != "SELL"]
                
                result[product] = orders

                # Update traderData
                if len(traderData) < 15:
                    mid_price = (order_depth.buy_orders[0].price + order_depth.sell_orders[0].price) / 2
                    traderData = traderData + f"{mid_price} "
                else:
                    traderData = " ".join(traderData_list)

        conversions = 1
        return result, conversions, traderData
    
    def calculate_rsi(self, prices, period=14):
        """
        Calculate RSI (Relative Strength Index)
        """
        if len(prices) <= period:
            return None  # Not enough data to calculate RSI
        
        gains = []
        losses = []
        
        # Calculate price changes
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change >= 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        # Calculate average gains and losses
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # Calculate initial RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate subsequent RS and RSI using exponential moving averages (EMAs)
        for i in range(period, len(prices)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def has_active_positions(self, orders, position_type):
        """
        Check if there are active positions of given type
        """
        for order in orders:
            if order.type == position_type:
                return True
        return False
