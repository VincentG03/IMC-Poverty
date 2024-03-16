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

    logger = Logger(local=True)

    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        
        traderData = state.traderData
				# Orders to be placed on exchange matching engine
        traderData_list = []
        if state.traderData != "":
          traderData_list = state.traderData.split(" ")
        result = {}
        for product in state.order_depths:

            order_depth: OrderDepth = state.order_depths[product]
            # Initialize the list of Orders to be sent as an empty list
            orders: List[Order] = []
            # Define a fair value for the PRODUCT. Might be different for each tradable item
            # Note that this value of 10 is just a dummy value, you should likely change it!
            acceptable_price = 10
						# All print statements output will be delivered inside test results
            print("Acceptable price : " + str(acceptable_price))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

            RSI = 50
            gains_up = []
            loss_down = []
            if state.traderData != "" and len(traderData_list) > 14:
              curr_point = traderData_list[0]
              for price in traderData_list:
                if price > curr_point:
                  gains_up.append(price)
                if price < curr_point:
                  loss_down.append(price)
                if price == curr_point:
                  gains_up.append(price)
                  loss_down.append(price)
                  
                curr_point = price
              average_gains_up_period = statistics.mean(gains_up)
              average_loss_down_period = statistics.mean(loss_down)
              
            
              RSI = 100 - (100 / (1 + (average_gains_up_period/average_loss_down_period)))
            print(f"RSI: {RSI}")
            print(f"Order Depth: {order_depth}")
            
						# Order depth list come already sorted. 
						# We can simply pick first item to check first item to get best bid or offer
            # if len(order_depth.sell_orders) != 0:
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                # if int(best_ask) < acceptable_price:
                if RSI < 45:
                    # In case the lowest ask is lower than our fair value,
                    # This presents an opportunity for us to buy cheaply
                    # The code below therefore sends a BUY order at the price level of the ask,
                    # with the same quantity
                    # We expect this order to trade with the sell order
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))
            # if len(order_depth.buy_orders) != 0:
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if RSI > 55:
                                        # Similar situation with sell orders
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
                mid_price = (best_bid - best_ask) / 2
            result[product] = orders
    
                
            # if state.traderData != "" and len(traderData_list) > 0 and len(traderData_list) < 15:
              
            
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        if len(traderData) < 15:
          traderData = traderData + f"{mid_price} "
        else:
          traderData = " ".join(traderData_list)

        
				# Sample conversion request. Check more details below. 
        conversions = 1
        # return result, conversions, traderData
        # Initialize the method output dict as an empty dict
        # result = {}
        self.logger.flush(state, result)
        return result, traderData
