import pandas as pd
import numpy as np
import datetime
from pandas_datareader import data as pdr
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import EfficientCVaR
from collections import OrderedDict
from yahooquery import Ticker
import yfinance as yf

yf.pdr_override()

country_of_origin = "USA"
max_new_number = 10
max_new_number_exist = 5
end_date = datetime.datetime.today().strftime('%Y-%m-%d')
us_treasuries = ['^TNX', '^IRX', '^TYX', '^FVX']
us_treasuries_t = ['TNX', 'IRX', 'TYX', 'FVX']
alc_stocks = {"Large Cap", "Small or Mid Cap", "Foreign"}
num_day_years = 251

recommend = True
deposit = 0
start_date = '2013-01-01'

recommended_allocation = pd.read_excel('asset allocation.xlsx')
bonds_allocation = pd.read_excel('allocation_bonds.xlsx')

recommended_stocks = pd.read_csv('recomended_stocks.csv')
recommended_stocks['P/E'] = recommended_stocks['P/E'].astype('float')
recommended_stocks = recommended_stocks.sort_values(by=['P/E'], ascending=False)

all_stocks = pd.read_csv('all_stocks_info.csv')
all_stocks_model = all_stocks.set_index('Ticker')


def get_dict_stocks():
    new_stocks = OrderedDict()

    for st in alc_stocks:
        new_stocks[st] = []

    return new_stocks


def get_dict_bonds_weights(weights):
    dict_weights = {}

    for i in range(len(us_treasuries)):
        dict_weights[us_treasuries[i]] = weights[i]

    return dict_weights


def get_dict_values():
    value_stocks = OrderedDict()

    for st in alc_stocks:
        value_stocks[st] = 0

    for bond in us_treasuries_t:
        value_stocks[bond] = 0

    value_stocks['Cash'] = deposit

    return value_stocks


def merge_stocks(new_stocks, cl_stocks):
    merged_stocks = OrderedDict()

    for st in alc_stocks:
        merged_stocks[st] = new_stocks[st] + cl_stocks[st]

    return merged_stocks


def get_horizon(horizon):
    """
    :param horizon: horizon of investment (1: < 3
                                           2: 3 - 5
                                           3: 5 - 7
                                           4: 7 - 10
                                           5: 10 - 15
                                           6: > 15)
    """
    if horizon <= 3:
        return 1
    else:
        if horizon <= 5:
            return 2
        else:
            if horizon <= 7:
                return 3
            else:
                if horizon <= 10:
                    return 4
                else:
                    if horizon <= 15:
                        return 4
                    else:
                        return 6


def get_client_assets(cl_assets, cl_units):
    cl_df_assets = pd.DataFrame(data={'assets': ['Large Cap', 'Small or Mid Cap', 'Foreign', 'Bonds', 'Cash'],
                                      'client': [0, 0, 0, 0, deposit]})
    cl_df_bonds = pd.DataFrame(data={'bonds': us_treasuries_t, 'client': [0, 0, 0, 0]})

    cl_stocks = get_dict_stocks()
    init_portfolio_value = deposit
    init_bonds_value = 0
    for i in range(len(cl_assets)):
        tr = False
        ticker = cl_assets[i]
        print(ticker)

        for j in range(len(us_treasuries_t)):
            if ticker == us_treasuries_t[j]:
                print("here")
                last_price = float(pdr.get_data_yahoo(us_treasuries[j],
                                                      start=start_date, end=end_date)['Adj Close'][-1])
                init_portfolio_value += cl_units[i] * last_price
                init_bonds_value += cl_units[i] * last_price
                cl_df_assets.at[3, 'client'] += cl_units[i] * last_price
                cl_df_bonds.at[j, 'client'] += cl_units[i] * last_price
                tr = True
                break

        if not tr:
            last_price = float(pdr.get_data_yahoo(ticker, start=start_date, end=end_date)['Adj Close'][-1])
            init_portfolio_value += cl_units[i] * last_price

            if all_stocks_model.loc[ticker]['Country'] != country_of_origin:
                cl_stocks['Foreign'].append(ticker)
                cl_df_assets.at[2, 'client'] += cl_units[i] * last_price
                break

            cap = all_stocks_model.loc[ticker]['Cap']
            cl_stocks[cap].append(ticker)
            if cap == "Large Cap":
                cl_df_assets.at[0, 'client'] += cl_units[i] * last_price
            else:
                cl_df_assets.at[1, 'client'] += cl_units[i] * last_price

    if init_portfolio_value:
        cl_df_assets['client'] = cl_df_assets['client'].apply(lambda x: x / init_portfolio_value)

    if init_bonds_value:
        cl_df_bonds['client'] = cl_df_bonds['client'].apply(lambda x: x / init_bonds_value)

    return cl_stocks, init_portfolio_value, cl_df_assets, cl_df_bonds


def get_cl_data_close(tickers):
    cl_data_close = pd.DataFrame()
    for stock in tickers:
        if stock in us_treasuries_t:
            cl_data_close[stock] = pdr.get_data_yahoo('^' + stock, start=start_date, end=end_date)['Adj Close']
        else:
            cl_data_close[stock] = pdr.get_data_yahoo(stock, start=start_date, end=end_date)['Adj Close']
    return cl_data_close


def get_discrete(data_close_assets, money, weights_min):
    latest_prices = get_latest_prices(data_close_assets)
    discrete_allocation = DiscreteAllocation(weights_min, latest_prices, total_portfolio_value=money)
    allocation, leftover = discrete_allocation.greedy_portfolio()
    return allocation, leftover


