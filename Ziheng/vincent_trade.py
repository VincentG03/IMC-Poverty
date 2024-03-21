

from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List






class Trader:
    # Hardcode different sprteads for different products 
    # Figure out the trend of the market, trade in larger quantities when its favourable ( we were long, then market dropped, then we had to close out at a loss)
    # Instead of rejecting if the trade is bad, can increase my spread then send order again (unlikely to be executed but if they do we get big profit)
    
    def run(self, state: TradingState):
        """
        1. Check outstanding positions 
            1.1 No outstanding positions --> Market make 
            1.2 Outstanding positions --> Send order to close position
        """
        #print("traderData: " + state.traderData)
        #print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
        state.toJSON()
        result = {}
        # traderData = json.loads(state.traderData or "null") #I think this is correct 
        traderData = state.traderData
        print(f"traderData0: {traderData}")
        if traderData == "":
            print(f"NORMAL")
            traderData = None

        for product in state.order_depths:

            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            print(f"|| Buy Orders {product}: " + str(order_depth.buy_orders) + f", Sell Orders {product}: " + str(order_depth.sell_orders) + "||")

            #Determine the position limit (set by IMC)
            position_limit = self.find_position_limits(product)

            #(!!!!!!!!) Determine the spread we will trade for this product 
            required_spread = self.find_required_spread(product, traderData) 

            #Print current position
            if len(state.position) != 0:
                print(f"My position: {state.position}")
            else:
                print(f"No open positions")
            

            #Determine mid price to quote around
            mid_price = ((list(order_depth.buy_orders.items())[0][0]) + (list(order_depth.sell_orders.items())[0][0]))/2
            
            #Determine the market's best bid and best ask
            best_bid = list(order_depth.buy_orders.items())[0][0]
            best_ask = list(order_depth.sell_orders.items())[0][0]
            print(f"bid {best_bid}, ask {best_ask}")

            #Determine the spread 
            spread = best_ask - best_bid 
            print(f"traderData1: {traderData}")
            traderData = self.last_x_spread(traderData, product, spread, spread_hist = 20)
            print(f"traderData2: {traderData}")

            #Determine my bids and ask that I will send 
            my_bid, my_ask = self.find_my_bid_ask(best_bid, best_ask)

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
                    #print("(MM) Quoting BUY", str(qty_remaining) + "x", product, my_bid)
                    orders.append(Order(product, my_bid, qty_remaining))

                    #print("(MM) Quoting SELL", str(qty_remaining) + "x", product, my_ask)
                    orders.append(Order(product, my_ask, -qty_remaining))
                
                    print(f"(MM) Quoting {product}: bid {qty_remaining}x {my_bid}, ask {qty_remaining}x {my_ask}")
                else: 
                    #If the below executes, it means that we are potentially 
                    print(f"Could place {my_bid} and {my_ask}")
                
                
                
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


        # traderData = "" 
        
        # Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, str(traderData)
    


    def find_position_limits(self, product) -> int:
        """
        For each product, find the position limited set (hard coded).
        """
        #Set position limits 
        product_limits = {'AMETHYSTS': 20, 'STARFRUIT': 20}
        
        if product in product_limits:
            return product_limits[product]
        else: 
            return 20 #Set default position limit to 20
        
        
    def find_required_spread(self, product, traderData):
        """
        For a particular product, find the spread we require before we market make.
        """
        product_required_spread = {'AMETHYSTS': 6, 'STARFRUIT': 6}
        
        if product in product_required_spread:
            return product_required_spread[product]
        else: 
            return 6 #Default spread set to 6 (NOT RELIABLE)
        
        
    def find_my_bid_ask(self, best_bid, best_ask):
        """
        Return the bid and ask prices we will quote.
        """
        return best_bid + 1, best_ask - 1
        

    def last_x_spread(self, traderData, symbol, curr_spread, spread_hist):
        if traderData is None:
            print("HI")
            return {symbol: [curr_spread]}
        if symbol in traderData:
            if len(traderData[symbol]) < spread_hist:
                traderData[symbol].append(curr_spread)
                print(f"traderData4: {traderData}")
            else:
                traderData[symbol].pop(0)
                traderData[symbol].append(curr_spread)
                print(f"traderData5: {traderData}")
        else:
            traderData[symbol] = [curr_spread]
            print(f"traderData6: {traderData}")
            return traderData
        print(f"traderData7: {traderData}")
        return traderData

    # example of what the dict will look like
    # {AMETHYST: [4, 5, 3, 4, 5, 5, 4], STARFRUIT: [1, 3, 4, 3, 2, 3]}