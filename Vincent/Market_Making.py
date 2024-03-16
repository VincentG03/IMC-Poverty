"""
Strategy: Market Making 

Considerations: 
- Send small order? So they don't just trade with 50% of the qty and have to close out 
- Consider FOK orders to avoid issue above 
- When quoting bid and ask price, it is important that you dont cross over the mid price.


Idea: 
- Check if outstanding positions:
- YES: give the best order to the market to try to close out of that position
- NO: market make both BID and ASK orders 
"""

from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import pandas as pd
import numpy as np
import math 
import string

class Trader:
    
    def run(self, state: TradingState):
        """
        1. Check outstanding positions 
            1.1 No outstanding positions --> Market make 
            1.2 Outstanding positions --> Send order to close position
        """
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        #Set position limits 
        product_limits = {'AMETHYSTS': 15, 'STARFRUIT': 15}

        # Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

            #Find the position limit
            position_limit = self.find_position_limits(product, product_limits)

            #(!!!) There are open positions --> Send orders to attempt to close position
            if state.position[product] != 0:
                qty_to_close = abs(state.position[product])

                if state.position[product] > 0: #SELL to close                    
                    best_bid = list(order_depth.buy_orders.items())[0][0]
                    print("SELL", str(qty_to_close) + "x", best_bid)
                    orders.append(Order(product, best_bid, -qty_to_close))
                    
                else: #BUY to close
                    best_ask = list(order_depth.sell_orders.items())[0][0]
                    print("BUY", str(qty_to_close) + "x", best_ask)
                    orders.append(Order(product, best_ask, qty_to_close))

                result[product] = orders


            #(!!!) There are no open positions --> Send orders to market make
            else:
                #Get the maximum amount of orders to send. There should be no outstanding positions so max is position limit set. 
                qty_to_mm = position_limit
               
                #Get mid price to ensure that our quoted bid and ask price are correct (bid < mid price, ask > mid price)
                mid_price = ((list(order_depth.buy_orders.items())[0][0]) + (list(order_depth.sell_orders.items())[0][0]))/2

                #Quote a better bid price (BUY order) and a better ask price (SELL order)
                my_bid = list(order_depth.buy_orders.items())[0][0] + 1 
                my_ask = list(order_depth.sell_orders.items())[0][0] - 1

                #Check if the order is valid - if not do nothing. 
                if my_bid < mid_price and my_ask > mid_price: 
                    print("SELL", str(qty_to_mm) + "x", my_ask)
                    orders.append(Order(product, my_ask, -qty_to_mm))

                    print("BUY", str(qty_to_mm) + "x", my_bid)
                    orders.append(Order(product, my_bid, qty_to_mm))

                    result[product] = orders


        traderData = "No data needed" 
        
                # Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData
    



    def find_position_limits(self, product, product_limits: dict) -> int:
        """
        For each product, find the position limited set (hard coded).
        """
        if product in product_limits:
            return product_limits[product]
        else: 
            return 20 #Set default position limit to 20