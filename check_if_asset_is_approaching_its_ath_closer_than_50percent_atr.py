from statistics import mean
import pandas as pd
import os
import time
import datetime
import traceback
import datetime as dt
import tzlocal
import numpy as np
from collections import Counter
from sqlalchemy_utils import create_database,database_exists
import db_config
# from sqlalchemy import MetaData
from sqlalchemy import inspect
import logging
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

def calculate_atr_without_paranormal_bars_from_numpy_array(atr_over_this_period,
                  numpy_array_slice,
                  row_number_last_bar):
    list_of_true_ranges = []
    advanced_atr=False
    percentile_20=False
    percentile_80=False
    number_of_rows_in_numpy_array=len(numpy_array_slice)
    array_of_true_ranges=False
    print("numpy_array_slice")
    print(numpy_array_slice)
    print("atr_over_this_period")
    print(atr_over_this_period)
    print("row_number_last_bar")
    print(row_number_last_bar)
    try:
        if (row_number_last_bar+1 - number_of_rows_in_numpy_array) < 0:
            array_of_true_ranges=numpy_array_slice[:,2]-numpy_array_slice[:,3]
            percentile_20 = np.percentile ( array_of_true_ranges , 20 )
            percentile_80 = np.percentile ( array_of_true_ranges , 80 )
        else:
            array_of_true_ranges=numpy_array_slice[-atr_over_this_period-1:,2]-\
                                 numpy_array_slice[-atr_over_this_period-1:,3]

            percentile_20 = np.percentile ( array_of_true_ranges , 20 )
            percentile_80 = np.percentile ( array_of_true_ranges , 80 )
            print("percentile_80")
            print ( percentile_80 )
            print ( "percentile_20" )
            print ( percentile_20 )



    except:
        traceback.print_exc()
    print("array_of_true_ranges")
    print(array_of_true_ranges)
    list_of_non_rejected_true_ranges = []
    for true_range_in_array in array_of_true_ranges:

        if true_range_in_array >= percentile_20 and true_range_in_array <= percentile_80:
            list_of_non_rejected_true_ranges.append ( true_range_in_array )
    print("list_of_non_rejected_true_ranges")
    print ( list_of_non_rejected_true_ranges )
    advanced_atr = mean ( list_of_non_rejected_true_ranges )

    return advanced_atr



def find_if_level_is_round(level):
    level = str ( level )
    level_is_round=False

    if "." in level:  # quick check if it is decimal
        decimal_part = level.split ( "." )[1]
        # print(f"decimal part of {mirror_level} is {decimal_part}")
        if decimal_part=="0":
            print(f"level is round")
            print ( f"decimal part of {level} is {decimal_part}" )
            level_is_round = True
            return level_is_round
        elif decimal_part=="25":
            print(f"level is round")
            print ( f"decimal part of {level} is {decimal_part}" )
            level_is_round = True
            return level_is_round
        elif decimal_part == "5":
            print ( f"level is round" )
            print ( f"decimal part of {level} is {decimal_part}" )
            level_is_round = True
            return level_is_round
        elif decimal_part == "75":
            print ( f"level is round" )
            print ( f"decimal part of {level} is {decimal_part}" )
            level_is_round = True
            return level_is_round
        else:
            print ( f"level is not round" )
            print ( f"decimal part of {level} is {decimal_part}" )
            return level_is_round


def connect_to_postres_db_without_deleting_it_first(database):
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database

    engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                             isolation_level = 'AUTOCOMMIT' , echo = True )
    print ( f"{engine} created successfully" )

    # Create database if it does not exist.
    if not database_exists ( engine.url ):
        create_database ( engine.url )
        print ( f'new database created for {engine}' )
        connection=engine.connect ()
        print ( f'Connection to {engine} established after creating new database' )

    connection = engine.connect ()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection

def get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks):
    '''get list of all tables in db which is given as parameter'''
    inspector=inspect(engine_for_ohlcv_data_for_stocks)
    list_of_tables_in_db=inspector.get_table_names()

    return list_of_tables_in_db



def get_all_time_high_from_ohlcv_table(engine_for_ohlcv_data_for_stocks,
                                      table_with_ohlcv_table):
    table_with_ohlcv_data_df = \
        pd.read_sql_query ( f'''select * from "{table_with_ohlcv_table}"''' ,
                            engine_for_ohlcv_data_for_stocks )
    # print("table_with_ohlcv_data_df")
    # print ( table_with_ohlcv_data_df )

    all_time_high_in_stock=table_with_ohlcv_data_df["high"].max()
    print ( "all_time_high_in_stock" )
    print ( all_time_high_in_stock )

    return all_time_high_in_stock, table_with_ohlcv_data_df

