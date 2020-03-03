import yfinance as yf
import pprint
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import datetime

FILE = "investment_shares.csv"
PATH = r'C:\Users\Marco\Documents'
period = '5d'
interval = '1d'


def calc_cost_of_share(shares_df):
    """Creates column Cost equal to the total investment cost of the shares"""
    cost_of_share = pd.Series(shares_df.number_shares * shares_df.avg_cost)
    return cost_of_share


def calc_perc_cost_per_share(shares_df):
    """Creates a new column in df containing the value of cost per share in a percent with respect to the total cost"""
    sum_shares = calc_total_cost(shares_df)
    return (shares_df.cost / sum_shares) * 100


def calc_total_cost(shares_df):
    """Returns a value equal to the total sum of shares cost"""
    return shares_df.cost.sum(skipna=True)


def calc_total_no_shares(shares_df):
    """Sums total number of stocks bought"""
    return shares_df.no_shares.sum()


def df_by_type(shares_df, shares_type):
    """Creates a new df that matches the shares type"""
    new_df = shares_df[shares_df.type == shares_type].reset_index(drop=True)
    return new_df


def last_close(history_df):
    """Returns an int of the last Close value in the df provided. Prints warning if the last Close date does not equal
    to today's date"""
    close_value = history_df[history_df.index == history_df.index.max()]
    close_date = close_value.index.date
    current_time = datetime.datetime.now()
    last_friday = (current_time.date() - datetime.timedelta(days=current_time.weekday())
                   + datetime.timedelta(days=4, weeks=-1))
    if (current_time.isoweekday() > 5 and close_date != last_friday) or \
            (current_time.isoweekday() in range(1, 6) and close_date != current_time.date()):
        print("The last close date value is not for today's!")
    return close_value


def create_history_summary(shares_list, period='3mo', interval='1d'):
    """Creates a DF including history for  all elements in shares_list.
    Defaults to 3-month period with a 1-day interval"""
    summary_df = pd.DataFrame()
    for share in shares_list:
        try:
            ticker = yf.Ticker(share)
            history_df = ticker.history(period=period, interval=interval).rename(columns={'Close': share})[share]
            summary_df = summary_df.join(history_df, how='outer').dropna(axis=0)
        except:
            continue
    return summary_df


def join_shares_history_df(shares_df, history_df):
    """Joins (outer) dataframes by index = stock"""
    shares_df = shares_df.set_index('holding')
    history_transp = history_df.T
    history_transp.columns = history_transp.columns.date
    combined_df = shares_df.join(history_transp, how='outer')
    return combined_df


def calc_share_gain(combined_df, weekend):
    current_date = datetime.datetime.now().date()
    if not weekend:
        combined_df['gain_USD'] = (combined_df[current_date] * combined_df.number_shares) - combined_df.cost
    elif weekend:
        last_friday = (current_date - datetime.timedelta(days=current_date.weekday())
                       + datetime.timedelta(days=4, weeks=-1))
        combined_df['gain_USD'] = (combined_df[last_friday] * combined_df.number_shares) - combined_df.cost
    combined_df['gain_perc'] = combined_df['gain_USD'] / combined_df.cost * 100
    combined_df['gain_perc'] = combined_df['gain_perc'].round(2)
    return combined_df


def is_weekend():
    current_date = datetime.datetime.now().date()
    if current_date.isoweekday() in range(1, 6):
        return False
    elif current_date.isoweekday() > 5:
        return True
    else:
        print("Error calculating weekend check")


def is_dividend(shares_list):
    """Returns a list specifying if the ticker pays dividends"""
    dividend_list = []
    for share in shares_list:
        try:
            ticker = yf.Ticker(share)
            if not ticker.dividends.empty:
                dividend_list.append(True)
            else:
                dividend_list.append(False)
        except:
            continue
    return dividend_list


def dividend_df(shares_df):
    shares_list = create_shares_list(shares_df)
    return is_dividend(shares_list)


def load_csv(path, file):
    """Reads CSV with accordig path directory"""
    dir_path = os.path.join(path, file)
    return pd.read_csv(dir_path)


def create_shares_list(shares_df):
    """Returns a list of shares Tickers"""
    return shares_df.holding


def compile_shares_df(shares_df):
    shares_df['cost'] = calc_cost_of_share(shares_df)
    shares_df['perc_cost'] = calc_perc_cost_per_share(shares_df)
    shares_df['dividend'] = dividend_df(shares_df)
    return shares_df


# if __name__ == "__main__":
#     weekend_check = is_weekend()
#     shares_df = load_csv(PATH, FILE)
#     shares_list = create_shares_list(shares_df)
#     shares_df = compile_shares_df(shares_df)
#     history_df = create_history_summary(shares_list, period='1y', interval='1d')
#     last_close_value = last_close(history_df)
#     combined_df = join_shares_history_df(shares_df, history_df)
#     combined_df = calc_share_gain(combined_df, weekend_check)
#     combined_df.to_csv(r'C:\Users\Marco\Documents\investment_summary.csv')
#     history_df.to_csv(r'C:\Users\Marco\Documents\investment_history.csv')
