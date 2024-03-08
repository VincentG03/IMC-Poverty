from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    
    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # print("traderData: " + state.traderData)
        # print("Observations: " + str(state.observations))
        print(f' state position {state.position}')
        valid_positions = {'AMETHYSTS': 20, 'STARFRUIT': 20}
				# Orders to be placed on exchange matching engine
        result = {}
        for product in state.order_depths:

            print(f'product {product}')
            order_depth: OrderDepth = state.order_depths[product]
            # Initialize the list of Orders to be sent as an empty list
            orders: List[Order] = []
            # Define a fair value for the PRODUCT. Might be different for each tradable item
            # Note that this value of 10 is just a dummy value, you should likely change it!
            acceptable_price = 10
						# All print statements output will be delivered inside test results
            # print("Acceptable price : " + str(acceptable_price))
            # print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
    
						# Order depth list come already sorted. 
						# We can simply pick first item to check first item to get best bid or offer
            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                # if int(best_ask) < acceptable_price:

                    # print("BUY", str(-best_ask_amount) + "x", best_ask)
                    # orders.append(Order(product, best_ask, -best_ask_amount))
    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                # if int(best_bid) > acceptable_price:
				# 						# Similar situation with sell orders
                #     print("SELL", str(best_bid_amount) + "x", best_bid)
                #     orders.append(Order(product, best_bid, -best_bid_amount))
            
            average_val = round(self.avg({ **order_depth.buy_orders, **order_depth.sell_orders}))
            mid_price = (best_ask + best_bid) / 2

            position = state.position.get(product, 0)
            # if its gonna go up
            if average_val > mid_price:
                # buy low sell high
                for ask, ask_amount in order_depth.sell_orders.items():
                    if average_val < ask:
                        break
                    else:
                        ask_amount = position - ask_amount if abs(position - ask_amount) <= 20 else None
                        orders.append(Order(product, ask, ask_amount))

            # if its gonna go down
            if average_val < mid_price:
                # buy low sell high
                for bid, bid_amount in order_depth.buy_orders.items():
                    if average_val > bid:
                        break
                    else:
                        bid_amount = position - bid_amount if abs(position - bid_amount) <= 20 else None
                        orders.append(Order(product, bid, bid_amount))

            result[product] = orders
    
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        traderData = "" 
        
				# Sample conversion request. Check more details below. 
        conversions = 1

        # print(f'results: {result}, conversions: {conversions}, traderData: {traderData}')
        return result, conversions, traderData

    def avg(self, orders):
        total = 0
        for price, quantity in orders.items():
            total += price * abs(quantity)
        total = total / sum([abs(quantity) for _, quantity in orders.items()])

        return total



# the next price is always gonna go in the trend of the avg price
    
    # calculate the avg
    # compare the avg to the mid price
    # if the avg is bigger than the mid price, buy
    # if the avg is smaller than the mid price, sell
    # if its the same dont do anything


# shit