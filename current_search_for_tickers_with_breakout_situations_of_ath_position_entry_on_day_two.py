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
from check_if_ath_or_atl_was_not_brken_over_long_periond_of_time import check_ath_breakout
from check_if_ath_or_atl_was_not_brken_over_long_periond_of_time import check_atl_breakout

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

def get_ohlc_of_breakout_bar(truncated_high_and_low_table_with_ohlcv_data_df,
                                         row_number_of_bpu1):
    low_of_breakout_bar = False
    high_of_breakout_bar = False
    open_of_breakout_bar = False
    close_of_breakout_bar = False
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 2 == row_number_of_bpu1:
            print ( "there is no breakout_bar" )
        elif len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no breakout_bar" )
        else:
            low_of_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "low"]
            open_of_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "open"]
            close_of_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "close"]
            high_of_breakout_bar = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "high"]
            # print ( "high_of_breakout_bar" )
            # print ( high_of_breakout_bar )
    except:
        traceback.print_exc ()
    return open_of_breakout_bar , high_of_breakout_bar , low_of_breakout_bar , close_of_breakout_bar

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

def calculate_number_of_bars_which_fulfil_suppression_criterion_to_ath(last_several_rows_in_np_array_slice_but_one,
                                                      number_of_last_row_in_np_array_row_slice):
    number_of_bars_which_fulfil_suppression_criterion=0
    for number_of_bar_backward in range(1,len(last_several_rows_in_np_array_slice_but_one)):
        current_low=last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward][3]
        previous_low=last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward-1][3]
        current_close = last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward][4]
        previous_close = last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward - 1][4]
        # print ( "last_several_rows_in_np_array_slice_but_one" )
        # print(last_several_rows_in_np_array_slice_but_one)
        # print ( "current_low" )
        # print ( current_low )
        # print ( "previous_low" )
        # print ( previous_low )

        #учитываем поджатие по лоям
        if current_low<previous_low:
            break
        else:
            #учитываем еще и поджатие по закрытиям
            if current_close<previous_close:
                break
            else:
                number_of_bars_which_fulfil_suppression_criterion=\
                    number_of_bars_which_fulfil_suppression_criterion+1
    return number_of_bars_which_fulfil_suppression_criterion

