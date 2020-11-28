import os
import numpy as np
import pandas as pd
import yfinance.utils as utils

from yfinance import Ticker, Tickers
from datetime import datetime
from resources.ticker_mapping import tick_map

yahoo_url = "https://finance.yahoo.com/quote"
etfdb_url = "https://etfdb.com/etf/{}/#holdings"


class Holding(Ticker):

    def __init__(self, share):
        self.share = share.upper()
        super().__init__(self.share)

    @property
    def short_name(self):
        """Returns the short name of the share"""
        try:
            return super().info['shortName']
        except Exception as e:
            print(type(e), e)
            return None

    @property
    def mkt_price(self):
        """Gets Market Price of share"""
        try:
            return super().info['regularMarketPrice']
        except Exception as e:
            print(type(e), e)
            return np.nan

    def scrape_holdings(self, source="ETFDB"):
        """Only valid for ETFs or Index funds with a list of holdings.
        Returns a DataFrame including the top holdings of the ETF and their corresponding %assets

        :param source: string, specifies from which website to scrape
        """
        source = source.lower()
        if source == "etfdb":
            scrape_url = etfdb_url.format(self.share)
            holdings_list = pd.read_html(scrape_url)
            holdings_df = holdings_list[2].rename(columns={'Holding': 'Name'})
            holdings_df.drop(holdings_list[2].tail(1).index, inplace=True)
        elif source == "yahoo finance":
            scrape_url = "{}/{}/holdings".format(yahoo_url, self.share)
            holdings_list = pd.read_html(scrape_url)
            holdings_df = holdings_list[0].dropna(axis=0)
        holdings_df.loc[:, "% Assets"] = holdings_df["% Assets"].str.replace('%', '').astype(float)
        return holdings_df.set_index('Symbol').rename(columns={"% Assets": "Perc Assets"})


class Holdings(Tickers):

    def __init__(self, holdings):
        self.holdings = holdings.upper()
        super().__init__(self.holdings)

    def return_sector_list(self):
        """Returns a list of the Sectors for all holdings passed"""
        sector_list = []
        for tick in self.tickers:
            try:
                sector_list.append(tick.info['sector'])
            except:
                sector_list.append(None)
        return sector_list

    def return_country_list(self):
        """Returns a list of the Sectors for all holdings passed"""
        sector_list = []
        for tick in self.tickers:
            try:
                sector_list.append(tick.info['country'])
            except:
                sector_list.append(None)
        return sector_list


class ScrapeHolding(object):

    def __init__(self, holding=None, holdings_list=None):
        self.holding = str(holding).upper()
        self.holdings_list = holdings_list

    def scrape_json_value(self, key, detail_key=None):
        """Returns the value of key value pair from Yahoo Finance scraping json. Default to summaryProfile"""
        try:
            scrape_url = 'https://finance.yahoo.com/quote'
            url = '%s/%s' % (scrape_url, self.holding)
            data = utils.get_json(url)
            return data[key][detail_key]
        except Exception:
            pass
            # print(
            #     "Could not retreive {} from {}. Ticker must be a STOCK, cannot be ETF".format(detail_key.capitalize(),
            #                                                                                   self.holding))

    def scrape_json_values(self, key="summaryProfile", detail_key=None):
        """Returns a list of Values for all tickers in tickers_list"""
        return_list = []
        for ticker in self.holdings_list:
            self.holding = ticker
            try:
                value = self.scrape_json_value(key=key, detail_key=detail_key)
                return_list.append(value)
            except:
                return_list.append(None)
        return return_list


def etf_asset_allocation(*args):
    """Adds the percent of all %assets of the same ticker
    :param args: list of dfs, df must contain list of shares with corresponding %asset"""
    tot_df = pd.DataFrame()
    for df in args:
        tot_df = tot_df.append(df)
    tot_df["Allocation"] = tot_df["Perc Assets"] * tot_df["Weight"]
    tot_df = tot_df.groupby(tot_df.index).sum()
    return tot_df["Allocation"]


def stock_allocation(df):
    """Calculates total allocation of stocks
    :param df: dataframe, df of ETFs+Stock. If df does not contain stocks, returns empty df"""
    try:
        stock_df = df[df["Type"] == "Stock"]
        stock_df = stock_df.rename(columns={"Allocation Ratio": "Allocation"})
        return stock_df["Allocation"] * 100
    except Exception:
        return pd.DataFrame()


