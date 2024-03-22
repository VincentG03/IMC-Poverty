import json
from datamodel import Order, ProsperityEncoder, Symbol, TradingState, Trade, OrderDepth
from typing import Any, List
import statistics

class Logger:
    # Set this to true, if u want to create
    # local logs
    local: bool 
    # this is used as a buffer for logs
    # instead of stdout
    local_logs: dict[int, str] = {}

    def __init__(self, local=False) -> None:
        self.logs = ""
        self.local = local

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
        output = json.dumps({
            "state": state,
            "orders": orders,
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True)
        if self.local:
            self.local_logs[state.timestamp] = output
        print(output)

        self.logs = ""

    def compress_state(self, state: TradingState) -> dict[str, Any]:
        listings = []
        for listing in state.listings.values():
            listings.append([listing["symbol"], listing["product"], listing["denomination"]])

        order_depths = {}
        for symbol, order_depth in state.order_depths.items():
            order_depths[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return {
            "t": state.timestamp,
            "l": listings,
            "od": order_depths,
            "ot": self.compress_trades(state.own_trades),
            "mt": self.compress_trades(state.market_trades),
            "p": state.position,
            "o": state.observations,
        }

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.buyer,
                    trade.seller,
                    trade.price,
                    trade.quantity,
                    trade.timestamp,
                ])

        return compressed

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

# This is provisionary, if no other algorithm works.
# Better to loose nothing, then dreaming of a gain.

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
        traderData = state.traderData 
        
        if traderData != "":
            traderData = eval(traderData)

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
            print(f"Market bid {best_bid}, Market ask {best_ask}")

            #Calculate the spread + add to traderData (to calculate avg spread)
            current_spread = best_ask - best_bid 
            traderData = self.append_last_x_spread(traderData, product, current_spread)
            print(f"Current traderData: {traderData}")
            
            #(!!!!!!!!) Determine the spread we will trade for this product            
            required_spread = self.find_required_spread(product, traderData) 
                
            #Calculate mid price to quote around (THIS MAY BE NOT USED IN THE FUTURE)
            mid_price = ((list(order_depth.buy_orders.items())[0][0]) + (list(order_depth.sell_orders.items())[0][0]))/2
            
            #Determine my bids and ask that I will send 
            my_bid, my_ask = self.find_my_bid_ask(best_bid, best_ask)
            
            #Print current position
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
        return result, traderData
    


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
    
    
    def append_last_x_spread(self, traderData, product, current_spread):
        """
        For a particular product, update traderData to contain the last 20 values of it's spread.
        Used to calculate the spread at which we will trade at.
        
        "spread_dict": 
        """
        product = f'"{product}"'
        spread_hist = 20
        
        if traderData == "": #No products. Initialise ALL required for traderData (not just spread, inc ema and everything)
            traderData = {"spread_dict": {product: [current_spread]}, "ema_dict": [], "other_dict": []} 
        
        elif product in traderData["spread_dict"]: #Product already exists
            if len(traderData["spread_dict"][product]) < spread_hist:
                traderData["spread_dict"][product].append(current_spread)
            else: 
                traderData["spread_dict"][product].pop()
                traderData["spread_dict"][product].append(current_spread)
        else: #New product
            traderData["spread_dict"][product] = [current_spread]
        
        return traderData