# def drop_table(table_name,engine):
#     engine.execute (
#         f"DROP TABLE IF EXISTS {table_name};" )

from sqlalchemy import text

def drop_table(table_name, engine):
    conn = engine.connect()
    query = text(f"DROP TABLE IF EXISTS {table_name}")
    conn.execute(query)
    conn.close()

def get_last_close_price_of_asset(ohlcv_table_df):
    last_close_price=ohlcv_table_df["close"].iat[-1]
    return last_close_price

import os
import datetime

def create_text_file_and_writ_text_to_it(text, subdirectory_name):
  # Declare the path to the current directory
  current_directory = os.getcwd()

  # Create the subdirectory in the current directory if it does not exist
  subdirectory_path = os.path.join(current_directory, subdirectory_name)
  os.makedirs(subdirectory_path, exist_ok=True)

  # Get the current date
  today = datetime.datetime.now().strftime('%Y-%m-%d')

  # Create the file path by combining the subdirectory and the file name (today's date)
  file_path = os.path.join(subdirectory_path, "crypto_" + today + '.txt')

  # Check if the file exists
  if not os.path.exists(file_path):
    # Create the file if it does not exist
    open(file_path, 'a').close()

  # Open the file for writing
  with open(file_path, 'a') as f:
    # Redirect the output of the print function to the file
    print = lambda x: f.write(str(x) + '\n')

    # Output the text to the file using the print function
    print(text)

  # Close the file
  f.close()