def calculate_number_of_bars_which_fulfil_suppression_criterion_to_atl(last_several_rows_in_np_array_slice_but_one,
                                                      number_of_last_row_in_np_array_row_slice):
    number_of_bars_which_fulfil_suppression_criterion=0
    for number_of_bar_backward in range(1,len(last_several_rows_in_np_array_slice_but_one)):
        current_high=last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward][2]
        current_close = last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward][4]
        previous_high=last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward-1][2]
        previous_close = last_several_rows_in_np_array_slice_but_one[-number_of_bar_backward - 1][4]
        # print ( "last_several_rows_in_np_array_slice_but_one" )
        # print(last_several_rows_in_np_array_slice_but_one)
        # print ( "current_low" )
        # print ( current_low )
        # print ( "previous_low" )
        # print ( previous_low )
        #учитываем поджатие по хаям к историческому минимуму
        if current_high>previous_high:
            break
        else:
            #еще учитываем поджатие по закрытиям
            if current_close>previous_close:
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
                                                number_of_bars_in_suppression_to_check_for_volume_acceptance,
                                                factor_to_multiply_atr_by_to_check_suppression,
                                                count_min_volume_over_this_many_days
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
    list_of_stocks_which_broke_ath=[]
    list_of_stocks_which_broke_atl = []

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

            # print ("table_with_ohlcv_data_df.index")
            # print(table_with_ohlcv_data_df.index)
            # print("list(table_with_ohlcv_data_df.columns)")
            # print(list(table_with_ohlcv_data_df.columns))

            exchange = table_with_ohlcv_data_df.loc[0 , "exchange"]
            short_name = table_with_ohlcv_data_df.loc[0 , 'short_name']


            # Select last 365*2 rows (last two years) of data
            last_two_years_of_data = table_with_ohlcv_data_df.tail(365 * 2)

            # Round ohlc and adjclose to 6 decimal places
            last_two_years_of_data = last_two_years_of_data.round(
                {'open': 6, 'high': 6, 'low': 6, 'close': 6, 'adjclose': 6})

            # Find row number of last row in last_two_years_of_data
            breakout_bar_row_number = last_two_years_of_data.index[-2]

            # Find Timestamp, open, high, low, close, volume of breakout_bar
            timestamp_of_breakout_bar = last_two_years_of_data.loc[
                breakout_bar_row_number, 'Timestamp']
            open_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'open']
            high_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'high']
            low_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'low']
            close_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'close']
            volume_of_breakout_bar = last_two_years_of_data.loc[breakout_bar_row_number, 'volume']

            if pd.isna(open_of_breakout_bar) or pd.isna(close_of_breakout_bar) or \
                    pd.isna(low_of_breakout_bar) or pd.isna(high_of_breakout_bar):
                continue

            # Select all rows in last_two_years_of_data excluding the last 2 rows
            last_two_years_of_data_but_two_last_days = last_two_years_of_data.iloc[:-2]

            # Find row number of last row in last_two_years_of_data_but_two_last_days
            pre_breakout_bar_row_number = last_two_years_of_data_but_two_last_days.index[-1]

            # Make a dataframe out of last row of last_two_years_of_data_but_two_last_days
            pre_breakout_bar_df = last_two_years_of_data_but_two_last_days.iloc[[-1]]

            # Находим номер последнего бара в датафрэйме (следующий день после пробоя)
            next_day_bar_after_break_out_bar_row_number = last_two_years_of_data.index[-1]

            # Делаем слайс изначального датафрэйма, чтобы получить дф последнего бара в датафрэйме
            # (следующий день после пробоя)
            next_day_bar_after_break_out_bar_df = last_two_years_of_data.iloc[[-1]]

            # Find Timestamp, open, high, low, close, volume of pre_breakout_bar
            timestamp_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'Timestamp']
            open_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'open']
            high_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'high']
            low_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'low']
            close_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'close']
            volume_of_pre_breakout_bar = pre_breakout_bar_df.loc[pre_breakout_bar_row_number, 'volume']

            # Find Timestamp, open, high, low, close, volume of bar after breakout bar
            timestamp_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'Timestamp']
            open_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'open']
            high_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'high']
            low_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'low']
            close_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'close']
            volume_of_next_day_bar_after_break_out_bar = next_day_bar_after_break_out_bar_df.loc[next_day_bar_after_break_out_bar_row_number, 'volume']

            # print("table_with_ohlcv_data_df")
            # print(table_with_ohlcv_data_df.tail(10).to_string())


            # Print Timestamp, open, high, low, close, volume of breakout_bar
            # print(f"Timestamp of candidate breakout bar: {timestamp_of_breakout_bar}")
            # print(f"Open of candidate breakout bar: {open_of_breakout_bar}")
            # print(f"High of candidate breakout bar: {high_of_breakout_bar}")
            # print(f"Low of candidate breakout bar: {low_of_breakout_bar}")
            # print(f"Close of candidate breakout bar: {close_of_breakout_bar}")
            # print(f"Volume of candidate breakout bar: {volume_of_breakout_bar}")

            # Print Timestamp, open, high, low, close, volume of pre_breakout_bar
            # print(f"Timestamp of pre-breakout bar: {timestamp_of_pre_breakout_bar}")
            # print(f"Open of pre-breakout bar: {open_of_pre_breakout_bar}")
            # print(f"High of pre-breakout bar: {high_of_pre_breakout_bar}")
            # print(f"Low of pre-breakout bar: {low_of_pre_breakout_bar}")
            # print(f"Close of pre-breakout bar: {close_of_pre_breakout_bar}")
            # print(f"Volume of pre-breakout bar: {volume_of_pre_breakout_bar}")

            if last_two_years_of_data.tail(30)['volume'].min() < 750:
                continue

            if close_of_breakout_bar < 1 and last_two_years_of_data.tail(30)['volume'].min() < 1000:
                continue


            # find all time high in last_two_years_of_data_but_one_last_day
            all_time_high = last_two_years_of_data_but_two_last_days['high'].max()
            print(f"all_time_high: {all_time_high}")

            all_time_high_row_numbers =\
                last_two_years_of_data_but_two_last_days[last_two_years_of_data_but_two_last_days['high'] == all_time_high].index

            last_all_time_high_row_number = all_time_high_row_numbers[-1]

            # Find timestamps of all_time_high rows and create list out of them
            all_time_high_timestamps = last_two_years_of_data_but_two_last_days.loc[all_time_high_row_numbers][
                'Timestamp'].tolist()

            timestamp_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'Timestamp']
            open_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'open']
            high_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'high']
            low_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'low']
            close_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'close']
            volume_of_last_all_time_high = last_two_years_of_data_but_two_last_days.loc[
                last_all_time_high_row_number, 'volume']
            print(f"1found_stock={stock_name}")


            # проверяем, ближайший исторический максимум был не ближе, чем 3 дня до пробоя
            if breakout_bar_row_number - last_all_time_high_row_number < 3:
                continue

            print(f"2found_stock={stock_name}")

            if last_two_years_of_data_but_two_last_days.loc[
               last_all_time_high_row_number + 1:,"high"].max() > all_time_high:
                continue

            print(f"3found_stock={stock_name}")

            if high_of_breakout_bar <= all_time_high:
                continue

            print(f"4found_stock={stock_name}")

            if open_of_breakout_bar >= all_time_high:
                continue

            print(f"5found_stock={stock_name}")

            if close_of_breakout_bar <= all_time_high:
                continue

            print(f"6found_stock={stock_name}")

            #cмотрим поджатие
            last_n_lows = list(last_two_years_of_data['low'].tail(3))
            suppression_flag = True
            for i in range(len(last_n_lows) - 1):
                if last_n_lows[i + 1] < last_n_lows[i]:
                    suppression_flag = False
                    break
            if suppression_flag==False:
                continue
            print(f"last_n_lows_for_{stock_name}")
            print(last_n_lows)

            print(f"7found_stock={stock_name}")

            last_two_years_of_data_but_two_last_days_array = last_two_years_of_data_but_two_last_days.to_numpy()

            advanced_atr=\
                calculate_atr_without_paranormal_bars_from_numpy_array(atr_over_this_period,
                                                                   last_two_years_of_data_but_two_last_days_array,
                                                                   pre_breakout_bar_row_number)


            if open_of_next_day_bar_after_break_out_bar<close_of_breakout_bar or\
                close_of_next_day_bar_after_break_out_bar<close_of_breakout_bar:
                continue



            # print(f"open_of_breakout_bar={open_of_breakout_bar}")
            # print(
            #     f"close_of_breakout_bar={close_of_breakout_bar}")

            distance_between_current_ath_and_breakout_bar_open = \
                all_time_high - open_of_breakout_bar
            distance_between_current_ath_and_breakout_bar_close = \
                close_of_breakout_bar - all_time_high
            if distance_between_current_ath_and_breakout_bar_open == 0:
                continue
            if not (distance_between_current_ath_and_breakout_bar_open > advanced_atr * 0.05) and \
                    (distance_between_current_ath_and_breakout_bar_close > advanced_atr * 0.05):
                continue





            date_and_time_of_last_ath, date_of_last_ath = get_date_with_and_without_time_from_timestamp(
                all_time_high_timestamps[-1])
            date_and_time_of_pre_breakout_bar, date_of_pre_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_pre_breakout_bar)
            date_and_time_of_breakout_bar, date_of_breakout_bar = get_date_with_and_without_time_from_timestamp(
                timestamp_of_breakout_bar)
            date_and_time_of_next_day_bar_after_break_out_bar, date_of_next_day_bar_after_break_out_bar =\
                get_date_with_and_without_time_from_timestamp(
                timestamp_of_next_day_bar_after_break_out_bar)

            calculated_stop_loss = all_time_high - (advanced_atr * 0.05)
            buy_order = all_time_high + (advanced_atr * 0.5)
            take_profit_when_sl_is_calculated_3_to_1 = (buy_order - calculated_stop_loss) * 3 + buy_order
            take_profit_when_sl_is_calculated_4_to_1 = (buy_order - calculated_stop_loss) * 4 + buy_order

            # round decimals for ease of looking at
            buy_order = round(buy_order, 6)
            calculated_stop_loss = round(calculated_stop_loss, 6)
            take_profit_when_sl_is_calculated_3_to_1 = round(take_profit_when_sl_is_calculated_3_to_1, 6)
            take_profit_when_sl_is_calculated_4_to_1 = round(take_profit_when_sl_is_calculated_4_to_1, 6)

            # plot all lines with advanced atr (stop loss is technical)
            technical_stop_loss = low_of_breakout_bar - (0.05 * advanced_atr)
            distance_between_technical_stop_loss_and_buy_order = buy_order - technical_stop_loss
            take_profit_when_sl_is_technical_3_to_1 = (buy_order - technical_stop_loss) * 3 + buy_order
            take_profit_when_sl_is_technical_4_to_1 = (buy_order - technical_stop_loss) * 4 + buy_order
            distance_between_technical_stop_loss_and_buy_order_in_atr = \
                distance_between_technical_stop_loss_and_buy_order / advanced_atr
            # round technical stop loss and take profit for ease of looking at
            technical_stop_loss = round(technical_stop_loss, 6)
            take_profit_when_sl_is_technical_3_to_1 = \
                round(take_profit_when_sl_is_technical_3_to_1, 6)
            take_profit_when_sl_is_technical_4_to_1 = \
                round(take_profit_when_sl_is_technical_4_to_1, 6)
            distance_between_technical_stop_loss_and_buy_order_in_atr = \
                round(distance_between_technical_stop_loss_and_buy_order_in_atr, 6)

            list_of_stocks_which_broke_ath.append(stock_name)
            print("list_of_stocks_which_broke_ath")
            print(list_of_stocks_which_broke_ath)

            df_with_level_atr_bpu_bsu_etc = pd.DataFrame()
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "ticker"] = stock_name
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "exchange"] = exchange
            
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "model"] = "ПРОБОЙ_ATH_с_подтверждением_вход_на_2й_день"
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "ath"] = all_time_high
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "advanced_atr"] = advanced_atr

            df_with_level_atr_bpu_bsu_etc.loc[
                0, "advanced_atr_over_this_period"] = \
                advanced_atr_over_this_period
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "high_of_bsu"] = all_time_high
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "volume_of_bsu"] = volume_of_last_all_time_high
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "timestamp_of_bsu"] = timestamp_of_last_all_time_high
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "human_date_of_bsu"] = date_of_last_ath

            df_with_level_atr_bpu_bsu_etc.loc[
                0, "timestamp_of_pre_breakout_bar"] = timestamp_of_pre_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "human_date_of_pre_breakout_bar"] = date_of_pre_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "open_of_pre_breakout_bar"] = open_of_pre_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "high_of_pre_breakout_bar"] = high_of_pre_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "low_of_pre_breakout_bar"] = low_of_pre_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "close_of_pre_breakout_bar"] = close_of_pre_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "volume_of_pre_breakout_bar"] = volume_of_pre_breakout_bar

            df_with_level_atr_bpu_bsu_etc.loc[
                0, "timestamp_of_breakout_bar"] = timestamp_of_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "human_date_of_breakout_bar"] = date_of_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "open_of_breakout_bar"] = open_of_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "high_of_breakout_bar"] = high_of_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "low_of_breakout_bar"] = low_of_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "close_of_breakout_bar"] = close_of_breakout_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "volume_of_breakout_bar"] = volume_of_breakout_bar

            df_with_level_atr_bpu_bsu_etc.loc[
                0, "timestamp_of_next_day_bar_after_break_out_bar"] = timestamp_of_next_day_bar_after_break_out_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "human_date_of_next_day_bar_after_break_out_bar"] = date_of_next_day_bar_after_break_out_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "open_of_next_day_bar_after_break_out_bar"] = open_of_next_day_bar_after_break_out_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "high_of_next_day_bar_after_break_out_bar"] = high_of_next_day_bar_after_break_out_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "low_of_next_day_bar_after_break_out_bar"] = low_of_next_day_bar_after_break_out_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "close_of_next_day_bar_after_break_out_bar"] = close_of_next_day_bar_after_break_out_bar
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "volume_of_next_day_bar_after_break_out_bar"] = volume_of_next_day_bar_after_break_out_bar


            df_with_level_atr_bpu_bsu_etc.loc[
                0, "min_volume_over_last_n_days"] =  last_two_years_of_data['volume'].tail(count_min_volume_over_this_many_days).min()
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "count_min_volume_over_this_many_days"] = count_min_volume_over_this_many_days

            df_with_level_atr_bpu_bsu_etc.loc[
                0, "buy_order"] = buy_order
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "calculated_stop_loss"] = calculated_stop_loss
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "take_profit_when_sl_is_calculated_3_to_1"] = take_profit_when_sl_is_calculated_3_to_1
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "take_profit_when_sl_is_calculated_4_to_1"] = take_profit_when_sl_is_calculated_4_to_1

            distance_between_calculated_stop_loss_and_buy_order = buy_order - calculated_stop_loss
            distance_between_calculated_stop_loss_and_buy_order_in_atr = \
                distance_between_calculated_stop_loss_and_buy_order / advanced_atr
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "distance_between_calculated_stop_loss_and_buy_order_in_atr"] = \
                distance_between_calculated_stop_loss_and_buy_order_in_atr

            df_with_level_atr_bpu_bsu_etc.loc[
                0, "technical_stop_loss"] = technical_stop_loss
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "take_profit_when_sl_is_technical_3_to_1"] = take_profit_when_sl_is_technical_3_to_1
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "take_profit_when_sl_is_technical_4_to_1"] = take_profit_when_sl_is_technical_4_to_1
            df_with_level_atr_bpu_bsu_etc.loc[
                0, "distance_between_technical_sl_and_buy_order_in_atr"] = distance_between_technical_stop_loss_and_buy_order_in_atr


            df_with_level_atr_bpu_bsu_etc.to_sql(
                table_where_ticker_which_may_have_fast_breakout_situations_from_ath_will_be,
                engine_for_db_where_ticker_which_may_have_fast_breakout_situations,
                if_exists='append')
            print_df_to_file(df_with_level_atr_bpu_bsu_etc,
                             'current_rebound_breakout_and_false_breakout')

        except:
            traceback.print_exc()

    string_for_output = f"Список инструментов, которые сформировали модель ПРОБОЙ исторического максимума (с подтверждением)." \
                        f"Вход через 1 день после пробоя:\n" \
                        f"{list_of_stocks_which_broke_ath}\n\n"
    # Use the function to create a text file with the text
    # in the subdirectory "current_rebound_breakout_and_false_breakout"
    create_text_file_and_writ_text_to_it(string_for_output,
                                         'current_rebound_breakout_and_false_breakout')
    print ( "list_of_stocks_which_broke_ath" )
    print ( list_of_stocks_which_broke_ath )
    print ( "list_of_stocks_which_broke_atl" )
    print ( list_of_stocks_which_broke_atl )




