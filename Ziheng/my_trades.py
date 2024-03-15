from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np
import statistics

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

    
            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]

            traderData_dict = state.traderData.split(",")
            traderData = state.traderData
            
            average_val_this_round = round(self.avg({ **order_depth.buy_orders, **order_depth.sell_orders}))
            traderData_dict.append(average_val_this_round)
            if len(traderData_dict) > 9:
                traderData_dict.pop(0)
                past_10_avg = [avg_price for avg_price in traderData_dict]

                x_val = [i for i in range(9)]
                print(f"past 10_avg: {past_10_avg}")
                print(f"x_val: {x_val}")
                
                constant, gradient = self.lin_reg(x_val, past_10_avg)
                
                # gotta have a gradient buffer
                # if the gradient is between 0.5 and -0.5 => we will assume horizontal line so we don't do anything meaning price is still the same
                if gradient < 0.5 or gradient > -0.5:
                    break
                
                # average_val = round(self.avg({ **order_depth.buy_orders, **order_depth.sell_orders}))
                mid_price = (best_ask + best_bid) / 2

                position = state.position.get(product, 0)
                
                average_val = statistics.mean(past_10_avg)
                # if its gonna go up
                if gradient > 0 and average_val > mid_price:
                    # buy low sell high
                    for ask, ask_amount in order_depth.sell_orders.items():
                        if average_val < ask:
                            break
                        else:
                            ask_amount = position - ask_amount if abs(position - ask_amount) <= 20 else 0
                            orders.append(Order(product, ask, ask_amount))

                # if its gonna go down
                if gradient < 0 and average_val < mid_price:
                    # buy low sell high
                    for bid, bid_amount in order_depth.buy_orders.items():
                        if average_val > bid:
                            break
                        else:
                            bid_amount = position - bid_amount if abs(position - bid_amount) <= 20 else 0
                            orders.append(Order(product, bid, bid_amount))

                result[product] = orders
    
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        if len(traderData_dict) > 9:
            traderData = "".join(past_10_avg)
        else:
            if len(traderData_dict) < 10:
                traderData = traderData + f", {average_val_this_round}"
            else:
                traderData = traderData + f"{average_val_this_round}"
        
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


    def lin_reg(self, x, y):
        # number of observations/points
        n = np.size(x)
        
        # mean of x and y vector
        m_x = np.mean(x)
        m_y = np.mean(y)
        
        # calculating cross-deviation and deviation about x
        SS_xy = np.sum(y*x) - n*m_y*m_x
        SS_xx = np.sum(x*x) - n*m_x*m_x
        
        # calculating regression coefficients
        b_1 = SS_xy / SS_xx
        b_0 = m_y - b_1*m_x
        
        return (float(b_0), float(b_1))
    
    # the next price is always gonna go in the trend of the avg price
    
    # calculate the avg
    # compare the avg to the mid price
    # if the avg is bigger than the mid price, buy
    # if the avg is smaller than the mid price, sell
    # if its the same dont do anything


# shit