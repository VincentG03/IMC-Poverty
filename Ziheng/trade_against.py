


from datamodel import *


class OrderDepth1:
    def __init__(self) -> None:
        
        super().__init__(self)
        self.buy_orders: Dict[int, int] = {}
        self.sell_orders: Dict[int, int] = {}



def trade_against_each_other(traders: List[Trader]):
    """
    Put your Trader class last if you want to test it
    """

    iterations = 2000
    
    
    traderData = ""
    time = 0
    order_depth = OrderDepth()
    listings = Listing("APPL", "APPL", "idk what this is")
    own_trades = {}
    market_trades = {}
    position = {}
    # no observations for now
    observations = Observation({}, {})
    
    trading_state = TradingState(traderData, time, listings, order_depth, own_trades, 
                                 market_trades, position, observations)
    
    profits = {}
    while time < iterations:
        # this is fucked because it's running sequentially - idk how else you would do it
        
        # order book will not be cleared every timestep due to fairness
        for trade in traders:
            result, conversions, traderData = trade.run(trading_state)
            
            # putting results in order book
            for product, order in result.items():
                if order.quantity > 0:
                    trading_state.order_depths[product].buy_orders[order.price] = order.quantity 
                if order.quantity > 0:
                    trading_state.order_depths[product].sell_orders[order.price] = order.quantity 
                    
            
            
            
if __name__ == "__main__":
    
    # my trade algorithm
    from my_trades import Trader as myTrader
    my_trade = myTrader()
    