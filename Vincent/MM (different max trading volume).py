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

133700, we were quoting a SELL to close out of MM position. But we send SELL order at BELOW mid price.



"""

from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle


class Trader:
    # Figure out the trend of the market, trade in larger quantities when its favourable ( we were long, then market dropped, then we had to close out at a loss)
    # Instead of rejecting if the trade is bad, can increase my spread then send order again (unlikely to be executed but if they do we get big profit)
    # need to add in something when there is no orders on one side. 
    # If best bid/ask is low volume, instead of beating them by 1, just match them.
    
    
    # Market make by default 
    # If the spread is not good enough 
    # Check order book volume 
    # If it is low enough, then match orders.
    
    
    
    def run(self, state: TradingState):
        """
        1. Check outstanding positions 
            1.1 No outstanding positions --> Market make 
            1.2 Outstanding positions --> Send order to close position
        """
        # Orders to be placed on exchange matching engine
        state.toJSON()
        result = {}
        
        #Retrieve data passed on from last round
        traderData = state.traderData 
        if traderData != "":
            traderData = jsonpickle.decode(traderData)

        #Repeat trading logic for each product
        for product in state.order_depths:
            """
            ===================================================================================
                                Setting up parameters and required variables
            ===================================================================================
            """
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            print(f"|| Buy Orders {product}: " + str(order_depth.buy_orders) + f", Sell Orders {product}: " + str(order_depth.sell_orders) + "||")

            #Determine the position limit (set by IMC)
            position_limit = self.find_position_limits(product)

            #Calculate the market's best bid and best ask
            best_bid = list(order_depth.buy_orders.items())[0][0]
            best_ask = list(order_depth.sell_orders.items())[0][0]
            #print(f"Market bid {best_bid}, Market ask {best_ask}")

            #Calculate the spread + add to traderData (to calculate avg spread)
            current_spread = best_ask - best_bid 
            traderData = self.append_last_x_spread(traderData, product, current_spread)
            #print(f"Current traderData: {traderData}")
            
            #(!!!!!!!!) Determine the spread we will trade for this product
            required_spread = self.find_required_spread(product, traderData) #Right now, set to find the average (only trading when above average)
            print(f"Required spread for {product}: {required_spread}")
            
            #Calculate mid price to quote around (THIS MAY BE NOT USED IN THE FUTURE)
            mid_price = ((list(order_depth.buy_orders.items())[0][0]) + (list(order_depth.sell_orders.items())[0][0]))/2
            
            #Determine my bids and ask that I will send 
            my_bid, my_ask = self.find_my_bid_my_ask(best_bid, best_ask, order_depth)
            
            #Print current oustanding position
            if len(state.position) != 0:
                print(f"My position: {state.position}")
            else:
                print(f"No open positions")
                
            """
            ===================================================================================
                                                Trading Logic
            ===================================================================================
            """
            #(!!!) There are no open positions --> quote orders to MM (max position limit)
            if state.position.get(product, 0) == 0: #If product position = 0 or None (which means we haven't traded it yet)
                """
                1. Market make with the max position limit
                """
                #Get the maximum amount of orders to send. There should be no outstanding positions so max is position limit set. 
                qty_to_mm = abs(position_limit)

                #Check if the order is valid (bid < mid, ask > mid, spread is big enough)
                if my_bid < mid_price and my_ask > mid_price and current_spread >= required_spread: 
                    print("(MM) Quoting BUY", str(qty_to_mm) + "x", product, my_bid)
                    orders.append(Order(product, my_bid, qty_to_mm))

                    print("(MM) Quoting SELL", str(qty_to_mm) + "x", product, my_ask)
                    orders.append(Order(product, my_ask, -qty_to_mm))

                    result[product] = orders

            #(!!!) There are open positions --> quote orders to MM (max position - oustanding position) + quote orders to close positions 
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
                if my_bid < mid_price and my_ask > mid_price and current_spread >= required_spread: 
                    #print("(MM) Quoting BUY", str(qty_remaining) + "x", product, my_bid)
                    orders.append(Order(product, my_bid, qty_remaining))

                    #print("(MM) Quoting SELL", str(qty_remaining) + "x", product, my_ask)
                    orders.append(Order(product, my_ask, -qty_remaining))
                
                    print(f"(MM) Quoting {product}: bid {qty_remaining}x {my_bid}, ask {qty_remaining}x {my_ask}")
                else: 
                    #If the below executes, it means that we could potentially place it but decide against it cause low spread.
                    print(f"(Outside Required Spread) Could place {my_bid} and {my_ask}")
                
                
                
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

        
        # Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, jsonpickle.encode(traderData)
    


    def find_position_limits(self, product) -> int:
        """
        For each product, find the position limited set (hard coded).
        """
        #Set position limits 
        product_limits = {'AMETHYSTS': 20, 'STARFRUIT': 20}  
         
        if product in product_limits:
            return product_limits[product]
        else: 
            return 20 #Set default position limit to 20 (mostly for backtester purposes -> IMC should always be hard codeded in)
        
        
    def find_required_spread(self, product, traderData):
        """
        For a particular product, find the spread we require before we market make.
        """
        scale_factor = 0.8 #0.8 = This means if average spread is 10, we will trade for 8 spread and above.
        spread_list = traderData["spread_dict"][product]
        
        if product in traderData["spread_dict"]:
            if len(spread_list) == 0:
                print("uh oh big boo boo")
                return   # Return 0 if the list is empty
            else:
                return round(float(sum(spread_list) / len(spread_list)), 2)*scale_factor # 2 decimal places
        
        else: #Hard coding spreads (mostly for backtester)
            return 6 
        
        
    def find_my_bid_my_ask(self, best_bid, best_ask, order_depth):
        """
        Return the bid and ask prices we will quote.
        """
        return best_bid + 1, best_ask - 1
    
    
    def append_last_x_spread(self, traderData, product, current_spread):
        """
        For a particular product, update traderData to contain the last 20 values of it's spread.
        Used to calculate the spread at which we will trade at.
        
        "spread_dict": dictionary with the last x spreads of each product 
        "ema_dict": NOT IMPLEMENTED
        "other_dict": NOT IMPLEMENTED (spare) 
        
        Change "spread_hist" to the simple moving average required.
        """
        spread_hist = 40
        
        if traderData == "": #No products. Initialise ALL required for traderData (not just spread, inc ema and everything)
            traderData = {"spread_dict": {product: [current_spread]}, "ema_dict": [], "other_dict": []} 
        
        elif product in traderData["spread_dict"]: #Product already exists
            if len(traderData["spread_dict"][product]) < spread_hist:
                traderData["spread_dict"][product].append(current_spread)
            else: 
                traderData["spread_dict"][product].pop(0)
                traderData["spread_dict"][product].append(current_spread)
        else: #New product
            traderData["spread_dict"][product] = [current_spread]
        
        return traderData
            

        
        