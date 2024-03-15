from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import statistics

class Trader:
    
    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        traderData = state.traderData
        traderData_list = []
        if state.traderData != "":
            traderData_list = state.traderData.split(" ")
        
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            acceptable_price = 10
            
            RSI = 50
            gains_up = []
            loss_down = []
            if state.traderData != "" and len(traderData_list) > 14:
                curr_point = traderData_list[0]
                for price in traderData_list:
                    if price > curr_point:
                        gains_up.append(price)
                    elif price < curr_point:
                        loss_down.append(price)
                    elif price == curr_point:
                        gains_up.append(price)
                        loss_down.append(price)
                    curr_point = price
                average_gains_up_period = statistics.mean(gains_up)
                average_loss_down_period = statistics.mean(loss_down)
                RSI = 100 - (100 / (1 + (average_gains_up_period / average_loss_down_period)))
            print(f"RSI: {RSI}")

            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if RSI < 45:
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))
    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if RSI > 55:
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))
            
            result[product] = orders

            mid_price = (best_bid - best_ask) / 2
            
            if len(traderData) < 15:
                traderData = traderData + f"{mid_price} "
            else:
                traderData = " ".join(traderData_list)

        conversions = 1
        return result, conversions, traderData