def calculate_value_weight(value_list):
    """Returns a weighted value corresponding to the money allocation of all accounts
    "param value_list: list, values must be integers corresponding to accounts"""
    try:
        total_worth = sum(value_list)
        return_list = []
        for val in value_list:
            v = val / total_worth
            return_list.append(v)
        return return_list
    except Exception as e:
        print("Oops! We encountered the following error: {}\nType: {}".format(e, type(e)))


# class AccountShares(ScrapeHolding):
#
#     def __init__(self, account_file):
#         self.account_file = account_file
#
#     def

# tick_list = ['BABA', 'NESN', '700', '2330', '005930', 'ROG', 'NOVN', '7203', 'HSBA',
#              'AZN', '1299', 'SAP', 'ASML', 'CSL', 'SAN']
# sh = ScrapeHolding(holdings_list=tick_list)
# country = sh.scrape_json_values(detail_key="country")
# h = Holding('vxus')
# holdings = h.scrape_holdings()
# print(holdings)


def calculate_account_value(file):
    """Calculates the total value of an account. Creates a get request to yahoo finance for every ticker in file,
    requesting latest market value. In addition, creates a copy of file based off Allocation Ratio
    :param file: str. Account file name
    :return account_total_value: int. Total value of account
    """
    dirpath = r"C:\Users\Marco\github_repos\shares_analysis\resources"
    path = os.path.join(dirpath, file)
    account_df = pd.read_csv(path).set_index("Stock")
    sh = ScrapeHolding(holdings_list=account_df.index)
    price_list = sh.scrape_json_values(key="price", detail_key="regularMarketPrice")
    account_df["Value"] = account_df.Shares * price_list
    account_total_value = sum(account_df["Value"])
    account_df["Allocation Ratio"] = account_df["Value"] / account_total_value
    account_df.to_csv(r"{}\robinhood.csv".format(dirpath))
    return account_total_value


robinhood_file = "rh_account.csv"

###Passing a list of ETFs
accounts = ["m1.csv", "ira.csv", "hsa.csv", "robinhood.csv"]
value_worth = [8138, 6573, 2140, calculate_account_value(robinhood_file)]
# accounts = ["401k.csv"]
# value_worth = [900]
acc_worth = calculate_value_weight(value_worth)
print("Total worth $", round(sum(value_worth), 2))z
dirpath = r"C:\Users\Marco\github_repos\shares_analysis\resources"

final_df = pd.DataFrame()
for acc, worth in zip(accounts, acc_worth):
    path = os.path.join(dirpath, acc)
    account_df = pd.read_csv(path).set_index("Stock")
    etf_df = account_df[(account_df["Type"] == "ETF") | (account_df["Type"] == "Fund")]
    etf_list = etf_df.index.to_list()
    asset_list = []
    for etf in etf_list:
        h = Holding(etf)
        if acc == "hsa.csv":
            source = "yahoo finance"
        else:
            source = "yahoo finance"
        h_df = h.scrape_holdings(source=source)
        if etf == "VSMGX":
            etf_list2 = h_df.index.to_list()
            asset_list2 = []
            for etf2 in etf_list2:
                h2 = Holding(etf2)
                h_df2 = h2.scrape_holdings(source=source)  # Returns "Name" and "Perc Assets" for ETF
                h_df2["Weight"] = h_df.loc[h_df.index == etf2, ["Perc Assets"]].iloc[0, 0]
                h_df2["Perc Assets"] = h_df2["Perc Assets"] * h_df2["Weight"] / 100
                h_df = h_df.drop(h_df[h_df.index == etf2].index)
                if not h_df2.empty:
                    h_df = h_df.append(h_df2, sort=False)
            h_df["Weight"] = etf_df.loc[etf_df.index == etf, ["Allocation Ratio"]].iloc[0, 0]
            asset_list.append(h_df)
            continue
        h_df["Weight"] = etf_df.loc[etf_df.index == etf, ["Allocation Ratio"]].iloc[0, 0]
        asset_list.append(h_df)
    asset_df = etf_asset_allocation(asset_list)
    stock_df = stock_allocation(account_df)
    if not stock_df.empty:
        asset_df = asset_df.append(stock_df)
    asset_df = asset_df * worth
    final_df = pd.concat([final_df, asset_df])
tlist = [t for t in final_df.index.to_list() if t in tick_map.keys()]
for t in tlist:
    final_df.rename(index={t: tick_map.get(t)}, inplace=True)
final_df = final_df.groupby(final_df.index).sum()
final_df.columns = ["Percent"]
final_df.index.name = "Symbol"
final_df.to_csv(r"{}\{}_results.csv".format(dirpath, str(datetime.now().strftime('%y-%m-%d'))))
