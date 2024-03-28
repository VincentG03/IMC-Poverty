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
import math


class Trader:
    # Figure out the trend of the market, trade in larger quantities when its favourable ( we were long, then market dropped, then we had to close out at a loss)
    
    # Instead of rejecting if the trade is bad, can increase my spread then send order again (unlikely to be executed but if they do we get big profit)
    
    # need to add in something when there is no orders on one side. 
    
    
    
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
            print("")
            print(f"|| {product}: BUY orders {str(order_depth.buy_orders)}, SELL orders {str(order_depth.sell_orders)} ||")

            #Determine the position limit (set by IMC)
            position_limit = self.find_position_limits(product)



            #Check that bids/asks are NOT empty and calculate the market's best bid and best ask. (Right now, be conservative and just quote lower bid and higher ask. To improve, we could calculate using last prices + average spread)
            market_buy_orders = list(order_depth.buy_orders.items())
            market_sell_orders = list(order_depth.sell_orders.items())
            
            if state.timestamp != 0:
                last_bid = traderData['history_prices_dict'][product][-1][0]
                last_ask = traderData['history_prices_dict'][product][-1][1]

                if len(market_buy_orders) == 0 and len(market_sell_orders) != 0: #Bid orders empty
                    #Bid orders are empty. Use last and current ask price to estimate bid price
                    market_buy_orders = [last_bid - 1]
            
                elif len(market_buy_orders) == 0 and len(market_sell_orders) != 0: #Ask orders empty
                    #Ask orders empty. Use last and current bit price to estimate ask price
                    market_sell_orders = [last_ask + 1]
                    
                elif len(market_buy_orders) == 0 and len(market_sell_orders) == 0: #Both bids and asks empty
                    #Both orders empty.
                    market_buy_orders = [last_bid - 1]
                    market_sell_orders = [last_ask + 1]

            #Add best bid/ask prices to traderData
            traderData = self.append_last_x_prices(traderData, product, market_buy_orders[0], market_sell_orders[0])



            #Determine market's best bid and ask
            best_bid = market_buy_orders[0][0]
            best_ask = market_sell_orders[0][0]
            


            #Calculate the spread + add to traderData (to calculate avg spread)
            current_spread = best_ask - best_bid 
            traderData = self.append_last_x_spread(traderData, product, current_spread)
            #print(f"Current traderData: {traderData}")
            
            #Determine the spread we will trade for this product
            required_spread = math.ceil(self.find_required_spread(product, traderData)) #Right now, set to find the average (only trading when above average)
            print(f"Required spread for {product}: {required_spread}")
            



            #Calculate mid price to quote around (THIS MAY BE NOT USED IN THE FUTURE)
            mid_price = (best_bid + best_ask)/2
            
            #Determine my bids and ask that I will send 
            my_bid, my_ask = self.find_my_bid_my_ask(best_bid, best_ask, market_buy_orders[0], market_sell_orders[0])
            
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
                    orders.append(Order(product, my_bid, qty_to_mm))
                    orders.append(Order(product, my_ask, -qty_to_mm))

                    print(f"(MM) Quoting {product}: bid {qty_to_mm}x {my_bid}, ask {qty_to_mm}x {my_ask}")

                    result[product] = orders
                else:
                    #We can't quote the BEST prices AND meet our required spread. Thus market make and meet our required SPREAD but not the best prices (bots could still trade against it - less likely)
                    my_bid, my_ask = self.find_required_bid_ask(market_buy_orders, market_sell_orders, my_bid, my_ask, required_spread)

                    #Modify our bids and ask (widen them) to meet the spread requirement. Less likely to be filled now.
                    orders.append(Order(product, my_bid, qty_to_mm))
                    orders.append(Order(product, my_ask, -qty_to_mm))

                    print(f"(O.R.S) Quoting {product}: bid {qty_to_mm}x {my_bid}, ask {qty_to_mm}x {my_ask}")
                    # print("Do nothing outside of spread")
 

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
                    orders.append(Order(product, my_bid, qty_remaining))
                    orders.append(Order(product, my_ask, -qty_remaining))
                
                    print(f"(MM) Quoting {product}: bid {qty_remaining}x {my_bid}, ask {qty_remaining}x {my_ask}")
                else:
                    #We can't quote the BEST prices AND meet our required spread. Thus market make and meet our required SPREAD but not the best prices (bots could still trade against it - less likely)
                    my_bid, my_ask = self.find_required_bid_ask(market_buy_orders, market_sell_orders, my_bid, my_ask, required_spread)

                    #Modify our bids and ask (widen them) to meet the spread requirement. Less likely to be filled now.
                    orders.append(Order(product, my_bid, qty_remaining))
                    orders.append(Order(product, my_ask, -qty_remaining))

                    print(f"(O.R.S) Quoting {product}: bid {qty_remaining}x {my_bid}, ask {qty_remaining}x {my_ask}")
                    #print("Do nothing outside of spread")
                
                
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
                
                print(f" ------------------------------{product}----------------------------------")


        print(f"TraderData AFTER: {traderData}")
        
        # Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, jsonpickle.encode(traderData)
    


    def find_position_limits(self, product) -> int:
        """
        For each product, find the position limited set (hard coded).
        """
        #Set position limits 
        product_limits = {'AMETHYSTS': 20, 'STARFRUIT': 20} #I tried restrciting it to 10, it is less profit.
        
        if product in product_limits:
            return product_limits[product]
        else: 
            return 20 #Set default position limit to 20 (mostly for backtester purposes -> IMC should always be hard codeded in)
        
        
    def find_required_spread(self, product, traderData):
        """
        For a particular product, find the spread we require before we market make.

        Change "scale_factor_dict_ to include all items you want to change the scale factor of.
        """
        scale_factor_dict = {'AMETHYSTS': 0.8, 'STARFRUIT': 0.8}
        spread_list = traderData["spread_dict"][product]
        
        if product in scale_factor_dict:
            scale_factor = scale_factor_dict[product]
        else: #Account for backtester        
            scale_factor = 0.8 #0.8 = This means if average spread is 10, we will trade for 8 spread and above.
        
        if product in traderData["spread_dict"]:
            if len(spread_list) == 0:
                print("uh oh big boo boo")
                return   # Return 0 if the list is empty
            else:
                return round(float(sum(spread_list) / len(spread_list)), 2)*scale_factor # 2 decimal places
        
        else: #Hard coding spreads (mostly for backtester)
            return 6 
        
        
    def find_my_bid_my_ask(self, best_bid, best_ask, best_buy_order, best_sell_order):
        """
        Return the bid and ask prices we will quote.
        """
        best_bid_vol = best_buy_order[1]
        best_ask_vol = best_sell_order[1]
        allowed_volume = {0, 1}
        
        #If the best bid and ask volume is low, we can match the price with higher volume to make more profit.
        if best_bid_vol in allowed_volume and abs(best_ask_vol) in allowed_volume: #Both low volume 
            print("(!!!) Both volume low(!!!) ")
            my_bid = best_bid 
            my_ask = best_ask 
        elif best_bid_vol in allowed_volume and abs(best_ask_vol) not in allowed_volume: #Only Bid low volume
            print("(!!!) Only bid volume low(!!!) ")
            my_bid = best_bid
            my_ask = best_ask - 1
        elif best_bid_vol not in allowed_volume and abs(best_ask_vol) in allowed_volume: #Only Ask bolume low 
            print("(!!!) Only ask volume low(!!!) ")
            my_bid = best_bid + 1
            my_ask = best_ask 
        else: #Both high volume 
            print("(!!!) Both volume high(!!!) ")
            my_bid = best_bid + 1
            my_ask = best_ask - 1
        
        return my_bid, my_ask
            
    def find_required_bid_ask(self, market_buy_orders, market_sell_orders, my_bid, my_ask, required_spread):
        """
        This function is called when the spread of the calculated my_bid and my_ask is too small (compared to ) 
        """
        print("(O.R.S) --> calculating new prices")
        #This function should only be called when my bids/ask at lower spread than required spread, so spread_difference should always be < 0. 
        best_bid_vol = market_buy_orders[0][1]
        best_ask_vol = market_sell_orders[0][1]
        spread_difference = required_spread - (my_ask - my_bid)
        print(f"required spread: {required_spread}, my quoted spread: {(my_ask - my_bid)}, difference of: {spread_difference}")

        if spread_difference % 2 == 0: #Even --> split evently between bid and ask
            print(f"Old prices are {my_bid} {my_ask}")
            my_bid = my_bid - spread_difference//2
            my_ask = my_ask + spread_difference//2
            print(f"Even spread - new prices are: {my_bid} {my_ask}")
        else: #Odd --> choose to quote better price for bid or ask.
            if best_bid_vol > best_ask_vol: #Less volume for ask, more likely to be filled if try to match.
                print(f"Old prices are {my_bid} {my_ask}")
                my_bid = my_bid - int(math.ceil(spread_difference/2))
                my_ask = my_ask + int(math.floor(spread_difference/2))
                print(f"Odd spread - new prices are: {my_bid} {my_ask}")
            else: #Less volume for bid, more likely to be filled if we try to match.
                print(f"Old prices are {my_bid} {my_ask}")
                my_bid = my_bid - int(math.floor(spread_difference/2))
                my_ask = my_ask + int(math.ceil(spread_difference/2))
                print(f"Odd spread - new prices are: {my_bid} {my_ask}")          

        return my_bid, my_ask

    def append_last_x_spread(self, traderData, product, current_spread):
        """
        For a particular product, update traderData to contain the last x values of it's spread.
        Used to calculate the spread at which we will trade at.
        
        "spread_dict": dictionary with the last x spreads of each product, {product: [spread_1, spread_2, ...], ...}
        "history_prices_dict": dictionary with the last x best bid and best ask, {product: [[best_bid1, best_ask1], [best_bid2, best_ask2], ...], ...} 
        "other_dict": NOT IMPLEMENTED (spare) 
        
        Change "spread_hist" to the simple moving average required.
        """
        spread_hist = 40
        
        if traderData == "": #No products. Initialise ALL required for traderData (not just spread, inc ema and everything)
            traderData = {"spread_dict": {product: [current_spread]}, "history_prices_dict": {}, "other_dict": {}} 
        
        elif product in traderData["spread_dict"]: #Product already exists
            if len(traderData["spread_dict"][product]) < spread_hist:
                traderData["spread_dict"][product].append(current_spread)
            else: 
                traderData["spread_dict"][product].pop(0)
                traderData["spread_dict"][product].append(current_spread)
        else: #New product
            traderData["spread_dict"][product] = [current_spread]
        
        return traderData
            

    def append_last_x_prices(self, traderData, product, best_buy_order, best_ask_order):
        """
        For a particular product, update traderData to contain the last x values of the best bid and best ask.
        Used to calculate a fair value if a mid price is not given. 

        Change "data_hist" to the number of data periods you want to retain.
        """
        data_hist = 4
        
        if traderData == "": #No products. Initialise ALL required for traderData (not just spread, inc ema and everything)
            traderData = {"spread_dict": {}, "history_prices_dict": {product: [[best_buy_order[0], best_ask_order[0]]] }, "other_dict": {}}
        
        elif product in traderData["history_prices_dict"]:
            if len(traderData["history_prices_dict"][product]) < data_hist:
                traderData["history_prices_dict"][product].append([best_buy_order[0], best_ask_order[0]])
            else: 
                traderData["history_prices_dict"][product].pop(0)
                traderData["history_prices_dict"][product].append([best_buy_order[0], best_ask_order[0]])
        else: #New product 
            traderData["history_prices_dict"][product] = [[best_buy_order[0], best_ask_order[0]]]
        
        return traderData
        
        
        
