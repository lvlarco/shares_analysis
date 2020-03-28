import pandas as pd
from yfinance import Ticker, Tickers
import yfinance.utils as utils

yahoo_url = "https://finance.yahoo.com/quote"
etfdb_url = "https://etfdb.com/etf/{}/#holdings"


class Holding(Ticker):

    def __init__(self, holding):
        self.holding = holding.upper()
        super().__init__(self.holding)

    @property
    def return_short_name(self):
        """Returns the short name of the holding"""
        try:
            return super().info['shortName']
        except:
            return None

    def scrape_holdings(self, source="ETFDB"):
        """Returns a DataFrame including the top holdings of the ETF
        :param source: string, specifies from which website to scrape
        """
        source = source.lower()
        if source == "etfdb":
            scrape_url = etfdb_url.format(self.holding)
            holdings_list = pd.read_html(scrape_url)
            holdings_df = holdings_list[2].rename(columns={'Holding': 'Name'})
            holdings_df.drop(holdings_list[2].tail(1).index, inplace=True)
        elif source == "yahoo finance":
            scrape_url = "{}/{}/holdings".format(yahoo_url, self.holding)
            holdings_list = pd.read_html(scrape_url)
            holdings_df = holdings_list[0].dropna(axis=0)
        holdings_df["% Assets"] = holdings_df["% Assets"].str.replace('%', '').astype(float)
        holdings_df = holdings_df.set_index('Symbol')
        return holdings_df


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

    def scrape_json_value(self, key="summaryProfile", detail_key=None):
        """Returns the value of key value pair from Yahoo Finance scraping json. Default to summaryProfile"""
        try:
            scrape_url = 'https://finance.yahoo.com/quote'
            url = '%s/%s' % (scrape_url, self.holding)
            data = utils.get_json(url)
            return data[key][detail_key]
        except:
            pass
            # print(
            #     "Could not retreive {} from {}. Ticker must be a STOCK, cannot be ETF".format(detail_key.capitalize(),
            #                                                                                   self.holding))

    def scrape_json_values(self, detail_key=None):
        """Returns a list of Values for all tickers in tickers_list"""
        return_list = []
        for ticker in self.holdings_list:
            self.holding = ticker
            try:
                value = self.scrape_json_value(detail_key=detail_key)
                return_list.append(value)
            except:
                return_list.append(None)
        return return_list


# tick_list = ['BABA', 'NESN', '700', '2330', '005930', 'ROG', 'NOVN', '7203', 'HSBA',
#              'AZN', '1299', 'SAP', 'ASML', 'CSL', 'SAN']
# sh = ScrapeHolding(holdings_list=tick_list)
# country = sh.scrape_json_values(detail_key="country")
# h = Holding('vxus')
# holdings = h.scrape_holdings()
# print(holdings)
