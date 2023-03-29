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

from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import check_ath_breakout
from check_if_ath_or_atl_was_not_broken_over_long_periond_of_time import check_atl_breakout

def print_df_to_file(dataframe, subdirectory_name):
    series = dataframe.squeeze()
    # get today's date
    date_today = datetime.datetime.now().strftime("%Y-%m-%d")

    # create file name
    file_name = f"atr_level_sl_tp_for_cryptos_{date_today}.txt"

    # create directory if it doesn't exist
    if not os.path.exists(subdirectory_name):
        os.makedirs(subdirectory_name)

    with open(os.path.join(subdirectory_name, file_name), "a") as file:
        # print horizontal line
        file.write("\n"+"+" * 111 + "\n")

        # print series to file
        file.write(str(series))

        # print horizontal line again
        file.write("\n" + "+" * 111)

    print(f"Series appended to {file_name} in {subdirectory_name}")
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
    print("table_with_ohlcv_data_df")
    print ( table_with_ohlcv_data_df )

    all_time_high_in_stock=table_with_ohlcv_data_df["high"].max()
    print ( "all_time_high_in_stock" )
    print ( all_time_high_in_stock )

    return all_time_high_in_stock, table_with_ohlcv_data_df

def get_all_time_low_from_ohlcv_table(engine_for_ohlcv_data_for_stocks,
                                      table_with_ohlcv_table):
    table_with_ohlcv_data_df = \
        pd.read_sql_query ( f'''select * from "{table_with_ohlcv_table}"''' ,
                            engine_for_ohlcv_data_for_stocks )
    print("table_with_ohlcv_data_df")
    print ( table_with_ohlcv_data_df )

    all_time_low_in_stock=table_with_ohlcv_data_df["low"].min()
    print ( "all_time_low_in_stock" )
    print ( all_time_low_in_stock )

    return all_time_low_in_stock, table_with_ohlcv_data_df

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

def get_date_with_and_without_time_from_timestamp(timestamp):

    try:
        open_time = \
            dt.datetime.fromtimestamp ( timestamp  )
        # last_timestamp = historical_data_for_crypto_ticker_df["Timestamp"].iloc[-1]
        # last_date_with_time = historical_data_for_crypto_ticker_df["open_time"].iloc[-1]
        # print ( "type(last_date_with_time)\n" , type ( last_date_with_time ) )
        # print ( "last_date_with_time\n" , last_date_with_time )
        date_with_time = open_time.strftime ( "%Y/%m/%d %H:%M:%S" )
        date_without_time = date_with_time.split ( " " )
        print ( "date_with_time\n" , date_without_time[0] )
        date_without_time = date_without_time[0]
        print ( "date_without_time\n" , date_without_time )
        # date_without_time = date_without_time.replace ( "/" , "_" )
        # date_with_time = date_with_time.replace ( "/" , "_" )
        # date_with_time = date_with_time.replace ( " " , "__" )
        # date_with_time = date_with_time.replace ( ":" , "_" )
        return date_with_time,date_without_time
    except:
        return timestamp,timestamp


# def get_high_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,row_number_of_bpu1):
#     # get high of bpu2
#     high_of_bpu2=False
#     try:
#         if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
#             print ( "there is no bpu2" )
#         else:
#             high_of_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "high"]
#             print ( "high_of_bpu2_inside_function" )
#             print ( high_of_bpu2 )
#     except:
#         traceback.print_exc ()
#     return high_of_bpu2

def get_ohlc_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,row_number_of_bpu1):
    # get ohlcv of bpu2
    low_of_bpu2=False
    high_of_bpu2 = False
    open_of_bpu2 = False
    close_of_bpu2 = False
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no bpu2" )
        else:
            low_of_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "low"]
            open_of_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "open"]
            close_of_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "close"]
            high_of_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "high"]
            print ( "high_of_bpu2_inside_function" )
            print ( high_of_bpu2 )
    except:
        traceback.print_exc ()
    return open_of_bpu2,high_of_bpu2,low_of_bpu2,close_of_bpu2

def get_ohlc_of_possible_breakout_bar(truncated_high_and_low_table_with_ohlcv_data_df,
                                         row_number_of_bpu1):
    low_of_possible_breakout_bar = False
    high_of_possible_breakout_bar = False
    open_of_possible_breakout_bar = False
    close_of_possible_breakout_bar = False
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 2 == row_number_of_bpu1:
            print ( "there is no possible_breakout_bar" )
        elif len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no possible_breakout_bar" )
        else:
            low_of_possible_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "low"]
            open_of_possible_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "open"]
            close_of_possible_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "close"]
            high_of_possible_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "high"]
            # print ( "high_of_possible_breakout_bar" )
            # print ( high_of_possible_breakout_bar )
    except:
        traceback.print_exc ()
    return open_of_possible_breakout_bar , high_of_possible_breakout_bar , low_of_possible_breakout_bar , close_of_possible_breakout_bar

def get_timestamp_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,row_number_of_bpu1):
    # get high of bpu2
    timestamp_bpu2=False
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no bpu2" )
        else:
            timestamp_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "Timestamp"]
            # print ( "high_of_bpu2" )
            # print ( high_of_bpu2 )
    except:
        traceback.print_exc ()
    return timestamp_bpu2

def get_volume_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,row_number_of_bpu1):
    # get high of bpu2
    volume_bpu2=False
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no bpu2" )
        else:
            volume_bpu2 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 1 , "volume"]
            # print ( "high_of_bpu2" )
            # print ( high_of_bpu2 )
    except:
        traceback.print_exc ()
    return volume_bpu2

def calculate_atr(atr_over_this_period,
                  truncated_high_and_low_table_with_ohlcv_data_df,
                  row_number_of_bpu1):
    # calcualte atr over 5 days before bpu2. bpu2 is not included

    list_of_true_ranges = []
    for row_number_for_atr_calculation_backwards in range ( 0 , atr_over_this_period ):
        try:
            if (row_number_of_bpu1 - row_number_for_atr_calculation_backwards)<0:
                continue
            if truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 +1 , "high"]:
                high_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 +1 - row_number_for_atr_calculation_backwards , "high"]
                low_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 +1 - row_number_for_atr_calculation_backwards , "low"]
                true_range = abs ( high_for_atr_calculation - low_for_atr_calculation )
            else:
                high_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 - row_number_for_atr_calculation_backwards , "high"]
                low_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 - row_number_for_atr_calculation_backwards , "low"]
                true_range = abs ( high_for_atr_calculation - low_for_atr_calculation )
            # print("true_range")
            # print(true_range)

            list_of_true_ranges.append ( true_range )

        except:
            traceback.print_exc ()
    atr = mean ( list_of_true_ranges )
    # print ( "atr" )
    # print ( atr )
    return atr