def check_if_asset_is_approaching_its_ath(atr_over_this_period,
                                          db_where_ohlcv_data_for_stocks_is_stored,
                                          count_only_round_ath,
                                          db_where_levels_formed_by_ath_will_be,
                                          table_where_levels_formed_by_ath_will_be):

    levels_formed_by_ath_df=pd.DataFrame(columns = ["ticker",
                                                    "ath",
                                                    "exchange",
                                                    "short_name",
                                                    "timestamp_1",
                                                    "timestamp_2",
                                                    "timestamp_3"])
    list_of_assets_with_last_close_close_to_ath=[]


    engine_for_ohlcv_data_for_stocks , \
    connection_to_ohlcv_data_for_stocks = \
        connect_to_postres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored )

    engine_for_db_where_levels_formed_by_ath_will_be , \
    connection_to_db_where_levels_formed_by_ath_will_be = \
        connect_to_postres_db_without_deleting_it_first ( db_where_levels_formed_by_ath_will_be )

    drop_table ( table_where_levels_formed_by_ath_will_be ,
                 engine_for_db_where_levels_formed_by_ath_will_be )

    list_of_tables_in_ohlcv_db=\
        get_list_of_tables_in_db ( engine_for_ohlcv_data_for_stocks )
    counter=0
    for stock_name in list_of_tables_in_ohlcv_db:
        counter=counter+1
        print ( f'{stock_name} is'
                f' number {counter} out of {len ( list_of_tables_in_ohlcv_db )}\n' )
        all_time_high_in_stock, table_with_ohlcv_data_df=\
            get_all_time_high_from_ohlcv_table ( engine_for_ohlcv_data_for_stocks ,
                                            stock_name )

        calculate_volume_over_this_period = 30
        min_volume_over_n_days = min(table_with_ohlcv_data_df["volume"].tail(calculate_volume_over_this_period))
        print("min_volume_over_n_days")
        print(min_volume_over_n_days)
        if min_volume_over_n_days < 750:
            continue


        if count_only_round_ath==True:
            level_is_round_bool=find_if_level_is_round ( all_time_high_in_stock )
            if not level_is_round_bool:
                print(f"in {stock_name} level={all_time_high_in_stock} is not round and is ATL")
                continue
        last_close_price=np.nan
        try:
            last_close_price=get_last_close_price_of_asset ( table_with_ohlcv_data_df )
        except:
            traceback.print_exc()



        last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)
        last_two_years_of_data_numpy_array = last_two_years_of_data.to_numpy()
        last_bar_number = last_two_years_of_data.index[-1]
        advanced_atr = \
            calculate_atr_without_paranormal_bars_from_numpy_array(advanced_atr_over_this_period,
                                                                   last_two_years_of_data_numpy_array,
                                                                   last_bar_number)

        distance_from_last_close_price_to_ath=all_time_high_in_stock-last_close_price
        if distance_from_last_close_price_to_ath<=advanced_atr*0.5:
            # print(f"last closing price={last_close_price} is"
            #       f" within {percentage_between_ath_and_closing_price}% range to ath={all_time_high_in_stock}")
            list_of_assets_with_last_close_close_to_ath.append(stock_name)
            print(f"list_of_assets_with_last_close_closer_to_ath_than_50%ATR({advanced_atr_over_this_period})")
            print ( list_of_assets_with_last_close_close_to_ath )

            print(f"last_close_price_for_stock={stock_name}")
            print(last_close_price)
            print(f"advanced_atr_for_stock={stock_name}")
            print(advanced_atr)
            print(f"all_time_high_in_stock_for_stock={stock_name}")
            print(all_time_high_in_stock)
            print(f"distance_from_last_close_price_to_ath_in_stock_for_stock={stock_name}")
            print(distance_from_last_close_price_to_ath)

            df_where_high_equals_ath=\
                table_with_ohlcv_data_df[table_with_ohlcv_data_df["high"]==all_time_high_in_stock]
            print ( "df_where_high_equals_ath" )
            print ( df_where_high_equals_ath )
            exchange=table_with_ohlcv_data_df["exchange"].iat[0]
            short_name = table_with_ohlcv_data_df["short_name"].iat[0]


            levels_formed_by_ath_df.at[counter - 1 , "ticker"] = stock_name
            levels_formed_by_ath_df.at[counter - 1 , "exchange"] = exchange
            levels_formed_by_ath_df.at[counter - 1 , "short_name"] = short_name
            levels_formed_by_ath_df.loc[
                counter - 1, "model"] = "РАССТОЯНИЕ ОТ CLOSE ДО ATH <50% ATR"
            levels_formed_by_ath_df.at[counter - 1 , "ath"] = all_time_high_in_stock
            levels_formed_by_ath_df.at[counter - 1, "advanced_atr"] = advanced_atr
            levels_formed_by_ath_df.at[counter - 1, "advanced_atr_over_this_period"] =\
                advanced_atr_over_this_period

            for number_of_timestamp,timestamp_of_ath in enumerate(df_where_high_equals_ath.loc[:,"Timestamp"]):
                print("number_of_timestamp")
                print ( number_of_timestamp )
                print ( "timestamp_of_ath" )
                print ( timestamp_of_ath )
                levels_formed_by_ath_df.at[counter - 1 , f"timestamp_{number_of_timestamp+1}"]=\
                    timestamp_of_ath





            print("levels_formed_by_ath_df")
            print ( levels_formed_by_ath_df )


    levels_formed_by_ath_df.reset_index(inplace = True)
    string_for_output=f"\nСписок инструментов, в которых расстояние от " \
                      f"цены закрытия до цены исторического максимума <50% ATR({advanced_atr_over_this_period}):\n" \
                      f"{list_of_assets_with_last_close_close_to_ath}\n"
    # Use the function to create a text file with the text
    # in the subdirectory "current_rebound_breakout_and_false_breakout"
    create_text_file_and_writ_text_to_it(string_for_output, 'current_rebound_breakout_and_false_breakout')

    levels_formed_by_ath_df.to_sql(table_where_levels_formed_by_ath_will_be,
                                   engine_for_db_where_levels_formed_by_ath_will_be,
                                   if_exists = 'replace')
    print ( "levels_formed_by_ath_df" )
    print ( levels_formed_by_ath_df )




    pass
if __name__=="__main__":
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_data_for_usdt_pairs_for_1d_timeframe"
    count_only_round_ath=False
    db_where_levels_formed_by_ath_will_be="levels_formed_by_highs_and_lows_for_cryptos"
    table_where_levels_formed_by_ath_will_be = "current_asset_approaches_its_ath_closer_than_50percent_atr"

    if count_only_round_ath:
        db_where_levels_formed_by_ath_will_be="round_levels_formed_by_highs_and_lows_for_cryptos"
    percentage_between_ath_and_closing_price=10
    advanced_atr_over_this_period=30
    check_if_asset_is_approaching_its_ath(advanced_atr_over_this_period,
                                              db_where_ohlcv_data_for_stocks_is_stored,
                                              count_only_round_ath,
                                              db_where_levels_formed_by_ath_will_be,
                                              table_where_levels_formed_by_ath_will_be)