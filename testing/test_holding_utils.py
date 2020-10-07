import unittest
import pandas as pd
import src.holding_util as hu


class TestHoldings(unittest.TestCase):

    def test_utils(self):
        data1 = [["VTI", "ETF", 0.25],
                 ["USRT", "ETF", 0.50],
                 ["VNQI", "ETF", 0.25]]
        data2 = [["AAPL", "Stock", 0.30],
                 ["MSFT", "Stock", 0.30],
                 ["VOO", "ETF", 0.40]]
        cols = ["Stock", "Type", "Total_perc"]
        acc1 = pd.DataFrame(data1, columns=cols).set_index("Stock", drop=True)
        acc2 = pd.DataFrame(data2, columns=cols).set_index("Stock", drop=True)
        accounts = [acc1, acc2]
        value_worth = [5000, 2500]
        acc_worth = hu.calculate_value_weight(value_worth)

        final_df = pd.DataFrame()
        for acc, worth in zip(accounts, acc_worth):
            account_df = acc
            etf_df = account_df[account_df["Type"] == "ETF"]
            etf_list = etf_df.index.to_list()

            asset_list = []
            for etf in etf_list:
                h = hu.Holding(etf)
                h_df = h.scrape_holdings()
                h_df["Weight"] = etf_df[etf_df.index == etf]["Total_perc"][0]
                asset_list.append(h_df)
            asset_df = hu.etf_asset_allocation(asset_list)
            stock_df = hu.stock_allocation(account_df)
            if not stock_df.empty:
                asset_df = asset_df.append(stock_df)
            asset_df = asset_df * worth
            final_df = pd.concat([final_df, asset_df])
        final_df = final_df.groupby(final_df.index).sum()
        print(final_df)