def calculate_advanced_atr(atr_over_this_period,
                  truncated_high_and_low_table_with_ohlcv_data_df,
                  row_number_of_bpu1):


    list_of_true_ranges = []
    for row_number_for_atr_calculation_backwards in range ( 0 , atr_over_this_period ):
        try:
            if (row_number_of_bpu1 - row_number_for_atr_calculation_backwards) < 0:
                continue
            if truncated_high_and_low_table_with_ohlcv_data_df.loc[
                row_number_of_bpu1 + 1 , "high"]:
                high_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 + 1 - row_number_for_atr_calculation_backwards , "high"]
                low_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 + 1 - row_number_for_atr_calculation_backwards , "low"]
                true_range = abs ( high_for_atr_calculation - low_for_atr_calculation )
            else:
                high_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 - row_number_for_atr_calculation_backwards , "high"]
                low_for_atr_calculation = truncated_high_and_low_table_with_ohlcv_data_df.loc[
                    row_number_of_bpu1 - row_number_for_atr_calculation_backwards , "low"]
                true_range = abs ( high_for_atr_calculation - low_for_atr_calculation )
            # print("true_range")
            # print(true_range)

            list_of_true_ranges.append ( true_range )

        except:
            traceback.print_exc ()
    percentile_20=np.percentile(list_of_true_ranges,20)
    percentile_80 = np.percentile ( list_of_true_ranges , 80 )
    # print ( "list_of_true_ranges" )
    # print ( list_of_true_ranges )
    # print ( "percentile_20" )
    # print ( percentile_20 )
    # print ( "percentile_80" )
    # print ( percentile_80 )
    list_of_non_rejected_true_ranges=[]
    for true_range_in_list in list_of_true_ranges:
        if true_range_in_list>=percentile_20 and true_range_in_list<=percentile_80:
            list_of_non_rejected_true_ranges.append(true_range_in_list)
    atr=mean(list_of_non_rejected_true_ranges)

    return atr
def calculate_atr_without_paranormal_bars_from_numpy_array(atr_over_this_period,
                  numpy_array_slice,
                  row_number_last_bar):
    list_of_true_ranges = []
    advanced_atr=False
    percentile_20=False
    percentile_80=False
    number_of_rows_in_numpy_array=len(numpy_array_slice)
    array_of_true_ranges=False
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
            # print("percentile_80")
            # print ( percentile_80 )
            # print ( "percentile_20" )
            # print ( percentile_20 )



    except:
        traceback.print_exc()

    list_of_non_rejected_true_ranges = []
    for true_range_in_array in array_of_true_ranges:

        if true_range_in_array >= percentile_20 and true_range_in_array <= percentile_80:
            list_of_non_rejected_true_ranges.append ( true_range_in_array )
    # print("list_of_non_rejected_true_ranges")
    # print ( list_of_non_rejected_true_ranges )
    advanced_atr = mean ( list_of_non_rejected_true_ranges )

    return advanced_atr


def trunc(num, digits):
    if num!=False:
        try:
            l = str(float(num)).split('.')
            digits = min(len(l[1]), digits)
            return float(l[0] + '.' + l[1][:digits])
        except:
            traceback.print_exc()
    else:
        return False
def check_if_bsu_bpu1_bpu2_do_not_open_into_atl_level (
        acceptable_backlash,atr,open_of_bsu , open_of_bpu1 , open_of_bpu2 ,
        high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
        low_of_bsu , low_of_bpu1 , low_of_bpu2 ):
    three_bars_do_not_open_into_level=False

    luft_for_bsu=(high_of_bsu-low_of_bsu)*acceptable_backlash
    luft_for_bpu1 = (high_of_bpu1 - low_of_bpu1) * acceptable_backlash
    luft_for_bpu2 = (high_of_bpu2 - low_of_bpu2) * acceptable_backlash

    if abs(open_of_bsu-low_of_bsu)>=luft_for_bsu:
        bsu_ok=True
    else:
        bsu_ok=False

    if abs(open_of_bpu1-low_of_bpu1)>=luft_for_bpu1:
        bpu1_ok=True
    else:
        bpu1_ok=False

    if abs(open_of_bpu2-low_of_bpu2)>=luft_for_bpu2:
        bpu2_ok=True
    else:
        bpu2_ok=False

    if all([bsu_ok,bpu1_ok,bpu2_ok]):
        three_bars_do_not_open_into_level=True
    else:
        three_bars_do_not_open_into_level = False

    return three_bars_do_not_open_into_level



def check_if_bsu_bpu1_bpu2_do_not_close_into_atl_level ( acceptable_backlash,atr,close_of_bsu , close_of_bpu1 , close_of_bpu2 ,
                                                                    high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
                                                                    low_of_bsu , low_of_bpu1 , low_of_bpu2 ):
    three_bars_do_not_close_into_level = False

    luft_for_bsu = (high_of_bsu - low_of_bsu) * acceptable_backlash
    luft_for_bpu1 = (high_of_bpu1 - low_of_bpu1) * acceptable_backlash
    luft_for_bpu2 = (high_of_bpu2 - low_of_bpu2) * acceptable_backlash

    if abs(close_of_bsu - low_of_bsu) >= luft_for_bsu:
        bsu_ok = True
    else:
        bsu_ok = False

    if abs(close_of_bpu1 - low_of_bpu1) >= luft_for_bpu1:
        bpu1_ok = True
    else:
        bpu1_ok = False

    if abs(close_of_bpu2 - low_of_bpu2) >= luft_for_bpu2:
        bpu2_ok = True
    else:
        bpu2_ok = False

    if all ( [bsu_ok , bpu1_ok , bpu2_ok] ):
        three_bars_do_not_close_into_level = True
    else:
        three_bars_do_not_close_into_level = False

    return three_bars_do_not_close_into_level