if __name__=="__main__":
    start_time=time.time ()
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_data_for_usdt_pairs_for_1d_timeframe"
    count_only_round_rebound_level=False
    db_where_ticker_which_may_have_fast_breakout_situations=\
        "levels_formed_by_highs_and_lows_for_cryptos"
    table_where_ticker_which_may_have_fast_breakout_situations_from_ath_will_be =\
        "current_breakout_situations_of_ath_position_entry_on_day_two"
    table_where_ticker_which_may_have_fast_breakout_situations_from_atl_will_be =\
        "current_breakout_situations_of_atl_position_entry_on_day_two"

    if count_only_round_rebound_level:
        db_where_ticker_which_may_have_fast_breakout_situations=\
            "round_levels_formed_by_highs_and_lows_for_cryptos"
    #0.05 means 5%
    
    atr_over_this_period=5
    advanced_atr_over_this_period=30
    number_of_bars_in_suppression_to_check_for_volume_acceptance=14
    factor_to_multiply_atr_by_to_check_suppression=1
    count_min_volume_over_this_many_days=30
    search_for_tickers_with_breakout_situations(
                                              db_where_ohlcv_data_for_stocks_is_stored,
                                              db_where_ticker_which_may_have_fast_breakout_situations,
                                              table_where_ticker_which_may_have_fast_breakout_situations_from_ath_will_be,
                                                table_where_ticker_which_may_have_fast_breakout_situations_from_atl_will_be,
                                            advanced_atr_over_this_period,
                                            number_of_bars_in_suppression_to_check_for_volume_acceptance,
                                            factor_to_multiply_atr_by_to_check_suppression,count_min_volume_over_this_many_days)

    end_time = time.time ()
    overall_time = end_time - start_time
    print ( 'overall time in minutes=' , overall_time / 60.0 )
    print ( 'overall time in hours=' , overall_time / 3600.0 )
    print ( 'overall time=' , str ( datetime.timedelta ( seconds = overall_time ) ) )
    print ( 'start_time=' , start_time )
    print ( 'end_time=' , end_time )