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
    
    def run(self, state: TradingState):
        """
        1. Check outstanding positions 
            1.1 No outstanding positions --> Market make 
            1.2 Outstanding positions --> Send order to close position
        """
        #print("traderData: " + state.traderData)
        #print("Observations: " + str(state.observations))

        #Set position limits 
        product_limits = {'AMETHYSTS': 15, 'STARFRUIT': 15}

        # Orders to be placed on exchange matching engine
        result = {}

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            print(f"|| Buy Orders {product}: " + str(order_depth.buy_orders) + f", Sell Orders {product}: " + str(order_depth.sell_orders) + "||")

            #Find the position limit
            position_limit = self.find_position_limits(product, product_limits)

            #Print current position
            if len(state.position) != 0:
                print(f"My position {product}: {state.position}")
            else:
                print(f"No open positions {product}")

            #(!!!) There are no open positions --> Send orders to attempt to MM
            if state.position.get(product, 0) == 0:
                #Get the maximum amount of orders to send. There should be no outstanding positions so max is position limit set. 
                qty_to_mm = abs(position_limit)
               
                #Get mid price to ensure that our quoted bid and ask price are correct (bid < mid price, ask > mid price)
                mid_price = ((list(order_depth.buy_orders.items())[0][0]) + (list(order_depth.sell_orders.items())[0][0]))/2

                #Quote a better bid price (BUY order) and a better ask price (SELL order)
                my_bid = list(order_depth.buy_orders.items())[0][0] + 1
                my_ask = list(order_depth.sell_orders.items())[0][0] - 1 

                #Check if the order is valid - if not do nothing. 
                if my_bid < mid_price and my_ask > mid_price and my_bid < my_ask: 
                    print("(MM) Quoting BUY", str(qty_to_mm) + "x", product, my_bid)
                    orders.append(Order(product, my_bid, qty_to_mm))

                    print("(MM) Quoting SELL", str(qty_to_mm) + "x", product, my_ask)
                    orders.append(Order(product, my_ask, -qty_to_mm))

                    result[product] = orders


            #(!!!) There are open positions --> Quote orders to close positions
            else:
                qty_to_close = state.position.get(product) #Only continue if the asset has a current open position. 
                #Now add logic to determine if we should quote at best bid and ask or better
                best_bid = list(order_depth.buy_orders.items())[0][0]
                best_ask = list(order_depth.sell_orders.items())[0][0]
                
                
                #Change this to determine if we should match the best bid/ask, or beat them (rn we are not doing anything)
                my_bid = best_bid
                my_ask = best_ask
                
                if qty_to_close is not None: 
                    if state.position[product] > 0: #Quote a ASK at best price                   
                        print("(CLOSE) Quoting Ask", str(qty_to_close) + "x", product, my_ask)
                        orders.append(Order(product, my_ask, -abs(qty_to_close)))
                        
                    else: #Quote a BID at best price 
                        print("(CLOSE) Quote Bid", str(qty_to_close) + "x", product, my_bid)
                        orders.append(Order(product, my_bid, abs(qty_to_close)))

                    result[product] = orders 


        traderData = "No data needed" 
        
        # Sample conversion request. Check more details below. 
        conversions = 1
        return result, traderData
    
    
    def find_position_limits(self, product, product_limits: dict) -> int:
        """
        For each product, find the position limited set (hard coded).
        """
        if product in product_limits:
            return product_limits[product]
        else: 
            return 20 #Set default position limit to 20
    