def check_if_bsu_bpu1_bpu2_do_not_open_into_ath_level(
        acceptable_backlash , atr , open_of_bsu , open_of_bpu1 , open_of_bpu2 ,
        high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
        low_of_bsu , low_of_bpu1 , low_of_bpu2):
    three_bars_do_not_open_into_level = False

    luft_for_bsu = (high_of_bsu - low_of_bsu) * acceptable_backlash
    luft_for_bpu1 = (high_of_bpu1 - low_of_bpu1) * acceptable_backlash
    luft_for_bpu2 = (high_of_bpu2 - low_of_bpu2) * acceptable_backlash

    if abs(high_of_bsu-open_of_bsu) >= luft_for_bsu:
        bsu_ok = True
    else:
        bsu_ok = False

    if abs(high_of_bpu1-open_of_bpu1) >= luft_for_bpu1:
        bpu1_ok = True
    else:
        bpu1_ok = False

    if abs(high_of_bpu2-open_of_bpu2) >= luft_for_bpu2:
        # print ( "luft_for_bpu2" )
        # print ( luft_for_bpu2 )
        # print ( "high_of_bpu2 - open_of_bpu2" )
        # print ( high_of_bpu2 - open_of_bpu2 )
        bpu2_ok = True
        # print ( "bpu2_ok" )
        # print ( bpu2_ok )
    else:
        # print ( "luft_for_bpu2" )
        # print ( luft_for_bpu2 )
        # print ( "high_of_bpu2" )
        # print ( high_of_bpu2 )
        # print ( "open_of_bpu2" )
        # print ( open_of_bpu2 )
        # print ( "high_of_bpu2 - open_of_bpu2" )
        # print ( high_of_bpu2 - open_of_bpu2 )
        bpu2_ok = False
        # print ( "bpu2_ok" )
        # print ( bpu2_ok )

    if all ( [bsu_ok , bpu1_ok , bpu2_ok] ):
        three_bars_do_not_open_into_level = True
    else:
        three_bars_do_not_open_into_level = False

    return three_bars_do_not_open_into_level


def check_if_bsu_bpu1_bpu2_do_not_close_into_ath_level(acceptable_backlash , atr , close_of_bsu , close_of_bpu1 ,
                                                       close_of_bpu2 ,
                                                       high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
                                                       low_of_bsu , low_of_bpu1 , low_of_bpu2):
    three_bars_do_not_close_into_level = False

    luft_for_bsu = (high_of_bsu - low_of_bsu) * acceptable_backlash
    luft_for_bpu1 = (high_of_bpu1 - low_of_bpu1) * acceptable_backlash
    luft_for_bpu2 = (high_of_bpu2 - low_of_bpu2) * acceptable_backlash

    if abs(high_of_bsu - close_of_bsu) >= luft_for_bsu:
        bsu_ok = True
    else:
        bsu_ok = False

    if abs(high_of_bpu1 - close_of_bpu1) >= luft_for_bpu1:
        bpu1_ok = True
    else:
        bpu1_ok = False

    if abs(high_of_bpu2 - close_of_bpu2) >= luft_for_bpu2:

        bpu2_ok = True
    else:
        bpu2_ok = False

    if all ( [bsu_ok , bpu1_ok , bpu2_ok] ):
        three_bars_do_not_close_into_level = True
    else:
        three_bars_do_not_close_into_level = False

    return three_bars_do_not_close_into_level

def calculate_number_of_bars_which_fulfil_suppression_criterion_to_ath(last_several_rows_in_np_array_slice,
                                                      number_of_last_row_in_np_array_row_slice):
    number_of_bars_which_fulfil_suppression_criterion=0
    for number_of_bar_backward in range(1,len(last_several_rows_in_np_array_slice)):
        current_low=last_several_rows_in_np_array_slice[-number_of_bar_backward][3]
        previous_low=last_several_rows_in_np_array_slice[-number_of_bar_backward-1][3]
        # print ( "last_several_rows_in_np_array_slice" )
        # print(last_several_rows_in_np_array_slice)
        # print ( "current_low" )
        # print ( current_low )
        # print ( "previous_low" )
        # print ( previous_low )
        if current_low<previous_low:
            break
        else:
            number_of_bars_which_fulfil_suppression_criterion=\
                number_of_bars_which_fulfil_suppression_criterion+1
    return number_of_bars_which_fulfil_suppression_criterion

def calculate_number_of_bars_which_fulfil_suppression_criterion_to_atl(last_several_rows_in_np_array_slice,
                                                      number_of_last_row_in_np_array_row_slice):
    number_of_bars_which_fulfil_suppression_criterion=0
    for number_of_bar_backward in range(1,len(last_several_rows_in_np_array_slice)):
        current_high=last_several_rows_in_np_array_slice[-number_of_bar_backward][2]
        previous_high=last_several_rows_in_np_array_slice[-number_of_bar_backward-1][2]
        # print ( "last_several_rows_in_np_array_slice" )
        # print(last_several_rows_in_np_array_slice)
        # print ( "current_low" )
        # print ( current_low )
        # print ( "previous_low" )
        # print ( previous_low )
        if current_high>previous_high:
            break
        else:
            number_of_bars_which_fulfil_suppression_criterion=\
                number_of_bars_which_fulfil_suppression_criterion+1
    return number_of_bars_which_fulfil_suppression_criterion

def find_min_volume_over_last_n_days (
                            last_n_rows_for_volume_check ):

    min_volume_over_last_n_days = np.amin ( last_n_rows_for_volume_check )

    return min_volume_over_last_n_days

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







