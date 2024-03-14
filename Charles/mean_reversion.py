from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    def __init__(self):
        self.historical_mid_prices = {}
        self.historical_average = {}
        self.deviation_threshold = 0.05  # Example: 5% deviation threshold
        self.max_position = 10
        self.current_position = {}
        self.window_size = 10  # Define window size for historical data

    def run(self, state: TradingState):
        current_mid_price = state.observations.plainValueObservations['mid_price']
        result = {}  # Initialize result dictionary to store orders
        
        MAX_ORDER_QUANTITY = 10  # Adjust max order quantity according to your requirements

        # Calculate historical average and deviation
        for product in state.order_depths:
            if product not in self.historical_mid_prices:
                self.historical_mid_prices[product] = []
                self.historical_average[product] = None
            self.update_historical_average(product, current_mid_price)
            deviation = self.calculate_deviation(product, current_mid_price)

            # Place orders based on deviation and position limit
            orders = self.generate_orders(product, current_mid_price, deviation, MAX_ORDER_QUANTITY)
            result[product] = orders

        return result, 1, "Sample Trader Data"

    def update_historical_average(self, product, current_mid_price):
        self.historical_mid_prices[product].append(current_mid_price)
        if len(self.historical_mid_prices[product]) > self.window_size:
            self.historical_mid_prices[product] = self.historical_mid_prices[product][1:]  # Keep only recent data
        self.historical_average[product] = sum(self.historical_mid_prices[product]) / len(self.historical_mid_prices[product])

    def calculate_deviation(self, product, current_mid_price):
        historical_avg = self.historical_average[product]
        if historical_avg:
            return (current_mid_price - historical_avg) / historical_avg
        else:
            return 0

    def generate_orders(self, product, current_mid_price, deviation, max_order_quantity):
        orders = []
        position = self.current_position.get(product, 0)
        max_buy_quantity = max(0, self.max_position - position)
        max_sell_quantity = max(0, self.max_position + position)

        if abs(deviation) > self.deviation_threshold:
            if deviation > 0:
                # Place sell orders
                sell_quantity = min(max_sell_quantity, max_order_quantity)
                orders.append(Order(product, current_mid_price, -sell_quantity))
            else:
                # Place buy orders
                buy_quantity = min(max_buy_quantity, max_order_quantity)
                orders.append(Order(product, current_mid_price, buy_quantity))

        return orders
