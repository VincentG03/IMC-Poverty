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
import pandas as pd
import numpy as np

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
            print(f" ------------------------------{product}----------------------------------")

            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            print("")
            print(f"|| {product}: BUY orders {str(order_depth.buy_orders)}, SELL orders {str(order_depth.sell_orders)} ||")

            #Determine the position limit (set by IMC)
            position_limit = self.find_position_limits(product)


            """
            Determine best market bid/ask + account for empty bid/asks.
            """
            #Check that bids/asks are NOT empty and calculate the market's best bid and best ask. (Right now, be conservative and just quote lower bid and higher ask. To improve, we could calculate using last prices + average spread)
            market_buy_orders = list(order_depth.buy_orders.items())
            market_sell_orders = list(order_depth.sell_orders.items())

            if state.timestamp != 0:
                last_bid = traderData['history_prices_dict'][product][-1][0]
                last_ask = traderData['history_prices_dict'][product][-1][1]

                #1 is an arbitrary number. We could find the average best bid/ask volume for a better estimate. Number should be small however to represent low interest.
                if len(market_buy_orders) == 0 and len(market_sell_orders) != 0: #Bid orders empty
                    #Bid orders are empty. Use last and current ask price to estimate bid price
                    market_buy_orders = [last_bid - 1, 1]
            
                elif len(market_buy_orders) == 0 and len(market_sell_orders) != 0: #Ask orders empty
                    #Ask orders empty. Use last and current bit price to estimate ask price
                    market_sell_orders = [last_ask + 1, 1]
                    
                elif len(market_buy_orders) == 0 and len(market_sell_orders) == 0: #Both bids and asks empty
                    #Both orders empty.
                    market_buy_orders = [last_bid - 1, 1]
                    market_sell_orders = [last_ask + 1, 1]

            #Add best bid/ask prices to traderData
            traderData = self.append_last_x_bid_ask_prices(traderData, product, market_buy_orders[0], market_sell_orders[0])

            #Determine market's best bid and ask
            best_bid = market_buy_orders[0][0]
            best_ask = market_sell_orders[0][0]


            """
            Calculate the required_spread for this product and this time period.
            """
            #Calculate the spread + add to traderData (to calculate avg spread)
            current_spread = best_ask - best_bid 
            traderData = self.append_last_x_spread(traderData, product, current_spread)
            
            #Determine the spread we will trade for this product
            required_spread = math.ceil(self.find_required_spread(product, traderData)) #Right now, set to find the average (only trading when above average)
            print(f"Required spread for {product}: {required_spread}")


            """
            Calculate the mid_price for valid quote comparison.
            """
            #Calculate mid price to quote around 
            mid_price = (best_bid + best_ask)/2            
            
            #Append the weighted mid price to traderData to use to calculate EMA later.
            traderData = self.append_last_x_midprice(traderData, product, market_buy_orders, market_sell_orders)
            
            
            """
            Calculate the EMA and Standard Deviation and determine the upper and lower bounds for this product and time period.
            """
            #Calculate the EMA for this time period
            ema = self.find_ema(traderData, product)
            print(f"Mid price: {mid_price}")
            print(f"Ema: {ema}")
            
            #Find standard deviation
            std_dev =self.find_standard_deviation(traderData, product)
            upper_bound = ema + 1.5*std_dev
            lower_bound = ema - 1.5*std_dev
            print(f"lower: {lower_bound}")
            print(f"upper: {upper_bound}")
                

            """
            Calculate the average, for trend prediction
            Currently uses 15 data points
            """
            avg_hist = 15
            average = self.avg(order_depth)
            traderData = self.append_last_x_avg(traderData, product, average, avg_hist)   # update traderData to include this timestep's average
            
            
            """
            Use linear regression to calculate trend
            """
            # currently 15 vals
            
            if len(traderData["avg"][product]) >= avg_hist: # must check there is at least 15 data points
                x = [i for i in range(avg_hist)]
                y = traderData["avg"][product]
                gradient, c = np.polyfit(np.array(x), np.array(y), 1)   # finding lin reg equation
                # Predicting next time step
                next_avg_price = gradient * (avg_hist + 1) + c
                diff_lst = []
                # calculating SD from our lin reg - needed to approximate our margin or error
                for i in range(len(traderData["avg"][product])):
                    curr_avg = traderData["midprice_dict"][product][-i -1]
                    c_lin_reg = gradient * (avg_hist - i) + c
                    diff = c_lin_reg - curr_avg
                    diff_lst.append(diff)
                sd = np.std(diff_lst, 0)
                print(f"gradient: {gradient}, c: {c}, sd: {sd}")
                print(f"Next average price: {next_avg_price}")


            """
            Determine bid and ask prices that I will quote around (considering best bid/ask volume)
            """
            #Determine my bids and ask that I will send 
            my_bid, my_ask = self.find_my_bid_my_ask(best_bid, best_ask, market_buy_orders[0], market_sell_orders[0])
            
            
            """
            Determine the quantity that I am able to market make (position limit = 20, current position = 12 --> then qty_to_mm = position limit - current position = 20 - 12 = 8)
            """
            #Print current oustanding position
            if len(state.position) != 0:
                print(f"My position: {state.position}")
            else:
                print(f"No open positions")
                
            #Find quantity to market make
            if state.position.get(product, 0) == 0:
                qty_to_mm = abs(position_limit)
            else:
                if state.position.get(product) > 0: #We are long
                    qty_to_mm = abs(position_limit) - state.position.get(product)
                else: 
                    qty_to_mm = abs(position_limit) + state.position.get(product)

            curr_pos = state.position.get(product, 0)

            # update traderData if we have any trades from previous iteration
            if product in state.own_trades:
                # update our avg_val traderData
                traderData = self.handle_avg_pos_val(traderData, product, curr_pos, state.own_trades[product])
                # print(f"Own trade {product}: {state.own_trades[product]}")

            else:
                traderData = self.handle_avg_pos_val(traderData, product, curr_pos, None)
                # print(f"Own trade {product}: None")

            #Define multipliers
            sd_multiplier = 0.7
            market_close_multiplier =  0.1

                
            """
            ===================================================================================
                                                Trading Logic
            ===================================================================================
            (!!) IF (!!): outlier - midprice less than lower bound of our trend, expect price to increase
                Only quote bids.
            
            (!!) ELIF (!!): outlier - midprice more than upper bound of our trend, expect price to decrease
                Only quote asks.
            
            (!!) ELSE (!!): if the mid price is not an outlier, market make as normal.
                
                (!) IF (!): the current spread is large enough, market make best prices.
                (!) ELSE (!): the current spread is not large enough, market make with larger spread and hence worse prices.
                
                Close out open positions.
                (!) IF (!): we are long, send ask orders to close.
                (!) ELIF (!): we are short, send bid orders to close.
            """
            mm = True   # market make = true
            if len(traderData["avg"][product]) >= avg_hist:


                if mid_price < next_avg_price - sd_multiplier* sd and qty_to_mm != 0:
                    """
                    Outlier - Only send bid quotes.
                    """                 
                    market_quantity = min(abs(market_sell_orders[0][1]), qty_to_mm)

                    """
                    Close out of our current position if necessary when we are in a short position
                    """
                    if curr_pos < 0:    # if we are short
                        # find what our average value is and compare it with the market order
                        # we want to trade with the bots ONLY if we can guaranee a profit of 4 seashells per position
                        myavg_pos = traderData["avg_pos"][product]["avg_val"]   # this should not generate an error since we this will only run however many iterations our avg_hist is
                        if myavg_pos - market_sell_orders[0][0] > 3 * market_close_multiplier:    # 4 is our benchmark of a profit we want
                            orders.append(Order(product, market_sell_orders[0][0], -curr_pos))
                            print(f"Closing out position when short. Quoting {product}: bid:{market_sell_orders[0][0]}, qty:{-curr_pos}")

                    if market_sell_orders[0][0] < next_avg_price:
                        
                        orders.append(Order(product, market_sell_orders[0][0], market_quantity))
                        print(f"OUTLIER-BOUGHT: Market_price: {market_sell_orders[0][0]}, QTY: {market_quantity}")
                        # orders.append(Order(product, math.ceil(mid_price), qty_to_mm- market_quantity))
                        orders.append(Order(product, market_buy_orders[0][0] + 1, qty_to_mm- market_quantity))
                        print(f"(OUTLIER) Quoting {product}: bid {qty_to_mm - market_quantity}x {mid_price}")
                        mm = False

                    # """
                    # Close out of our current position if necessary when we are in a short position
                    # """
                    # if curr_pos < 0:
                    #     # find what our average value is and compare it with the market order
                    #     # we want to trade with the bots ONLY if we can guaranee a profit of 4 seashells per position
                    #     myavg_pos = traderData["avg_pos"][product]["avg_val"]   # this should not generate an error since we this will only run however many iterations our avg_hist is
                    #     if myavg_pos - market_sell_orders[0][0] > 3 * market_close_multiplier:    # 4 is our benchmark of a profit we want
                    #         orders.append(Order(product, market_sell_orders[0][0], -curr_pos))
                    #         print(f"Closing out position when short. Quoting {product}: bid:{market_sell_orders[0][0]}, qty:{-curr_pos}")

                elif mid_price > next_avg_price + sd_multiplier* sd and qty_to_mm != 0: 
                    """
                    Outlier - Only send ask quotes.
                    """
                    market_quantity = min(abs(market_buy_orders[0][1]), qty_to_mm)

                    
                    """
                    Close out of our current position if necessary when we are in a long position
                    """
                    if curr_pos > 0:
                        # find what our average value is and compare it with the market order
                        # we want to trade with the bots ONLY if we can guaranee a profit of 4 seashells per position
                        myavg_pos = traderData["avg_pos"][product]["avg_val"]   # this should not generate an error since we this will only run however many iterations our avg_hist is
                        if market_buy_orders[0][0] - myavg_pos > 3 * market_close_multiplier:    # 4 is our benchmark of a profit we want
                            orders.append(Order(product, market_buy_orders [0][0], -curr_pos))
                            print(f"Closing out position when long. Quoting{product}: ask:{market_buy_orders[0][0]}, qty:{-curr_pos}")


                    if market_buy_orders[0][0] > next_avg_price:        

                        orders.append(Order(product, market_buy_orders[0][0], -market_quantity))
                        print(f"OUTLIER-SOLD: Market_price: {market_buy_orders[0][0]}, QTY: {-market_quantity}")
                        # orders.append(Order(product, math.floor(mid_price), -qty_to_mm + market_quantity))
                        orders.append(Order(product, market_sell_orders[0][0] - 1, -qty_to_mm + market_quantity))
                        print(f"(OUTLIER) Quoting {product}: bid {-qty_to_mm + market_quantity}x {mid_price}")
                        mm = False

                    # """
                    # Close out of our current position if necessary when we are in a long position
                    # """
                    # if curr_pos > 0:
                    #     # find what our average value is and compare it with the market order
                    #     # we want to trade with the bots ONLY if we can guaranee a profit of 4 seashells per position
                    #     myavg_pos = traderData["avg_pos"][product]["avg_val"]   # this should not generate an error since we this will only run however many iterations our avg_hist is
                    #     if market_buy_orders[0][0] - myavg_pos > 3 * market_close_multiplier:    # 4 is our benchmark of a profit we want
                    #         orders.append(Order(product, market_buy_orders [0][0], -curr_pos))
                    #         print(f"Closing out position when long. Quoting{product}: ask:{market_buy_orders[0][0]}, qty:{-curr_pos}")

            if mm:
                """
                Market make as normal.
                """
                #If calculated prices' spread is large enough, market make (with best prices).
                if my_bid < mid_price and my_ask > mid_price and current_spread >= required_spread: 
                    orders.append(Order(product, my_bid, qty_to_mm))
                    orders.append(Order(product, my_ask, -qty_to_mm))
                
                    print(f"(MM) Quoting {product}: bid {qty_to_mm}x {my_bid}, ask {qty_to_mm}x {my_ask}")
                
                #If calculated prices' spread is not large enough, recalculate bids and asks to meet the required spread (but send worse prices - less likely to be filled)
                else:
                    new_my_bid, new_my_ask = self.find_required_bid_ask(market_buy_orders, market_sell_orders, my_bid, my_ask, required_spread)

                    if my_bid < mid_price and my_ask > mid_price:
                        #Modify our bids and ask (widen them) to meet the spread requirement. 
                        orders.append(Order(product, new_my_bid, qty_to_mm))
                        orders.append(Order(product, new_my_ask, -qty_to_mm))

                        print(f"(O.R.S) Quoting {product}: bid {qty_to_mm}x {new_my_bid}, ask {qty_to_mm}x {new_my_ask}")
                    else:
                        print(f"(O.R.S) Modified prices not valid (B,A): {new_my_bid} {new_my_ask}") #From checking logs, this only relevant for FIRST iteration. 
                
                """
                Close out of open positions
                """
                qty_to_close = state.position.get(product, 0) #Only continue if the asset has a current open position.
                
                #Send orders to try to close out of position
                if qty_to_close > 0: #Quote a ASK at best price                   
                    print("(CLOSE) Quoting SELL", str(qty_to_close) + "x", product, my_ask)
                    orders.append(Order(product, my_ask, -abs(qty_to_close)))
                    
                elif qty_to_close < 0: #Quote a BID at best price 
                    print("(CLOSE) Quote BUY", str(qty_to_close) + "x", product, my_bid)
                    orders.append(Order(product, my_bid, abs(qty_to_close)))

            
            result[product] = orders 
                    
    
        #print(f"TraderData AFTER: {traderData}")
        
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
                print(f"(ERROR) {product} not found in 'spread_dict'")
                return 0 # Return 0 if the list is empty
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
            print("(!!!) Both volume low (!!!) ")
            my_bid = best_bid 
            my_ask = best_ask 
        elif best_bid_vol in allowed_volume and abs(best_ask_vol) not in allowed_volume: #Only Bid low volume
            print("(!!!) Only bid volume low (!!!) ")
            my_bid = best_bid
            my_ask = best_ask - 1
        elif best_bid_vol not in allowed_volume and abs(best_ask_vol) in allowed_volume: #Only Ask bolume low 
            print("(!!!) Only ask volume low (!!!) ")
            my_bid = best_bid + 1
            my_ask = best_ask 
        else: #Both high volume 
            print("(!!!) Both volume high (!!!) ")
            my_bid = best_bid + 1
            my_ask = best_ask - 1
        
        return my_bid, my_ask
            
    def find_required_bid_ask(self, market_buy_orders, market_sell_orders, my_bid, my_ask, required_spread):
        """
        This function is called when the spread of the calculated my_bid and my_ask is too small (compared to the required spread) 
        """
        #This function should only be called when my bids/ask at lower spread than required spread, so spread_difference should always be < 0. 
        best_bid_vol = market_buy_orders[0][1]
        best_ask_vol = market_sell_orders[0][1]
        spread_difference = required_spread - (my_ask - my_bid)
        print(f"Required spread: {required_spread}, my quoted spread: {(my_ask - my_bid)}, difference of: {spread_difference}")
        print(f"Old prices are {my_bid} {my_ask}")
        
        if spread_difference % 2 == 0: #Even --> split evently between bid and ask
            my_bid = my_bid - spread_difference//2
            my_ask = my_ask + spread_difference//2
            print(f"Even spread - new prices are: {my_bid} {my_ask}")
        else: #Odd --> choose to quote better price for bid or ask.
            if best_bid_vol > best_ask_vol: #Less volume for ask, more likely to be filled if try to match.
                my_bid = my_bid - int(math.ceil(spread_difference/2))
                my_ask = my_ask + int(math.floor(spread_difference/2))
            else: #Less volume for bid, more likely to be filled if we try to match.
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
        "mid_price_dict": a dictionary with the last x mid prices, {product: [mid_price1, mid_price2, mid_price3, ...], ...}
        
        Change "spread_hist" to the simple moving average required.
        """
        spread_hist = 40
        
        if traderData == "": #No products. Initialise ALL required for traderData (not just spread, inc ema and everything)
            traderData = {"spread_dict": {product: [current_spread]}, "history_prices_dict": {}, "midprice_dict": {}, "avg": {}, "avg_pos": {}} 
        
        elif product in traderData["spread_dict"]: #Product already exists
            if len(traderData["spread_dict"][product]) < spread_hist:
                traderData["spread_dict"][product].append(current_spread)
            else: 
                traderData["spread_dict"][product].pop(0)
                traderData["spread_dict"][product].append(current_spread)
        else: #New product
            traderData["spread_dict"][product] = [current_spread]
        
        return traderData
            

    def append_last_x_bid_ask_prices(self, traderData, product, best_buy_order, best_ask_order):
        """
        For a particular product, update traderData to contain the last x values of the best bid and best ask.
        Used to calculate a fair value if a mid price is not given. 

        Change "data_hist" to the number of data periods you want to retain.
        """
        data_hist = 2
        
        if traderData == "": #No products. Initialise ALL required for traderData (not just spread, inc ema and everything)
            traderData = {"spread_dict": {}, "history_prices_dict": {product: [[best_buy_order[0], best_ask_order[0]]] }, "midprice_dict": {},
                          "avg": {}, "avg_pos": {}}
        
        elif product in traderData["history_prices_dict"]:
            if len(traderData["history_prices_dict"][product]) < data_hist:
                traderData["history_prices_dict"][product].append([best_buy_order[0], best_ask_order[0]])
            else: 
                traderData["history_prices_dict"][product].pop(0)
                traderData["history_prices_dict"][product].append([best_buy_order[0], best_ask_order[0]])
        else: #New product 
            traderData["history_prices_dict"][product] = [[best_buy_order[0], best_ask_order[0]]]
        
        return traderData
        
        
    def append_last_x_midprice(self, traderData, product, market_buy_orders, market_sell_orders):
        """
        For a particular product, update traderData to contain the weighted midprice of that product. 
        This data will then be used to calculate an ema in another function. 
        
        Change "midprice_hist" to the number of datapoints you want to capture.
        """
        midprice_hist = 20
        best_bid_price = market_buy_orders[0][0]
        best_ask_price = market_sell_orders[0][0]
        best_bid_vol = market_buy_orders[0][1]
        best_ask_vol = abs(market_sell_orders[0][1])
        weighted_midprice = (best_bid_price*best_bid_vol + best_ask_price*best_ask_vol) / (best_bid_vol+best_ask_vol)
        
        if traderData == "":
            traderData = {"spread_dict": {}, "history_prices_dict": {}, "midprice_dict": {product: [weighted_midprice]},
                           "avg": {}, "avg_pos": {}}
            
        elif product in traderData["midprice_dict"]:
            if len(traderData["midprice_dict"][product]) < midprice_hist:
                traderData["midprice_dict"][product].append(weighted_midprice)
            else:
                traderData["midprice_dict"][product].pop(0)
                traderData["midprice_dict"][product].append(weighted_midprice)
        else: #New product 
            traderData["midprice_dict"][product] = [weighted_midprice]
        
        return traderData
    
    
    def find_ema(self, traderData, product):
        """
        Determine the current EMA for this product.
        
        Change span to the number of datapoints to include in EMA.
        """
        span = 20
        weighted_midprice_list = traderData["midprice_dict"][product]
        
        series =  pd.Series(weighted_midprice_list)
        emwa = series.ewm(adjust = True, span = span).mean()
        
        return emwa.iloc[-1]


    def find_standard_deviation(self, traderData, product):
        """
        Find the standard deviation to determine upper and lower bounds for mid_price.
        """
        if len(traderData["midprice_dict"][product]) != 0 and len(traderData["midprice_dict"][product]) != 1: 
            std_dev = np.std(traderData["midprice_dict"][product]) 
        else: 
            std_dev = float("inf") #Can't calculate std_dev with no or 1 data value.
        
        return std_dev
        

    def avg(self, orders):
        """
        Find the weighted average of the orderbook
        """
        total = 0
        quantity1 = 0

        for price, quantity in orders.buy_orders.items():
            total += price * abs(quantity)
            quantity1 += abs(quantity)

        for price, quantity in orders.sell_orders.items():
            total += price * abs(quantity)
            quantity1 += abs(quantity)


        total = total / quantity1

        return total
    
    def append_last_x_avg(self, traderData, product, avg_price, avg_hist):
        """
        Find the average of last x values
        """
        if traderData == "":
            traderData = {"spread_dict": {}, "history_prices_dict": {}, "midprice_dict": {},
                           "avg": {product: [avg_price]}, "avg_pos": {}}
            
        elif product in traderData["avg"]:
            if len(traderData["avg"][product]) < avg_hist:
                traderData["avg"][product].append(avg_price)
            else:
                traderData["avg"][product].pop(0)
                traderData["avg"][product].append(avg_price)
        else: #New product 
            traderData["avg"][product] = [avg_price]
        
        return traderData
    

    def handle_avg_pos_val(self, traderData, product, curr_pos, last_trades):

        """
        inputs:
            curr_pos = out current positin at this timestamp we're in
            last_trades = the trade that we made last for this particular product
        return: Average position (avg_pos) is the average value of our position
        """


        if traderData == "":    # in theory this if statement should never execute
            traderData = {"spread_dict": {}, "history_prices_dict": {}, "midprice_dict": {},
                           "avg": {}, 
                           "avg_pos": {product: {"avg_val": 0, "pos": 0}}}
            print("NEVER")
            
        elif product not in traderData["avg_pos"] and last_trades is None:
            traderData["avg_pos"][product] = {"avg_val": 0, "pos": 0}

        elif product in traderData["avg_pos"]:
            prev_pos = traderData["avg_pos"][product]["pos"]

            # if our position remains as either a long or a short 
            if curr_pos != traderData["avg_pos"][product]["pos"] and ((curr_pos > 0 and prev_pos >= 0) or (curr_pos < 0 and prev_pos <= 0)):
            # if there is a change in our last submitted trade vs current trade
                # total_amount = []
                # total_price = []        
                if (curr_pos > 0 and curr_pos > prev_pos) or (curr_pos < 0 and curr_pos < prev_pos):
                    avg_price = []        
                    for trade in last_trades:
                        price = trade.price
                        amount = trade.quantity
                        # total_price.append(price)
                        # total_amount.append(amount)
                        avg_price.append(price*amount)

                    # calculate the new value 
                    traderData["avg_pos"][product]["avg_val"] = (prev_pos * traderData["avg_pos"][product]["avg_val"] + sum(avg_price)) / curr_pos
                    traderData["avg_pos"][product]["pos"] = curr_pos
                
                #traderData["avg_pos"][product]["pos"] = curr_pos

                # there should be no else statement because if i have 100 TSLA and get rid of 5 of them, my avg value is still the same, just the quant is diff
            # going from a negative to positive position or a positive to negative position
            elif curr_pos != traderData["avg_pos"][product]["pos"] and ((curr_pos < 0 and prev_pos > 0) or (curr_pos > 0 and prev_pos < 0)):
            # if there is a change in our last submitted trade vs current trade
                total_amount = []
                # total_price = []     
                avg_price = []             
                for trade in last_trades:
                    price = trade.price
                    amount = trade.quantity
                    # total_price.append(price)
                    total_amount.append(amount)
                    avg_price.append(price*amount)

                # calculate the new value 
                traderData["avg_pos"][product]["avg_val"] = sum(avg_price) / sum(total_amount)
                traderData["avg_pos"][product]["pos"] = curr_pos

            elif curr_pos == traderData["avg_pos"][product]["pos"]:
                print("NOTHING HAPPENS")

            elif curr_pos == 0:
                traderData["avg_pos"][product]["avg_val"] = 0


            else:       # this means im missing a scenario
                print("THIS SHOULD NEVER RUN")


        else: #New product 
            total_amount = []
            avg_val = []  
            if last_trades is None:
                avg_val = 0
            else:
                for trade in last_trades:
                    price = trade.price
                    amount = trade.quantity
                    avg_val.append(price*amount)
                    total_amount.append(amount)
                avg_val = sum(avg_val) / sum(total_amount)
            print("HERE")

            if sum(total_amount) != curr_pos:       # this means the matho dont add up
                print("SOMETHING VERY WRONG")

            traderData["avg_pos"][product]["avg_val"] = avg_val
            traderData["avg_pos"][product]["pos"] = curr_pos

        return traderData










        # # change the avg holding value
        # elif curr_pos != traderData["profit"][product]["last_pos"]:


        # elif product in traderData["profit"]:
        #     # compare curr avg price with old avg price 
        #     if curr_pos > 0:
        #         last_avg_val = traderData["avg"][-1]
        #         diff = avg_val - last_avg_val 
        #         if avg_val > last_avg_val:             
        #             traderData[product]["profit"] += diff * curr_pos
        #         else: 
        #             traderData[product]["profit"] -= diff * curr_pos


        #     if curr_pos < 0:
        #         last_avg_val = traderData["avg"][-1]
        #         diff = avg_val - last_avg_val 
        #         if avg_val < last_avg_val:             
        #             traderData[product]["profit"] += diff * curr_pos
        #         else: 
        #             traderData[product]["profit"] -= diff * curr_pos

    # def handle_last_pos(self, )























    # long @ 10 at 1000  = required spread is 5
    # market is at 1005 - 1008
    # 1006 - 1007

    

    # multiplier for required spread that we are happy to secure a product of 4