def search_for_tickers_with_breakout_situations(db_where_ohlcv_data_for_stocks_is_stored,
                                          db_where_ticker_which_may_have_fast_breakout_situations,
                                               table_where_ticker_which_may_have_fast_breakout_situations_from_ath_will_be ,
                                               table_where_ticker_which_may_have_fast_breakout_situations_from_atl_will_be,
                                               advanced_atr_over_this_period,
                                                number_of_bars_in_suppression_to_check_for_volume_acceptance
                                               ):


    engine_for_ohlcv_data_for_stocks , \
    connection_to_ohlcv_data_for_stocks = \
        connect_to_postres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored )

    engine_for_db_where_ticker_which_may_have_fast_breakout_situations , \
    connection_to_db_where_ticker_which_may_have_fast_breakout_situations = \
        connect_to_postres_db_without_deleting_it_first ( db_where_ticker_which_may_have_fast_breakout_situations )

    drop_table ( table_where_ticker_which_may_have_fast_breakout_situations_from_ath_will_be ,
                 engine_for_db_where_ticker_which_may_have_fast_breakout_situations )
    # drop_table ( table_where_ticker_which_may_have_fast_breakout_situations_from_atl_will_be ,
    #              engine_for_db_where_ticker_which_may_have_fast_breakout_situations )

    list_of_tables_in_ohlcv_db=\
        get_list_of_tables_in_db ( engine_for_ohlcv_data_for_stocks )
    counter=0
    list_of_tickers_where_ath_is_also_limit_level=[]
    list_of_tickers_where_atl_is_also_limit_level = []
    list_of_stocks_approaching_ath=[]
    list_of_stocks_approaching_atl = []

    for stock_name in list_of_tables_in_ohlcv_db:

        try:

            counter=counter+1
            print ( f'{stock_name} is'
                    f' number {counter} out of {len ( list_of_tables_in_ohlcv_db )}\n' )



            table_with_ohlcv_data_df = \
                pd.read_sql_query ( f'''select * from "{stock_name}"''' ,
                                    engine_for_ohlcv_data_for_stocks )

            if table_with_ohlcv_data_df.empty:
                continue

            exchange = table_with_ohlcv_data_df.loc[0 , "exchange"]
            short_name = table_with_ohlcv_data_df.loc[0 , 'short_name']

            try:
                asset_type, maker_fee, taker_fee, url_of_trading_pair = \
                    get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(
                        table_with_ohlcv_data_df)
            except:
                traceback.print_exc()



            # truncated_high_and_low_table_with_ohlcv_data_df[["high","low"]]=table_with_ohlcv_data_df[["high","low"]].round(decimals=2)
            # print("truncated_high_and_low_table_with_ohlcv_data_df")
            # print ( truncated_high_and_low_table_with_ohlcv_data_df)
            # print ( "before_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df.head(10).to_string() )




            #truncate high and low to two decimal number

            table_with_ohlcv_data_df["high"] = \
                table_with_ohlcv_data_df["high"].apply ( round , args = (20,) )
            table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply ( round , args = (20,) )
            table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply ( round , args = (20,) )
            table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply ( round , args = (20,) )

            initial_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy ()
            truncated_high_and_low_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy ()

            truncated_high_and_low_table_with_ohlcv_data_df["high"]=\
                table_with_ohlcv_data_df["high"].apply(round,args = (20,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply ( round , args = (20,) )
            truncated_high_and_low_table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply ( round , args = (20,) )
            truncated_high_and_low_table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply ( round , args = (20,) )


            # round high and low to two decimal number

            truncated_high_and_low_table_with_ohlcv_data_df["high"]=\
                table_with_ohlcv_data_df["high"].apply(round,args = (20,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply ( round , args = (20,) )

            # print ( "after_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df )
            #####################

            number_of_all_rows_in_df=len(truncated_high_and_low_table_with_ohlcv_data_df)

            table_with_ohlcv_data_df_slice =\
                truncated_high_and_low_table_with_ohlcv_data_df[["Timestamp" , "open" , "high","low","close","volume"]]
            table_with_ohlcv_data_df_slice=table_with_ohlcv_data_df_slice.tail(365*2)
            table_with_ohlcv_data_df_slice_numpy_array=table_with_ohlcv_data_df_slice.to_numpy()
            number_of_rows_in_numpy_array=table_with_ohlcv_data_df_slice_numpy_array.shape[0]
            current_atl_in_iteration_over_numpy_array=False
            current_ath_in_iteration_over_numpy_array = False

            row_of_last_atl_in_iteration_over_numpy_array = False
            row_of_last_ath_in_iteration_over_numpy_array = False

            # for number_of_last_row_in_np_array_row_slice in range(1,number_of_rows_in_numpy_array):
            last_several_rows_in_np_array_slice=\
                table_with_ohlcv_data_df_slice_numpy_array
            number_of_last_row_in_np_array_row_slice=len(last_several_rows_in_np_array_slice)-1
            # print ( "first_several_rows_on_np_array_slice" )
            # print ( last_several_rows_in_np_array_slice )

            maxInColumns = np.amax ( last_several_rows_in_np_array_slice , axis = 0 )
            minInColumns = np.amin ( last_several_rows_in_np_array_slice , axis = 0 )
            ath=maxInColumns[2]
            atl=minInColumns[3]

            mask_for_non_atl_values_exclusion =\
                (last_several_rows_in_np_array_slice[: , 3] == atl)
            last_several_rows_in_np_array_slice_only_atl=\
                last_several_rows_in_np_array_slice[mask_for_non_atl_values_exclusion , :]

            mask_for_non_ath_values_exclusion = \
                (last_several_rows_in_np_array_slice[: , 2] == ath)
            last_several_rows_in_np_array_slice_only_ath = \
                last_several_rows_in_np_array_slice[mask_for_non_ath_values_exclusion , :]
######################################################################
            # find ath
            if len(last_several_rows_in_np_array_slice_only_ath)>=1:

                ath=\
                    last_several_rows_in_np_array_slice_only_ath[0][2]
                # print ( "ath" )
                # print ( ath )
                current_ath_in_iteration_over_numpy_array=ath
                timestamp_of_current_ath =\
                    last_several_rows_in_np_array_slice_only_ath[-1][0]
                volume_in_current_ath=last_several_rows_in_np_array_slice_only_ath[-1][5]


                column_of_timestamps = last_several_rows_in_np_array_slice[: , 0]
                row_of_last_ath_which_is_limit_level_also = \
                    list ( column_of_timestamps ).index ( timestamp_of_current_ath )
                # print ( "row_of_last_ath_which_is_limit_level_also" )
                # print ( row_of_last_ath_which_is_limit_level_also )

                # check if the found ath is legit and no broken for the last 2 years
                ath_is_not_broken_for_a_long_time = True
                try:
                    number_of_days_where_ath_was_not_broken = 366 * 2
                    table_with_ohlcv_data_df_slice_numpy_array = table_with_ohlcv_data_df.to_numpy(copy=True)
                    ath_is_not_broken_for_a_long_time = check_ath_breakout(
                        table_with_ohlcv_data_df_slice_numpy_array,
                        number_of_days_where_ath_was_not_broken,
                        ath,
                        row_of_last_ath_which_is_limit_level_also)
                    print(f"ath={ath}")
                    print(f"ath_is_not_broken_for_a_long_time for {stock_name}={ath_is_not_broken_for_a_long_time}")

                except:
                    pass

                if ath_is_not_broken_for_a_long_time == False:
                    continue

                current_high = last_several_rows_in_np_array_slice[-1][2]
                current_low = last_several_rows_in_np_array_slice[-1][3]

                current_timestamp = last_several_rows_in_np_array_slice[-1][0]



                current_close = last_several_rows_in_np_array_slice[-1][4]
                if volume_in_current_ath>=750:
                    last_n_rows_for_volume_check=last_several_rows_in_np_array_slice[-number_of_bars_in_suppression_to_check_for_volume_acceptance:,5]
                    min_volume_over_last_n_days=find_min_volume_over_last_n_days(last_n_rows_for_volume_check)
                    if min_volume_over_last_n_days>=750:

                        if current_high<=current_ath_in_iteration_over_numpy_array:
                            if number_of_last_row_in_np_array_row_slice>row_of_last_ath_which_is_limit_level_also+3:
                                advanced_atr=calculate_atr_without_paranormal_bars_from_numpy_array ( advanced_atr_over_this_period,
                                                                                         last_several_rows_in_np_array_slice ,
                                                                                         number_of_last_row_in_np_array_row_slice )
                                advanced_atr=round(advanced_atr,20)
                                #проверить что поджатие на маленьких барах
                                try:
                                    prev_high = last_several_rows_in_np_array_slice[-2][2]
                                    prev_low = last_several_rows_in_np_array_slice[-2][3]
                                    prev_prev_high = last_several_rows_in_np_array_slice[-3][2]
                                    prev_prev_low = last_several_rows_in_np_array_slice[-3][3]
                                    current_true_range = current_high - current_low
                                    prev_true_range = prev_high - prev_low
                                    prev_prev_true_range=prev_prev_high-prev_prev_low
                                    if current_true_range>advanced_atr or prev_true_range>advanced_atr or prev_prev_true_range>advanced_atr:
                                        continue
                                except:
                                    pass




                                # print(f"advanced_atr_for_row={number_of_last_row_in_np_array_row_slice}")
                                # print ( advanced_atr )
                                # distance_between_current_ath_and_current_close=\
                                #     current_ath_in_iteration_over_numpy_array-current_close
                                # if distance_between_current_ath_and_current_close>advanced_atr*0.05 and distance_between_current_ath_and_current_close<advanced_atr*0.1:
                                #     date_and_time_of_approaching_to_ath , date_of_approaching_to_ath = get_date_with_and_without_time_from_timestamp (
                                #        last_several_rows_in_np_array_slice[-1][0] )

                                # list_of_stocks_approaching_ath.append(stock_name)
                                number_of_bars_which_fulfil_suppression_to_ath = \
                                    calculate_number_of_bars_which_fulfil_suppression_criterion_to_ath (
                                        last_several_rows_in_np_array_slice ,
                                        number_of_last_row_in_np_array_row_slice )
                                # print(f"number_of_bars_which_fulfil_suppression_to_ath={number_of_bars_which_fulfil_suppression_to_ath}")


                                #check how many bars form suppression
                                if number_of_bars_which_fulfil_suppression_to_ath >= 3:


                                    try:
                                        open_of_possible_breakout_bar=False
                                        # try:
                                        #     open_of_possible_breakout_bar=\
                                        #         table_with_ohlcv_data_df_slice_numpy_array[number_of_last_row_in_np_array_row_slice][1]
                                        # except:
                                        #     pass
                                        close_of_bar_before_breakout = \
                                            table_with_ohlcv_data_df_slice_numpy_array[
                                                number_of_last_row_in_np_array_row_slice-1][4]

                                        print("close_of_bar_before_breakout")
                                        print(close_of_bar_before_breakout)

                                        if open_of_possible_breakout_bar!=False:
                                            print(f"1open_of_possible_breakout_bar not nan ={open_of_possible_breakout_bar}")
                                            if open_of_possible_breakout_bar>=close_of_bar_before_breakout:

                                                distance_between_current_ath_and_possible_breakout_bar_open = \
                                                    current_ath_in_iteration_over_numpy_array-open_of_possible_breakout_bar
                                                if distance_between_current_ath_and_possible_breakout_bar_open>0:
                                                    if distance_between_current_ath_and_possible_breakout_bar_open > advanced_atr * 0.05 and\
                                                        distance_between_current_ath_and_possible_breakout_bar_open < advanced_atr * 0.1:
                                                        date_and_time_of_approaching_to_ath , date_of_approaching_to_ath = get_date_with_and_without_time_from_timestamp (
                                                                    last_several_rows_in_np_array_slice[-1][0] )
                                                        print (f"number_of_bars_which_fulfil_suppression_to_ath={number_of_bars_which_fulfil_suppression_to_ath}" )
                                                        print (
                                                            f"for stock {stock_name} on {date_of_approaching_to_ath} approached to ath={current_ath_in_iteration_over_numpy_array}"
                                                            f" close_of_bar_before_breakout={close_of_bar_before_breakout} open_of_possible_breakout_bar={open_of_possible_breakout_bar}" )
                                                        print(f"open_of_possible_breakout_bar={open_of_possible_breakout_bar}")
                                                        print (
                                                            f"distance_between_current_ath_and_possible_breakout_bar_open={distance_between_current_ath_and_possible_breakout_bar_open}" )
                                                        # list_of_stocks_approaching_ath.append ( stock_name )
                                                        date_and_time_of_ath , date_of_ath = get_date_with_and_without_time_from_timestamp (
                                                            timestamp_of_current_ath )
                                                        date_and_time_of_current_timestamp , date_of_current_timestamp = get_date_with_and_without_time_from_timestamp (
                                                            current_timestamp )

                                                        list_of_stocks_approaching_ath.append ( stock_name )
                                                        df_with_level_atr_bpu_bsu_etc = pd.DataFrame ()
                                                        df_with_level_atr_bpu_bsu_etc.loc[0 , "ticker"] = stock_name
                                                        df_with_level_atr_bpu_bsu_etc.loc[0 , "exchange"] = exchange
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0, "model"] = "БЫСТРЫЙ_ПРОБОЙ_ATH"
                                                        
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "ath"] = current_ath_in_iteration_over_numpy_array
                                                        df_with_level_atr_bpu_bsu_etc.loc[0 , "advanced_atr"] = advanced_atr

                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "advanced_atr_over_this_period"] = \
                                                            advanced_atr_over_this_period
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "high_of_bsu"] = current_ath_in_iteration_over_numpy_array
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "volume_of_bsu"] = volume_in_current_ath
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "timestamp_of_bsu"] = timestamp_of_current_ath
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "human_date_of_bsu"] = date_of_ath
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "timestamp_of_pre_breakout_bar"] = current_timestamp
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "human_date_of_pre_breakout_bar"] = date_of_current_timestamp
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "open_of_possible_breakout_bar"] = open_of_possible_breakout_bar
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "min_volume_over_last_n_days"] = min_volume_over_last_n_days
                                                        df_with_level_atr_bpu_bsu_etc.loc[
                                                            0 , "count_min_volume_over_this_many_days"] = number_of_bars_in_suppression_to_check_for_volume_acceptance

                                                        df_with_level_atr_bpu_bsu_etc.to_sql (
                                                            table_where_ticker_which_may_have_fast_breakout_situations_from_ath_will_be ,
                                                            engine_for_db_where_ticker_which_may_have_fast_breakout_situations ,
                                                            if_exists = 'append' )
                                        else:
                                            #in this case possible breakout bar does not exist yet
                                            print ( f"2open_of_possible_breakout_bar={open_of_possible_breakout_bar}" )
                                            date_and_time_of_approaching_to_ath , date_of_approaching_to_ath = get_date_with_and_without_time_from_timestamp (
                                                last_several_rows_in_np_array_slice[-1][0] )

                                            distance_from_ath_to_close_of_pre_breakout_bar = \
                                                current_ath_in_iteration_over_numpy_array - close_of_bar_before_breakout
                                            if distance_from_ath_to_close_of_pre_breakout_bar > advanced_atr:
                                                continue


                                            print (
                                                f"number_of_bars_which_fulfil_suppression_to_ath={number_of_bars_which_fulfil_suppression_to_ath}" )
                                            print (
                                                f"for stock {stock_name} on {date_of_approaching_to_ath} approached to ath={current_ath_in_iteration_over_numpy_array}"
                                                f" close_of_bar_before_breakout={close_of_bar_before_breakout} open_of_possible_breakout_bar={open_of_possible_breakout_bar}" )






                                            list_of_stocks_approaching_ath.append ( stock_name )
                                            date_and_time_of_ath , date_of_ath = get_date_with_and_without_time_from_timestamp (
                                                timestamp_of_current_ath )
                                            date_and_time_of_current_timestamp , date_of_current_timestamp = get_date_with_and_without_time_from_timestamp (
                                                current_timestamp )

                                            # try:
                                            #     premarket_price=stock_info.get_premarket_price(stock_name)
                                            #     print("premarket_price")
                                            #     print(premarket_price)
                                            # except:
                                            #     traceback.print_exc()
                                            # try:
                                            #     next_earnings_date=\
                                            #         stock_info.get_next_earnings_date(stock_name)
                                            #     print("next_earnings_date")
                                            #     print(next_earnings_date)
                                            # except:
                                            #     traceback.print_exc()
                                            # try:
                                            #     market_status=stock_info.get_market_status()
                                            #     print("market_status")
                                            #     print(market_status)
                                            # except:
                                            #     pass







                                            list_of_stocks_approaching_ath.append ( stock_name )
                                            df_with_level_atr_bpu_bsu_etc = pd.DataFrame ()
                                            df_with_level_atr_bpu_bsu_etc.loc[0 , "ticker"] = stock_name
                                            df_with_level_atr_bpu_bsu_etc.loc[0 , "exchange"] = exchange
                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0, "model"] = "БЫСТРЫЙ_ПРОБОЙ_ATH"
                                            

                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "ath"] = current_ath_in_iteration_over_numpy_array
                                            df_with_level_atr_bpu_bsu_etc.loc[0 , "advanced_atr"] = advanced_atr

                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "advanced_atr_over_this_period"] = \
                                                advanced_atr_over_this_period
                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "high_of_bsu"] = current_ath_in_iteration_over_numpy_array
                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "volume_of_bsu"] = volume_in_current_ath
                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "timestamp_of_bsu"] = timestamp_of_current_ath
                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "human_date_of_bsu"] = date_of_ath
                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "timestamp_of_pre_breakout_bar"] = current_timestamp
                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "human_date_of_pre_breakout_bar"] = date_of_current_timestamp
                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "open_of_possible_breakout_bar"] = open_of_possible_breakout_bar
                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "min_volume_over_last_n_days"] = min_volume_over_last_n_days
                                            df_with_level_atr_bpu_bsu_etc.loc[
                                                0 , "count_min_volume_over_this_many_days"] = number_of_bars_in_suppression_to_check_for_volume_acceptance
                                            df_with_level_atr_bpu_bsu_etc.to_sql (
                                                table_where_ticker_which_may_have_fast_breakout_situations_from_ath_will_be ,
                                                engine_for_db_where_ticker_which_may_have_fast_breakout_situations ,
                                                if_exists = 'append' )
                                            print_df_to_file(df_with_level_atr_bpu_bsu_etc,
                                                             'current_rebound_breakout_and_false_breakout')



                                    except Exception as e:
                                        if e == IndexError:
                                            print ( e )
                                        else:
                                            traceback.print_exc ()
                # date_and_time_of_ath , date_of_ath = get_date_with_and_without_time_from_timestamp (
                #     last_several_rows_in_np_array_slice_only_ath[0][0] )
                # date_and_time_of_ath_2 , date_of_ath_2 = get_date_with_and_without_time_from_timestamp (
                #     last_several_rows_in_np_array_slice_only_ath[1][0] )
                # print ( f"in_stock={stock_name} ath was on {date_of_ath} and on {date_of_ath_2}" )
                # print ( ath )