def get_stock_allocation(assets, money):
    data_close_assets = get_cl_data_close(assets)
    returns_assets = data_close_assets.pct_change()
    mu = expected_returns.ema_historical_return(data_close_assets, compounding=True)

    efCVaR_portfolio = EfficientCVaR(mu, returns_assets)
    efCVaR_portfolio.min_cvar()
    weights_min = efCVaR_portfolio.clean_weights()

    return get_discrete(data_close_assets, money, weights_min)


def get_new_stocks(number):
    new_stocks = get_dict_stocks()
    for i in range(recommended_stocks.shape[0]):
        country_re = recommended_stocks.iloc[i]['Country']
        cap_re = recommended_stocks.iloc[i]['Cap']
        if country_of_origin != country_re:
            if len(new_stocks['Foreign']) != number:
                new_stocks['Foreign'].append(recommended_stocks.iloc[i]['Ticker'])
        else:
            if cap_re == 'Large':
                if len(new_stocks['Large Cap']) != number:
                    new_stocks['Large Cap'].append(recommended_stocks.iloc[i]['Ticker'])
            else:
                if len(new_stocks['Small or Mid Cap']) != number:
                    new_stocks['Small or Mid Cap'].append(recommended_stocks.iloc[i]['Ticker'])
        if (len(new_stocks['Foreign']) == number) \
                and (len(new_stocks['Large Cap']) == number) \
                and (len(new_stocks['Small or Mid Cap']) == number):
            break
    return new_stocks


def get_recommended(risk_profile, horizon):
    horizon = get_horizon(horizon)
    profile = risk_profile + ' ' + str(horizon)

    rec_portfolio_stocks = recommended_allocation[['assets', profile]]
    rec_portfolio_stocks[profile] = rec_portfolio_stocks[profile].astype('float')

    rec_portfolio_bonds = bonds_allocation[['bonds', profile]]
    rec_portfolio_bonds[profile] = rec_portfolio_bonds[profile].astype('float')

    return profile, rec_portfolio_stocks, rec_portfolio_bonds


def convert(balanced_model):
    assets = []
    units = []
    for i in range(balanced_model.shape[0] - 1):
        dic = balanced_model.iloc[i][1]
        for key, value in dic.items():
            assets.append(key)
            units.append(value)
    return assets, units


def get_weights(assets, units):
    weights = []
    portfolio_value = 0
    for i in range(len(assets)):
        if assets[i] in us_treasuries_t:
            last_price = float(pdr.get_data_yahoo('^' + assets[i], start=start_date, end=end_date)['Adj Close'][-1])
        else:
            last_price = float(pdr.get_data_yahoo(assets[i], start=start_date, end=end_date)['Adj Close'][-1])
        portfolio_value += units[i] * last_price
        weights.append(units[i] * last_price)
    weights = np.array(weights)
    weights = weights / portfolio_value
    return weights


def get_value(assets, units):
    weights = get_weights(assets, units)

    returns = get_cl_data_close(assets).pct_change()
    annual_returns = returns.mean() * num_day_years
    portfolio_return = np.sum(weights * annual_returns)

    cov_matrix = returns.cov()
    cov_matrix = cov_matrix * num_day_years
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    return portfolio_return, portfolio_volatility


def get_balancing(cl_assets, cl_units, risk_profile, horizon, money):
    balanced_portfolio = pd.DataFrame()
    profile, rec_portfolio_stocks, rec_portfolio_bonds = get_recommended(risk_profile, horizon)

    cl_stocks, init_portfolio_value, cl_df_assets, cl_df_bonds = get_client_assets(cl_assets, cl_units)
    money += init_portfolio_value

    rec_portfolio_stocks[profile] = rec_portfolio_stocks[profile].apply(lambda x: money * x / 100)
    rec_portfolio_bonds[profile] = rec_portfolio_bonds[profile].apply(lambda x: money * x / 100)

    if not cl_assets:
        cl_stocks = get_new_stocks(max_new_number)

    if recommend:
        new_stocks = get_new_stocks(max_new_number_exist)
        cl_stocks = merge_stocks(new_stocks, cl_stocks)

    leftover_stocks = 0

    for i in range(rec_portfolio_stocks.shape[0] - 2):  # does not include bonds and cash
        asset_type = rec_portfolio_stocks.iloc[i]['assets']
        allocated_money = rec_portfolio_stocks.iloc[i][profile]
        if allocated_money and cl_stocks[asset_type]:
            allocations, leftover = get_stock_allocation(cl_stocks[asset_type], allocated_money)
            leftover_stocks += leftover
            new = pd.DataFrame({"type": [asset_type], "assets": [allocations]})
            balanced_portfolio = pd.concat([balanced_portfolio, new], ignore_index=True)

    weights_min = np.array(rec_portfolio_bonds[profile])/float(rec_portfolio_bonds.iloc[-1][profile])
    weights_min = weights_min[:-1]
    allocation_bonds, leftover_bonds = get_discrete(get_cl_data_close(us_treasuries),
                                                    float(rec_portfolio_bonds.iloc[-1][profile]),
                                                    get_dict_bonds_weights(weights_min))
    allocation_bonds = {key[1:]: val for key, val in allocation_bonds.items()}

    new = pd.DataFrame({"type": ['Bonds'], "assets": [allocation_bonds]})
    balanced_portfolio = pd.concat([balanced_portfolio, new], ignore_index=True)

    cash_left = rec_portfolio_stocks.iloc[-1][profile] + leftover_bonds + leftover_stocks
    new = pd.DataFrame({"type": ['Cash/Deposit'], "assets": [{"cash": cash_left}]})
    balanced_portfolio = pd.concat([balanced_portfolio, new], ignore_index=True)

    return balanced_portfolio
