import pandas as pd
from yfinance import Ticker


class Holding(Ticker):

    def __init__(self, holding):
        self.holding = holding.upper()
        super().__init__(self.holding)

    @property
    def return_long_name(self):
        return super().info['longName']

# #
# tick_h = Holding('amd')
# print(tick_h.return_long_name)