##################################################################################
            # #find atl
            # if len(last_several_rows_in_np_array_slice_only_atl)>=1:
            #
            #     atl = \
            #         last_several_rows_in_np_array_slice_only_atl[0][3]
            #
            #
            #     # date_and_time_of_atl , date_of_atl = get_date_with_and_without_time_from_timestamp (
            #     #     last_several_rows_in_np_array_slice_only_atl[0][0] )
            #     # print ( f"in_stock={stock_name} atl was on {date_of_atl}" )
            #     # print ( atl )
            #
            #     current_atl_in_iteration_over_numpy_array = atl
            #     timestamp_of_current_atl = \
            #         last_several_rows_in_np_array_slice_only_atl[-1][0]
            #     volume_in_current_atl = last_several_rows_in_np_array_slice_only_atl[-1][5]
            #     column_of_timestamps=last_several_rows_in_np_array_slice[:,0]
            #     row_of_last_atl =\
            #         list ( column_of_timestamps ).index ( timestamp_of_current_atl )
            #     # print ( "row_of_last_atl" )
            #     # print ( row_of_last_atl )
            #
            #
            #     current_low = last_several_rows_in_np_array_slice[-1][3]
            #     current_high = last_several_rows_in_np_array_slice[-1][2]
            #     current_timestamp = last_several_rows_in_np_array_slice[-1][0]
            #     try:
            #         prev_high = last_several_rows_in_np_array_slice[-2][2]
            #         prev_low = last_several_rows_in_np_array_slice[-2][3]
            #         prev_prev_high = last_several_rows_in_np_array_slice[-3][2]
            #         prev_prev_low = last_several_rows_in_np_array_slice[-3][3]
            #     except:
            #         pass
            #
            #     current_close = last_several_rows_in_np_array_slice[-1][4]
            #
            #
            #
            #     if volume_in_current_atl>=750:
            #         last_n_rows_for_volume_check = last_several_rows_in_np_array_slice[
            #                                        -number_of_bars_in_suppression_to_check_for_volume_acceptance: ,
            #                                        5]
            #         min_volume_over_last_n_days = find_min_volume_over_last_n_days (
            #             last_n_rows_for_volume_check )
            #
            #         if min_volume_over_last_n_days>=750:
            #             if current_low >= current_atl_in_iteration_over_numpy_array:
            #                 if number_of_last_row_in_np_array_row_slice > row_of_last_atl + 3:
            #                     advanced_atr = calculate_atr_without_paranormal_bars_from_numpy_array (
            #                         advanced_atr_over_this_period ,
            #                         last_several_rows_in_np_array_slice ,
            #                         number_of_last_row_in_np_array_row_slice )
            #                     advanced_atr=round(advanced_atr,20)
            #
            #                     # проверить что поджатие на маленьких барах
            #                     try:
            #                         prev_high = last_several_rows_in_np_array_slice[-2][2]
            #                         prev_low = last_several_rows_in_np_array_slice[-2][3]
            #                         prev_prev_high = last_several_rows_in_np_array_slice[-3][2]
            #                         prev_prev_low = last_several_rows_in_np_array_slice[-3][3]
            #                         current_true_range = current_high - current_low
            #                         prev_true_range = prev_high - prev_low
            #                         prev_prev_true_range = prev_prev_high - prev_prev_low
            #                         if current_true_range > advanced_atr or prev_true_range > advanced_atr or prev_prev_true_range > advanced_atr:
            #                             continue
            #                     except:
            #                         pass
            #                     # print(f"advanced_atr_for_row={number_of_last_row_in_np_array_row_slice}")
            #                     # print ( advanced_atr )
            #                     # distance_between_current_atl_and_current_close = \
            #                     #     current_close - current_atl_in_iteration_over_numpy_array
            #                     # if distance_between_current_atl_and_current_close > advanced_atr * 0.05 and\
            #                     #         distance_between_current_atl_and_current_close < advanced_atr * 0.1:
            #
            #
            #
            #                     number_of_bars_which_fulfil_suppression_to_atl=\
            #                         calculate_number_of_bars_which_fulfil_suppression_criterion_to_atl(last_several_rows_in_np_array_slice,
            #                                                                        number_of_last_row_in_np_array_row_slice)
            #
            #
            #                     if number_of_bars_which_fulfil_suppression_to_atl>=3:
            #                         # print (
            #                         #     f"for stock {stock_name} on {date_of_approaching_to_atl} approached to atl={current_atl_in_iteration_over_numpy_array}" )
            #                         # list_of_stocks_approaching_atl.append ( stock_name )
            #
            #                         try:
            #                             open_of_possible_breakout_bar=False
            #                             try:
            #                                 open_of_possible_breakout_bar = \
            #                                     table_with_ohlcv_data_df_slice_numpy_array[
            #                                         number_of_last_row_in_np_array_row_slice ][1]
            #                             except:
            #                                 pass
            #                             close_of_bar_before_breakout = table_with_ohlcv_data_df_slice_numpy_array[
            #                                 number_of_last_row_in_np_array_row_slice-1][4]
            #                             if open_of_possible_breakout_bar:
            #                                 if open_of_possible_breakout_bar <= close_of_bar_before_breakout:
            #                                     # print (
            #                                     #     f"for stock {stock_name} on {date_of_approaching_to_atl} approached to atl={current_atl_in_iteration_over_numpy_array} "
            #                                     #     f"close_of_bar_before_breakout={close_of_bar_before_breakout} open_of_possible_breakout_bar={open_of_possible_breakout_bar}" )
            #                                     # list_of_stocks_approaching_atl.append ( stock_name )
            #                                     distance_between_current_atl_and_possible_breakout_bar_open = \
            #                                         open_of_possible_breakout_bar - current_atl_in_iteration_over_numpy_array
            #                                     if distance_between_current_atl_and_possible_breakout_bar_open>0:
            #                                         if distance_between_current_atl_and_possible_breakout_bar_open > advanced_atr * 0.05 and\
            #                                             distance_between_current_atl_and_possible_breakout_bar_open < advanced_atr * 0.1:
            #                                             date_and_time_of_approaching_to_atl , date_of_approaching_to_atl =\
            #                                                 get_date_with_and_without_time_from_timestamp (
            #                                                 last_several_rows_in_np_array_slice[-1][0] )
            #
            #                                             date_and_time_of_current_timestamp , date_of_current_timestamp = get_date_with_and_without_time_from_timestamp (
            #                                                 current_timestamp )
            #                                             print (f"number_of_bars_which_fulfil_suppression_to_atl={number_of_bars_which_fulfil_suppression_to_atl}" )
            #                                             print(    f"for stock {stock_name} on {date_of_approaching_to_atl} approached "
            #                                                 f"to atl={current_atl_in_iteration_over_numpy_array}"
            #                                             f" close_of_bar_before_breakout={close_of_bar_before_breakout} open_of_possible_breakout_bar={open_of_possible_breakout_bar}")
            #
            #                                             date_and_time_of_atl , date_of_atl=get_date_with_and_without_time_from_timestamp(timestamp_of_current_atl)
            #                                             list_of_stocks_approaching_atl.append ( stock_name )
            #                                             df_with_level_atr_bpu_bsu_etc = pd.DataFrame ()
            #                                             df_with_level_atr_bpu_bsu_etc.loc[0 , "ticker"] = stock_name
            #                                             df_with_level_atr_bpu_bsu_etc.loc[0 , "exchange"] = exchange
            #                                             
            #                                             df_with_level_atr_bpu_bsu_etc.loc[0 , "atl"] = current_atl_in_iteration_over_numpy_array
            #                                             df_with_level_atr_bpu_bsu_etc.loc[0 , "advanced_atr"] = advanced_atr
            #
            #                                             df_with_level_atr_bpu_bsu_etc.loc[
            #                                                 0 , "advanced_atr_over_this_period"] = \
            #                                                 advanced_atr_over_this_period
            #                                             df_with_level_atr_bpu_bsu_etc.loc[0 , "low_of_bsu"] = current_atl_in_iteration_over_numpy_array
            #                                             df_with_level_atr_bpu_bsu_etc.loc[
            #                                                 0 , "volume_of_bsu"] = volume_in_current_atl
            #                                             df_with_level_atr_bpu_bsu_etc.loc[
            #                                                 0 , "timestamp_of_bsu"] = timestamp_of_current_atl
            #                                             df_with_level_atr_bpu_bsu_etc.loc[
            #                                                 0 , "human_date_of_bsu"] = date_of_atl
            #                                             df_with_level_atr_bpu_bsu_etc.loc[
            #                                                 0 , "timestamp_of_pre_breakout_bar"] = current_timestamp
            #                                             df_with_level_atr_bpu_bsu_etc.loc[
            #                                                 0 , "human_date_of_pre_breakout_bar"] = date_of_current_timestamp
            #                                             df_with_level_atr_bpu_bsu_etc.loc[
            #                                                 0 , "open_of_possible_breakout_bar"] = open_of_possible_breakout_bar
            #                                             df_with_level_atr_bpu_bsu_etc.loc[
            #                                                 0 , "min_volume_over_last_n_days"] = min_volume_over_last_n_days
            #                                             df_with_level_atr_bpu_bsu_etc.loc[
            #                                                 0 , "count_min_volume_over_this_many_days"] = number_of_bars_in_suppression_to_check_for_volume_acceptance
            #                                             df_with_level_atr_bpu_bsu_etc.to_sql (
            #                                                 table_where_ticker_which_may_have_fast_breakout_situations_from_atl_will_be ,
            #                                                 engine_for_db_where_ticker_which_may_have_fast_breakout_situations ,
            #                                                 if_exists = 'append' )
            #                             else:
            #                                 date_and_time_of_approaching_to_atl , date_of_approaching_to_atl = \
            #                                     get_date_with_and_without_time_from_timestamp (
            #                                         last_several_rows_in_np_array_slice[-1][0] )
            #
            #                                 date_and_time_of_current_timestamp , date_of_current_timestamp = get_date_with_and_without_time_from_timestamp (
            #                                     current_timestamp )
            #                                 print (
            #                                     f"number_of_bars_which_fulfil_suppression_to_atl={number_of_bars_which_fulfil_suppression_to_atl}" )
            #                                 print (
            #                                     f"for stock {stock_name} on {date_of_approaching_to_atl} approached "
            #                                     f"to atl={current_atl_in_iteration_over_numpy_array}"
            #                                     f" close_of_bar_before_breakout={close_of_bar_before_breakout} open_of_possible_breakout_bar={open_of_possible_breakout_bar}" )
            #
            #                                 date_and_time_of_atl , date_of_atl = get_date_with_and_without_time_from_timestamp (
            #                                     timestamp_of_current_atl )
            #                                 list_of_stocks_approaching_atl.append ( stock_name )
            #                                 df_with_level_atr_bpu_bsu_etc = pd.DataFrame ()
            #                                 df_with_level_atr_bpu_bsu_etc.loc[0 , "ticker"] = stock_name
            #                                 df_with_level_atr_bpu_bsu_etc.loc[0 , "exchange"] = exchange
            #                                 
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "atl"] = current_atl_in_iteration_over_numpy_array
            #                                 df_with_level_atr_bpu_bsu_etc.loc[0 , "advanced_atr"] = advanced_atr
            #
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "advanced_atr_over_this_period"] = \
            #                                     advanced_atr_over_this_period
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "low_of_bsu"] = current_atl_in_iteration_over_numpy_array
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "volume_of_bsu"] = volume_in_current_atl
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "timestamp_of_bsu"] = timestamp_of_current_atl
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "human_date_of_bsu"] = date_of_atl
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "timestamp_of_pre_breakout_bar"] = current_timestamp
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "human_date_of_pre_breakout_bar"] = date_of_current_timestamp
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "open_of_possible_breakout_bar"] = open_of_possible_breakout_bar
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "min_volume_over_last_n_days"] = min_volume_over_last_n_days
            #                                 df_with_level_atr_bpu_bsu_etc.loc[
            #                                     0 , "count_min_volume_over_this_many_days"] = number_of_bars_in_suppression_to_check_for_volume_acceptance
            #                                 df_with_level_atr_bpu_bsu_etc.to_sql (
            #                                     table_where_ticker_which_may_have_fast_breakout_situations_from_atl_will_be ,
            #                                     engine_for_db_where_ticker_which_may_have_fast_breakout_situations ,
            #                                     if_exists = 'append' )
            #
            #
            #                         except Exception as e:
            #                             if e==IndexError:
            #                                 print(e)
            #                             else:
            #                                 traceback.print_exc()
            #

