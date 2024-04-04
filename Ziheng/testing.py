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
            pos = state.position.get(product, 0)

            if pos != 20:
                


				# Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData