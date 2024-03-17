from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import csv

class Trader:
    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input,
        # and outputs a list of orders to be sent
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                
                # Calculate spread
                spread = best_ask - best_bid
                
                # Place buy order at best bid minus spread
                buy_price = best_bid - spread * 0.25  # Adjusting to market making strategy
                buy_quantity = 10  # Adjust according to your strategy
                
                print("BUY", buy_quantity, "x", buy_price)
                orders.append(Order(product, buy_price, buy_quantity))
                
                # Place sell order at best ask plus spread
                sell_price = best_ask + spread * 0.25  # Adjusting to market making strategy
                sell_quantity = 10  # Adjust according to your strategy
                
                print("SELL", sell_quantity, "x", sell_price)
                orders.append(Order(product, sell_price, -sell_quantity))
                
            result[product] = orders
        
        # Return orders and other data
        traderData = "SAMPLE"  # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 1
        return result, conversions, traderData