###############################################

        except:
            traceback.print_exc()






    print ( "list_of_stocks_approaching_ath" )
    print ( list_of_stocks_approaching_ath )
    print ( "list_of_stocks_approaching_atl" )
    print ( list_of_stocks_approaching_atl )




if __name__=="__main__":
    start_time=time.time ()
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_data_for_usdt_pairs_for_1d_timeframe"
    count_only_round_rebound_level=False
    db_where_ticker_which_may_have_fast_breakout_situations=\
        "levels_formed_by_highs_and_lows_for_cryptos"
    table_where_ticker_which_may_have_fast_breakout_situations_from_ath_will_be =\
        "current_fast_breakout_situations_of_ath"
    table_where_ticker_which_may_have_fast_breakout_situations_from_atl_will_be =\
        "current_fast_breakout_situations_of_atl"

    if count_only_round_rebound_level:
        db_where_ticker_which_may_have_fast_breakout_situations=\
            "round_levels_formed_by_highs_and_lows_for_cryptos"
    #0.05 means 5%
    acceptable_backlash=0.05
    atr_over_this_period=5
    advanced_atr_over_this_period=30
    number_of_bars_in_suppression_to_check_for_volume_acceptance=30
    search_for_tickers_with_breakout_situations(
                                              db_where_ohlcv_data_for_stocks_is_stored,
                                              db_where_ticker_which_may_have_fast_breakout_situations,
                                              table_where_ticker_which_may_have_fast_breakout_situations_from_ath_will_be,
                                                table_where_ticker_which_may_have_fast_breakout_situations_from_atl_will_be,
                                            advanced_atr_over_this_period,
                                            number_of_bars_in_suppression_to_check_for_volume_acceptance)

    end_time = time.time ()
    overall_time = end_time - start_time
    print ( 'overall time in minutes=' , overall_time / 60.0 )
    print ( 'overall time in hours=' , overall_time / 3600.0 )
    print ( 'overall time=' , str ( datetime.timedelta ( seconds = overall_time ) ) )
    print ( 'start_time=' , start_time )
    print ( 'end_time=' , end_time )