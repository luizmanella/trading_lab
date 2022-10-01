import os
import json
import pandas as pd
from datetime import datetime, date
from pytz import timezone


'''
Checks to see if folder for symbol exists.
Ex. K:/Equities/AAPL
'''
def check_symbol_existence(data_source, symbol):
    symbol_path = '{data_source}/{symbol}'.format(data_source=data_source, symbol=symbol)
    symbol_path_reserved = '{data_source}/{symbol}reserved'.format(data_source=data_source, symbol=symbol)
    if os.path.exists(symbol_path) or os.path.exists(symbol_path_reserved):
        return True
    else:
        return False

'''
Builds a list of years to pull data for. Given that the database stores the data on yearly files.
For example, a user asks for data starting on 01-01-2018 and ending on 02-01-2022.
A final list of [2018, 2019, 2020, 2021, 2022] will yield from the function.
'''
def build_years_list(start_date, end_date):
    start_year = int(start_date.split('-')[0])
    end_year = int(end_date.split('-')[0])
    year_difference = end_year - start_year
    year_list = []
    dynamic_year = start_year
    for count in range(0,year_difference+1):
        year_list.append(dynamic_year)
        dynamic_year += 1
    return year_list

'''
Retrieves the files necessary from the database, merge the data together, and turn into a Pandas data frame.
'''
def retrieve_equities_price_time_bars_data(data_source, symbol, years_list, timespan):
    symbol_path = '{data_source}/{symbol}'.format(data_source=data_source, symbol=symbol)
    symbol_path_reserved = '{data_source}/{symbol}reserved'.format(data_source=data_source, symbol=symbol)
    if os.path.exists(symbol_path):
        database_symbol = symbol
    elif os.path.exists(symbol_path_reserved):
        database_symbol = symbol + 'reserved'

    database_symbol_path_data_directory = '{data_source}/{symbol}/Price/Adjusted/Time Bars/{timespan}'.format(data_source=data_source, symbol=database_symbol, timespan=timespan)
    database_symbol_files = os.listdir(database_symbol_path_data_directory)
    database_files_to_pull = []
    for year in years_list:
        for year_file in database_symbol_files:
            if str(year) in year_file:
                database_files_to_pull.append('{database_symbol_path_data_directory}/{year_file}'.format(database_symbol_path_data_directory=database_symbol_path_data_directory,
                                                                                                         year_file=year_file))

    database_total_data = []
    for year_file in database_files_to_pull:
        with open(year_file, mode='r') as json_file:
            try:
                database_total_data.extend(json.loads(json_file.read()))
            except Exception as e:
                print ('ERROR: Exception loading "{year_file}".'.format(year_file=year_file))

    data = pd.DataFrame(database_total_data)
    if ({'a', 'op'}.issubset(data.columns)):
        data.drop(['a', 'op'], axis=1, inplace=True)
    return data

'''
Create a new field for "datetime_eastern" that is a datetime object obtained from the "time" field which is epoch msec UTC.
Set the "datetime_eastern" column as the index, and convert the timezone from UTC to "US/Eastern".
Filter the data to the user requested timeframe.
'''
def filter_database_to_specified_timeframe(data, start_date, end_date):
    data['datetime_eastern'] = pd.to_datetime(data['time'], unit='ms', utc=True)
    data.set_index('datetime_eastern', inplace=True)
    data = data.tz_convert(tz='US/Eastern')
    data = data.loc[(data.index >= start_date) & (data.index < end_date)]
    return data

'''
Simple filter for removing extended trading hours.
'''
def filter_out_extended_trading_hours(data):
    data = data.between_time('09:30', '15:59')
    return data

'''
### Symbol
    - Accepts a single symbol such as "AAPL"
### Start Date / End Date
    - Must be in the format "YYYY-MM-DD"
### Adjusted
    - Accepts either "True" or "False"
'''
def equities_get_historical_price_time_bars(data_source, symbol, timespan, start_date = '2000-01-01', end_date = datetime.now(timezone('US/Eastern')).strftime('%Y-%m-%d'), extended_market_hours = False):
    if (check_symbol_existence(data_source, symbol)):
        years_list = build_years_list(start_date, end_date)
        data = retrieve_equities_price_time_bars_data(data_source, symbol, years_list, timespan)
        filtered_data = filter_database_to_specified_timeframe(data, start_date, end_date)
        if (timespan == 'Hourly' or timespan == 'Minute') and not extended_market_hours:
            filtered_data = filter_out_extended_trading_hours(filtered_data)
        return filtered_data
    else:
        print ('ERROR: Symbol: {symbol} does not exist in database.'.format(symbol=symbol))

#### EXAMPLES - All Options
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Daily', start_date='2018-01-01', end_date='2022-04-06', extended_market_hours=False)
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Hourly', start_date='2018-01-01', end_date='2022-04-06', extended_market_hours=False)
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Minute', start_date='2018-01-01', end_date='2022-04-06', extended_market_hours=False)

#### EXAMPLES - Start and End Only
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Daily', start_date='2018-01-01', end_date='2022-04-06')
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Hourly', start_date='2018-01-01', end_date='2022-04-06')
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Minute', start_date='2018-01-01', end_date='2022-04-06')

#### EXAMPLES - Start Only (End date is automatically populated with the current date.)
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Daily', start_date='2018-01-01')
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Hourly', start_date='2018-01-01')
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Minute', start_date='2018-01-01')

#### EXAMPLES - Required Only (Start date is default set to "2000-01-01". End date is automatically populated with the current date.)
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Daily')
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Hourly')
# data = equities_get_historical_price_time_bars(data_source='P:/Equities', symbol='AAPL', timespan='Minute')