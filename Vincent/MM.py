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



- (!) If we are long, to close out we need to short, to quote a bid price (instead of lifting the ask)
- (!) Update the quote prices to reflect market moving up or down
- (!) Only market make if it is worth the spread (for now, hard code the spread) 


PROBLEM: what if there are no bid or asks? how do determine what to quote at???
"""

from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List


class Trader:
    # Hardcode different sprteads for different products 
    
    def run(self, state: TradingState):
        """
        1. Check outstanding positions 
            1.1 No outstanding positions --> Market make 
            1.2 Outstanding positions --> Send order to close position
        """
        #print("traderData: " + state.traderData)
        #print("Observations: " + str(state.observations))

        #Set position limits 
        product_limits = {'AMETHYSTS': 20, 'STARFRUIT': 20}

        # Orders to be placed on exchange matching engine
        result = {}

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            print(f"|| Buy Orders {product}: " + str(order_depth.buy_orders) + f", Sell Orders {product}: " + str(order_depth.sell_orders) + "||")

            #Determine the position limit (set by IMC)
            position_limit = self.find_position_limits(product, product_limits)

            #(!!!!!!!!) Determine the spread we will trade for this product 
            required_spread = 6 #Hard coded number, only market make if spreads favourable 


            #Print current position
            if len(state.position) != 0:
                print(f"My position {product}: {state.position}")
            else:
                print(f"No open positions {product}")
                
            #Determine mid price to quote around
            mid_price = ((list(order_depth.buy_orders.items())[0][0]) + (list(order_depth.sell_orders.items())[0][0]))/2
            
            #Determine the market's best bid and best ask
            best_bid = list(order_depth.buy_orders.items())[0][0]
            best_ask = list(order_depth.sell_orders.items())[0][0]

            #Determine the spread 
            spread = best_ask - best_bid 

            #Determine my bids and ask that I will send 
            my_bid = best_bid + 1
            my_ask = best_ask - 1 
            # my_bid = best_bid 
            # my_ask = best_ask 

            #(!!!) There are no open positions --> quote orders to MM (max position limit)
            if state.position.get(product, 0) == 0: #If product position = 0 or None (which means we haven't traded it yet)
                """
                1. Market make with the max position limit
                """
                #Get the maximum amount of orders to send. There should be no outstanding positions so max is position limit set. 
                qty_to_mm = abs(position_limit)

                #Check if the order is valid (bid < mid, ask > mid, spread is big enough)
                if my_bid < mid_price and my_ask > mid_price and spread >= required_spread: 
                    print("(MM) Quoting BUY", str(qty_to_mm) + "x", product, my_bid)
                    orders.append(Order(product, my_bid, qty_to_mm))

                    print("(MM) Quoting SELL", str(qty_to_mm) + "x", product, my_ask)
                    orders.append(Order(product, my_ask, -qty_to_mm))

                    result[product] = orders

            #(!!!) There are open positions --> quote orders to MM + quote orders to close positions (max position - oustanding position)
            else:
                """
                1. Market make with remaining position (max position - current position) 
                2. Quote orders to try to close current positions 
                """
                #Determine max quantity to market max     
                if state.position.get(product) > 0: #We are long
                    qty_remaining = abs(position_limit) - state.position.get(product)
                else: 
                    qty_remaining = abs(position_limit) + state.position.get(product)
                
                #Market make the remaining position limit. Check if the order is valid (bid < mid, ask > mid, spread is big enough)
                if my_bid < mid_price and my_ask > mid_price and spread >= required_spread: 
                    print("(MM) Quoting BUY", str(qty_remaining) + "x", product, my_bid)
                    orders.append(Order(product, my_bid, qty_remaining))

                    print("(MM) Quoting SELL", str(qty_remaining) + "x", product, my_ask)
                    orders.append(Order(product, my_ask, -qty_remaining))
                
                
                
                
                #Get the position to close out of. 
                qty_to_close = state.position.get(product) #Only continue if the asset has a current open position.
                
                #Send orders to try to close out of position
                if state.position[product] > 0: #Quote a ASK at best price                   
                    print("(CLOSE) Quoting SELL", str(qty_to_close) + "x", product, my_ask)
                    orders.append(Order(product, my_ask, -abs(qty_to_close)))
                    
                else: #Quote a BID at best price 
                    print("(CLOSE) Quote BUY", str(qty_to_close) + "x", product, my_bid)
                    orders.append(Order(product, my_bid, abs(qty_to_close)))

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
        
        
    def find_required_spread(self, product, traderData):
        """
        For a particular product, find the spread we require before we market make.
        """
        pass