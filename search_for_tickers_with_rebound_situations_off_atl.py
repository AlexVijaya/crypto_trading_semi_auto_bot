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

def get_last_asset_type_url_maker_and_taker_fee_from_ohlcv_table(ohlcv_data_df):
    asset_type = ohlcv_data_df["asset_type"].iat[-1]
    maker_fee = ohlcv_data_df["maker_fee"].iat[-1]
    taker_fee = ohlcv_data_df["taker_fee"].iat[-1]
    url_of_trading_pair = ohlcv_data_df["url_of_trading_pair"].iat[-1]
    return asset_type,maker_fee,taker_fee,url_of_trading_pair
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

def drop_table(table_name,engine):
    engine.execute (
        f"DROP TABLE IF EXISTS {table_name};" )

def get_last_close_price_of_asset(ohlcv_table_df):
    last_close_price=ohlcv_table_df["close"].iat[-1]
    return last_close_price

def get_date_with_and_without_time_from_timestamp(timestamp):

    try:
        open_time = \
            dt.datetime.fromtimestamp ( timestamp  )
        # last_timestamp = historical_data_for_stock_ticker_df["Timestamp"].iloc[-1]
        # last_date_with_time = historical_data_for_stock_ticker_df["open_time"].iloc[-1]
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
#     high_of_bpu2=np.NaN
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
    low_of_bpu2=np.NaN
    high_of_bpu2 = np.NaN
    open_of_bpu2 = np.NaN
    close_of_bpu2 = np.NaN
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

def get_ohlc_of_tvx(truncated_high_and_low_table_with_ohlcv_data_df,
                                         row_number_of_bpu1):
    low_of_tvx = np.NaN
    high_of_tvx = np.NaN
    open_of_tvx = np.NaN
    close_of_tvx = np.NaN
    try:
        if len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 2 == row_number_of_bpu1:
            print ( "there is no tvx" )
        elif len ( truncated_high_and_low_table_with_ohlcv_data_df ) - 1 == row_number_of_bpu1:
            print ( "there is no tvx" )
        else:
            low_of_tvx = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "low"]
            open_of_tvx = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "open"]
            close_of_tvx = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "close"]
            high_of_tvx = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 + 2 , "high"]
            # print ( "high_of_tvx" )
            # print ( high_of_tvx )
    except:
        traceback.print_exc ()
    return open_of_tvx , high_of_tvx , low_of_tvx , close_of_tvx

def get_timestamp_of_bpu2(truncated_high_and_low_table_with_ohlcv_data_df,row_number_of_bpu1):
    # get high of bpu2
    timestamp_bpu2=np.NaN
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
    volume_bpu2=np.NaN
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
    print ( "atr" )
    print ( atr )
    return atr

def calculate_advanced_atr(atr_over_this_period,
                  truncated_high_and_low_table_with_ohlcv_data_df,
                  row_number_of_bpu1):
    # calcualte atr over 5 days before bpu2. bpu2 is not included

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
    print ( "list_of_true_ranges" )
    print ( list_of_true_ranges )
    print ( "percentile_20" )
    print ( percentile_20 )
    print ( "percentile_80" )
    print ( percentile_80 )
    list_of_non_rejected_true_ranges=[]
    for true_range_in_list in list_of_true_ranges:
        if true_range_in_list>=percentile_20 and true_range_in_list<=percentile_80:
            list_of_non_rejected_true_ranges.append(true_range_in_list)
    atr=mean(list_of_non_rejected_true_ranges)

    return atr


def trunc(num, digits):
    if num!=np.NaN:
        try:
            l = str(float(num)).split('.')
            digits = min(len(l[1]), digits)
            return float(l[0] + '.' + l[1][:digits])
        except:
            traceback.print_exc()
    else:
        return np.NaN
def check_if_bsu_bpu1_bpu2_do_not_open_into_atl_level (
        acceptable_backlash,atr,open_of_bsu , open_of_bpu1 , open_of_bpu2 ,
        high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
        low_of_bsu , low_of_bpu1 , low_of_bpu2 ):
    three_bars_do_not_open_into_level=np.NaN

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
    three_bars_do_not_close_into_level = np.NaN

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
    three_bars_do_not_open_into_level = np.NaN

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
    three_bars_do_not_close_into_level = np.NaN

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


def search_for_tickers_with_rebound_situations(db_where_ohlcv_data_for_stocks_is_stored,
                                          db_where_levels_formed_by_rebound_level_will_be,
                                               table_where_ticker_which_had_rebound_situations_from_ath_will_be ,
                                               table_where_ticker_which_had_rebound_situations_from_atl_will_be,
                                               acceptable_backlash ,
                                               atr_over_this_period,advanced_atr_over_this_period,
                                                count_min_volume_over_this_many_days
                                               ):


    engine_for_ohlcv_data_for_stocks , \
    connection_to_ohlcv_data_for_stocks = \
        connect_to_postres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored )

    engine_for_db_where_levels_formed_by_rebound_level_will_be , \
    connection_to_db_where_levels_formed_by_rebound_level_will_be = \
        connect_to_postres_db_without_deleting_it_first ( db_where_levels_formed_by_rebound_level_will_be )

    # drop_table ( table_where_ticker_which_had_rebound_situations_from_ath_will_be ,
    #              engine_for_db_where_levels_formed_by_rebound_level_will_be )
    drop_table ( table_where_ticker_which_had_rebound_situations_from_atl_will_be ,
                 engine_for_db_where_levels_formed_by_rebound_level_will_be )

    list_of_tables_in_ohlcv_db=\
        get_list_of_tables_in_db ( engine_for_ohlcv_data_for_stocks )
    counter=0
    list_of_tickers_where_ath_is_also_limit_level=[]
    list_of_tickers_where_atl_is_also_limit_level = []

    for stock_name in list_of_tables_in_ohlcv_db:
        # if stock_name!="FLME":
        #     continue
        try:

            counter=counter+1
            print ( f'{stock_name} is'
                    f' number {counter} out of {len ( list_of_tables_in_ohlcv_db )}\n' )



            table_with_ohlcv_data_df = \
                pd.read_sql_query ( f'''select * from "{stock_name}"''' ,
                                    engine_for_ohlcv_data_for_stocks )

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
                table_with_ohlcv_data_df["high"].apply(round , args = (20 ,) )
            table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round , args = (20 ,) )
            table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply(round , args = (20 ,) )
            table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply(round , args = (20 ,) )

            initial_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy ()
            truncated_high_and_low_table_with_ohlcv_data_df = table_with_ohlcv_data_df.copy ()

            truncated_high_and_low_table_with_ohlcv_data_df["high"]=\
                table_with_ohlcv_data_df["high"].apply(round,args = (20,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply(round , args = (20 ,) )
            truncated_high_and_low_table_with_ohlcv_data_df["open"] = \
                table_with_ohlcv_data_df["open"].apply(round , args = (20 ,) )
            truncated_high_and_low_table_with_ohlcv_data_df["close"] = \
                table_with_ohlcv_data_df["close"].apply(round , args = (20 ,) )

            print('table_with_ohlcv_data_df.loc[0,"close"]')
            print ( table_with_ohlcv_data_df.loc[0 , "close"] )

            # round high and low to two decimal number

            truncated_high_and_low_table_with_ohlcv_data_df["high"]=\
                table_with_ohlcv_data_df["high"].apply(round,args = (20,))
            truncated_high_and_low_table_with_ohlcv_data_df["low"] = \
                table_with_ohlcv_data_df["low"].apply ( round , args = (20,) )

            # print ( "after_table_with_ohlcv_data_df" )
            # print ( table_with_ohlcv_data_df )
            #####################

            number_of_all_rows_in_df=len(truncated_high_and_low_table_with_ohlcv_data_df)
            list_of_periods=list(range(20,number_of_all_rows_in_df,20))
            list_of_periods.append(len(truncated_high_and_low_table_with_ohlcv_data_df))
            # print ( "number_of_all_rows_in_df" )
            # print ( number_of_all_rows_in_df )
            # print ( "list_of_periods" )
            # print ( list_of_periods )

            for last_row_in_slice in list_of_periods:
                # print ( "last_row_in_slice" )
                # print ( last_row_in_slice )
                truncated_high_and_low_table_with_ohlcv_data_df_slice=\
                    truncated_high_and_low_table_with_ohlcv_data_df.head(last_row_in_slice)
                # print ( "initial_table_with_ohlcv_data_df" )
                # print ( initial_table_with_ohlcv_data_df.head ( 10 ).to_string () )

                # print ( "initial_table_with_ohlcv_data_df" )
                # print ( initial_table_with_ohlcv_data_df.head ( 10 ).to_string () )

                table_with_ohlcv_data_df_slice=initial_table_with_ohlcv_data_df.head(last_row_in_slice).copy()

                # print ( "initial_table_with_ohlcv_data_df" )
                # print ( initial_table_with_ohlcv_data_df.head(10).to_string() )
                #

                # print ( "truncated_high_and_low_table_with_ohlcv_data_df_slice" )
                # print ( truncated_high_and_low_table_with_ohlcv_data_df_slice )

                all_time_high=truncated_high_and_low_table_with_ohlcv_data_df_slice["high"].max()
                all_time_low = truncated_high_and_low_table_with_ohlcv_data_df_slice["low"].min ()

                # print("all_time_high")
                # print(all_time_high)
                # print("all_time_low")
                # print(all_time_low)
                ohlcv_df_with_low_equal_to_atl_slice=\
                    truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[truncated_high_and_low_table_with_ohlcv_data_df_slice["low"]==all_time_low]
                ohlcv_df_with_high_equal_to_ath_slice =\
                    truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[truncated_high_and_low_table_with_ohlcv_data_df_slice["high"] == all_time_high]

######################################################

                #find rebound from atl
                if len(ohlcv_df_with_low_equal_to_atl_slice)>1:
                    # list_of_tickers_where_atl_is_also_limit_level.append(stock_name)
                    # print ( "ohlcv_df_with_low_equal_to_atl_slice" )
                    # print ( ohlcv_df_with_low_equal_to_atl_slice )
                    print ( "list_of_tickers_where_atl_is_also_limit_level" )
                    print ( list_of_tickers_where_atl_is_also_limit_level )
                    ohlcv_df_with_low_equal_to_atl_slice=\
                        ohlcv_df_with_low_equal_to_atl_slice.rename ( columns = {"index": "index_column"}  )
                    # print ( "ohlcv_df_with_high_equal_to_ath_slice" )
                    # print ( ohlcv_df_with_high_equal_to_ath_slice.to_string () )
                    row_number_of_bpu1 = ohlcv_df_with_low_equal_to_atl_slice["index_column"].iat[1]
                    row_number_of_bsu = ohlcv_df_with_low_equal_to_atl_slice["index_column"].iat[0]
                    # print ( "row_number_of_bpu1" )
                    # print ( row_number_of_bpu1 )

                    #get ohlcv of bsu, bpu1,bpu2, tvx from truncated high and low df
                    # get ohlcv of bpu2 from NOT truncated high and low df
                    open_of_bpu2=high_of_bpu2=low_of_bpu2=close_of_bpu2=np.nan
                    open_of_tvx=high_of_tvx=low_of_tvx=close_of_tvx=np.nan
                    try:
                        open_of_bpu2,high_of_bpu2,low_of_bpu2,close_of_bpu2 = \
                            get_ohlc_of_bpu2 ( truncated_high_and_low_table_with_ohlcv_data_df ,
                                               row_number_of_bpu1 )
                    except:
                        pass

                    # get ohlcv of tvx from NOT truncated high and low df
                    try:
                        open_of_tvx , high_of_tvx , low_of_tvx , close_of_tvx = \
                            get_ohlc_of_tvx ( truncated_high_and_low_table_with_ohlcv_data_df ,
                                              row_number_of_bpu1 )
                    except:
                        pass

                    # if open_of_tvx==np.NaN:
                    #
                    #     print ( "row_number_of_bpu1" )
                    #     print ( row_number_of_bpu1 )
                    #     print ( "table_with_ohlcv_data_df" )
                    #     print ( table_with_ohlcv_data_df.iloc[row_number_of_bpu1-5:row_number_of_bpu1+5,:].to_string () )
                    #     #time.sleep(10000000)

                    #get ohlc of bsu, bpu1 from truncated high and low df
                    low_of_bsu=truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "low"]
                    low_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "low"]
                    open_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "open"]
                    open_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "open"]
                    close_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "close"]
                    close_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "close"]
                    high_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "high"]
                    high_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "high"]

                    # get ohlcv of bsu, bpu1,bpu2, tvx
                    # get ohlcv of bpu2
                    true_open_of_bpu2 , true_high_of_bpu2 , true_low_of_bpu2 , true_close_of_bpu2 = \
                        get_ohlc_of_bpu2 ( table_with_ohlcv_data_df ,
                                           row_number_of_bpu1 )

                    # get ohlcv of tvx
                    true_open_of_tvx , true_high_of_tvx , true_low_of_tvx , true_close_of_tvx = \
                        get_ohlc_of_tvx ( table_with_ohlcv_data_df ,
                                          row_number_of_bpu1 )
                    # get ohlc of bsu, bpu1
                    true_low_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "low"]
                    true_low_of_bpu1 = table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "low"]
                    true_open_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "open"]
                    true_open_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                        row_number_of_bpu1 , "open"]
                    true_close_of_bsu = table_with_ohlcv_data_df_slice.loc[
                        row_number_of_bsu , "close"]
                    true_close_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                        row_number_of_bpu1 , "close"]
                    true_high_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "high"]
                    true_high_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                        row_number_of_bpu1 , "high"]


                    volume_of_bsu = table_with_ohlcv_data_df.loc[row_number_of_bsu , "volume"]
                    volume_of_bpu1 = table_with_ohlcv_data_df.loc[row_number_of_bpu1 , "volume"]
                    volume_of_bpu2=get_volume_of_bpu2 ( table_with_ohlcv_data_df , row_number_of_bpu1 )

                    atr = calculate_atr ( atr_over_this_period ,
                                          table_with_ohlcv_data_df ,
                                          row_number_of_bpu1 )
                    advanced_atr=calculate_advanced_atr ( advanced_atr_over_this_period ,
                                             table_with_ohlcv_data_df ,
                                             row_number_of_bpu1 )

                    atr = round ( atr ,20)
                    advanced_atr = round ( advanced_atr ,20)

                    # print("true_low_of_bsu")
                    # print(true_low_of_bsu)
                    # print ( "true_low_of_bpu1" )
                    # print ( true_low_of_bpu1 )
                    # print ( "true_low_of_bpu2" )
                    # print ( true_low_of_bpu2 )

                    # if all_time_low<=1:
                    #     if volume_of_bpu1 < 1000000 or volume_of_bsu < 1000000 or volume_of_bpu2 < 1000000:
                    #         continue
                    #
                    # if volume_of_bpu1<750000 or volume_of_bsu<750000 or volume_of_bpu2<750000:
                    #     continue

                    if open_of_tvx<=close_of_bpu2:
                        continue

                    if true_low_of_tvx > all_time_low + 0.5 * atr:
                        continue


                    timestamp_of_bpu2=get_timestamp_of_bpu2 ( truncated_high_and_low_table_with_ohlcv_data_df , row_number_of_bpu1 )
                    timestamp_of_bpu1=truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 , "Timestamp"]
                    timestamp_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bsu , "Timestamp"]

                    timestamp_of_bpu2_with_time,timestamp_of_bpu2_without_time=get_date_with_and_without_time_from_timestamp ( timestamp_of_bpu2 )
                    timestamp_of_bpu1_with_time,timestamp_of_bpu1_without_time = get_date_with_and_without_time_from_timestamp ( timestamp_of_bpu1 )
                    timestamp_of_bsu_with_time,timestamp_of_bsu_without_time = get_date_with_and_without_time_from_timestamp ( timestamp_of_bsu )

                    # print ( "low_of_bpu2" )
                    # print ( low_of_bpu2 )

                    # calcualte atr over 5 days before bpu2. bpu2 is not included
                    # atr_over_this_period = 5



                    asset_not_open_into_level_bool = \
                        check_if_bsu_bpu1_bpu2_do_not_open_into_atl_level ( acceptable_backlash,atr,open_of_bsu , open_of_bpu1 , open_of_bpu2 ,
                                                                        high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
                                                                        low_of_bsu , low_of_bpu1 , low_of_bpu2 )
                    asset_not_close_into_level_bool = \
                        check_if_bsu_bpu1_bpu2_do_not_close_into_atl_level ( acceptable_backlash,atr,close_of_bsu , close_of_bpu1 , close_of_bpu2 ,
                                                                        high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
                                                                        low_of_bsu , low_of_bpu1 , low_of_bpu2 )

                    if not asset_not_open_into_level_bool and not asset_not_close_into_level_bool:
                        continue


                    if atr>0:
                        backlash = abs ( true_low_of_bpu2 - all_time_low )
                        if (backlash <= atr * acceptable_backlash) and ( low_of_bpu2 - all_time_low )>=0:
                            calculated_stop_loss = all_time_low - (advanced_atr * 0.05)
                            calculated_backlash_from_advanced_atr = advanced_atr * 0.05
                            buy_order = all_time_low + (advanced_atr * 0.5)
                            take_profit_3_to_1 = buy_order + (advanced_atr * 0.5) * 3
                            take_profit_4_to_1 = buy_order + (advanced_atr * 0.5) * 4

                            distance_between_calculated_stop_loss_and_buy_order = buy_order - calculated_stop_loss
                            distance_between_calculated_stop_loss_and_buy_order_in_atr=\
                                distance_between_calculated_stop_loss_and_buy_order/advanced_atr

                            calculated_stop_loss = round(calculated_stop_loss, 20)
                            calculated_backlash_from_advanced_atr = round(calculated_backlash_from_advanced_atr, 20)
                            buy_order = round(buy_order, 20)
                            take_profit_3_to_1 = round(take_profit_3_to_1, 20)
                            take_profit_4_to_1 = round(take_profit_4_to_1, 20)
                            # distance_between_calculated_stop_loss_and_buy_order_in_atr =\
                            #     round(distance_between_calculated_stop_loss_and_buy_order_in_atr, 20)

                            advanced_atr = round(advanced_atr, 20)
                            low_of_bsu = round(low_of_bsu, 20)
                            low_of_bpu1 = round(low_of_bpu1, 20)
                            low_of_bpu2 = round(low_of_bpu2, 20)
                            close_of_bpu2 = round(close_of_bpu2, 20)

                            list_of_tickers_where_atl_is_also_limit_level.append ( stock_name )
                            df_with_level_atr_bpu_bsu_etc = pd.DataFrame ()
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "ticker"] = stock_name
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "exchange"] = exchange
                            df_with_level_atr_bpu_bsu_etc.loc[0, "model"] = "ОТБОЙ_от_ATL"
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "short_name"] = short_name
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "atl"] = all_time_low
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "atr"] = atr
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "advanced_atr"] = advanced_atr
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "atr_over_this_period"] = atr_over_this_period
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "advanced_atr_over_this_period"] =\
                                advanced_atr_over_this_period
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "backlash"] = backlash
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "acceptable_backlash"] = acceptable_backlash
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "low_of_bsu"] = low_of_bsu
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "low_of_bpu1"] = low_of_bpu1
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "low_of_bpu2"] = low_of_bpu2

                            df_with_level_atr_bpu_bsu_etc.loc[0 , "true_low_of_bsu"] = true_low_of_bsu
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "true_low_of_bpu1"] = true_low_of_bpu1
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "true_low_of_bpu2"] = true_low_of_bpu2
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "close_of_bpu2"] = close_of_bpu2
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "open_of_tvx"] = open_of_tvx
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "volume_of_bsu"] = volume_of_bsu
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "volume_of_bpu1"] = volume_of_bpu1
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "volume_of_bpu2"] = volume_of_bpu2

                            df_with_level_atr_bpu_bsu_etc.loc[0 , "timestamp_of_bsu"] = timestamp_of_bsu
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "timestamp_of_bpu1"] = timestamp_of_bpu1
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "timestamp_of_bpu2"] = timestamp_of_bpu2
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "human_time_of_bsu"] = timestamp_of_bsu_with_time
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "human_time_of_bpu1"] = timestamp_of_bpu1_with_time
                            df_with_level_atr_bpu_bsu_etc.loc[0 , "human_time_of_bpu2"] = timestamp_of_bpu2_with_time

                            df_with_level_atr_bpu_bsu_etc.loc[0, "calculated_stop_loss"] = calculated_stop_loss
                            df_with_level_atr_bpu_bsu_etc.loc[0, "buy_order"] = buy_order
                            df_with_level_atr_bpu_bsu_etc.loc[
                                0, "приемлемый_люфт"] = calculated_backlash_from_advanced_atr
                            df_with_level_atr_bpu_bsu_etc.loc[0, "take_profit_3_to_1"] = take_profit_3_to_1
                            df_with_level_atr_bpu_bsu_etc.loc[0, "take_profit_4_to_1"] = take_profit_4_to_1
                            df_with_level_atr_bpu_bsu_etc.loc[0, "distance_between_calculated_stop_loss_and_buy_order"] =\
                                distance_between_calculated_stop_loss_and_buy_order
                            df_with_level_atr_bpu_bsu_etc.loc[0, "distance_between_calculated_stop_loss_and_buy_order_in_atr"] = \
                                distance_between_calculated_stop_loss_and_buy_order_in_atr

                            df_with_level_atr_bpu_bsu_etc.loc[
                                0, "calculated_backlash_from_advanced_atr"] = \
                                calculated_backlash_from_advanced_atr

                            df_with_level_atr_bpu_bsu_etc.loc[
                                0, "min_volume_over_last_n_days"] = int(table_with_ohlcv_data_df['volume'].tail(
                                count_min_volume_over_this_many_days).min())
                            df_with_level_atr_bpu_bsu_etc.loc[
                                0, "count_min_volume_over_this_many_days"] = int(count_min_volume_over_this_many_days)


                            df_with_level_atr_bpu_bsu_etc.to_sql (
                                table_where_ticker_which_had_rebound_situations_from_atl_will_be ,
                                engine_for_db_where_levels_formed_by_rebound_level_will_be ,
                                if_exists = 'append' )

###############################################
                #
                # #find rebound from ath
                # if len(ohlcv_df_with_high_equal_to_ath_slice)>1:
                #
                #     # print ( "ohlcv_df_with_high_equal_to_ath_slice" )
                #     # print ( ohlcv_df_with_high_equal_to_ath_slice )
                #     print ( "list_of_tickers_where_ath_is_also_limit_level" )
                #     print ( list_of_tickers_where_ath_is_also_limit_level )
                #     ohlcv_df_with_high_equal_to_ath_slice=\
                #         ohlcv_df_with_high_equal_to_ath_slice.rename(columns={"index":"index_column"})
                #     # print ( "ohlcv_df_with_high_equal_to_ath_slice" )
                #     # print ( ohlcv_df_with_high_equal_to_ath_slice.to_string () )
                #
                #     row_number_of_bpu1 = ohlcv_df_with_high_equal_to_ath_slice["index_column"].iat[1]
                #     row_number_of_bsu = ohlcv_df_with_high_equal_to_ath_slice["index_column"].iat[0]
                #     # print ( "row_number_of_bpu1" )
                #     # print ( row_number_of_bpu1 )
                #
                #     # get ohlcv of tvx with high and low truncated
                #     open_of_tvx,high_of_tvx,low_of_tvx,close_of_tvx=\
                #         get_ohlc_of_tvx(truncated_high_and_low_table_with_ohlcv_data_df,
                #                          row_number_of_bpu1)
                #     # get ohlcv of bpu2 with high and low truncated
                #     open_of_bpu2 , high_of_bpu2 , low_of_bpu2 , close_of_bpu2 = \
                #         get_ohlc_of_bpu2 ( truncated_high_and_low_table_with_ohlcv_data_df ,
                #                            row_number_of_bpu1 )
                #
                #     atr = calculate_atr ( atr_over_this_period ,
                #                           table_with_ohlcv_data_df ,
                #                           row_number_of_bpu1 )
                #     advanced_atr = calculate_advanced_atr ( advanced_atr_over_this_period ,
                #                                             table_with_ohlcv_data_df ,
                #                                             row_number_of_bpu1 )
                #     atr=round(atr,20)
                #     advanced_atr = round ( advanced_atr ,20)
                #
                #     low_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "low"]
                #     low_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "low"]
                #     open_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "open"]
                #     open_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "open"]
                #     close_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "close"]
                #     close_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "close"]
                #     high_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "high"]
                #     high_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "high"]
                #
                #     # get ohlcv of bsu, bpu1,bpu2, tvx
                #     # get ohlcv of bpu2
                #     # print ("table_with_ohlcv_data_df_2")
                #     # print (table_with_ohlcv_data_df.head(10).to_string())
                #     true_open_of_bpu2 , true_high_of_bpu2 , true_low_of_bpu2 , true_close_of_bpu2 = \
                #         get_ohlc_of_bpu2 ( table_with_ohlcv_data_df ,
                #                            row_number_of_bpu1 )
                #
                #     # get ohlcv of tvx
                #     true_open_of_tvx , true_high_of_tvx , true_low_of_tvx , true_close_of_tvx = \
                #         get_ohlc_of_tvx ( table_with_ohlcv_data_df ,
                #                           row_number_of_bpu1 )
                #     # get ohlc of bsu, bpu1
                #     true_low_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "low"]
                #     true_low_of_bpu1 = table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "low"]
                #     # true_high_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "high"]
                #     # true_high_of_bpu1 = table_with_ohlcv_data_df_slice.loc[row_number_of_bpu1 , "high"]
                #     #
                #     # print("table_with_ohlcv_data_df_slice_in_ath")
                #     # print(table_with_ohlcv_data_df_slice.head(10).to_string())
                #     true_open_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "open"]
                #     true_open_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                #         row_number_of_bpu1 , "open"]
                #     true_close_of_bsu = table_with_ohlcv_data_df_slice.loc[
                #         row_number_of_bsu , "close"]
                #     true_close_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                #         row_number_of_bpu1 , "close"]
                #     true_high_of_bsu = table_with_ohlcv_data_df_slice.loc[row_number_of_bsu , "high"]
                #     true_high_of_bpu1 = table_with_ohlcv_data_df_slice.loc[
                #         row_number_of_bpu1 , "high"]
                #
                #     volume_of_bsu = table_with_ohlcv_data_df.loc[row_number_of_bsu , "volume"]
                #     volume_of_bpu1 = table_with_ohlcv_data_df.loc[
                #         row_number_of_bpu1 , "volume"]
                #     volume_of_bpu2 = get_volume_of_bpu2 ( table_with_ohlcv_data_df ,
                #                                           row_number_of_bpu1 )
                #
                #
                #
                #     if all_time_high<=1:
                #         if volume_of_bpu1 < 1000000 or volume_of_bsu < 1000000 or volume_of_bpu2 < 1000000:
                #             continue
                #
                #     if volume_of_bpu1 < 750000 or volume_of_bsu < 750000 or volume_of_bpu2 < 750000:
                #         continue
                #
                #     if open_of_tvx>=close_of_bpu2:
                #         continue
                #
                #     if true_high_of_tvx<all_time_high-0.5*atr:
                #         continue
                #
                #
                #
                #     timestamp_of_bpu2 = get_timestamp_of_bpu2 ( truncated_high_and_low_table_with_ohlcv_data_df ,
                #                                                 row_number_of_bpu1 )
                #     timestamp_of_bpu1 = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bpu1 , "Timestamp"]
                #     timestamp_of_bsu = truncated_high_and_low_table_with_ohlcv_data_df.loc[row_number_of_bsu , "Timestamp"]
                #
                #     timestamp_of_bpu2_with_time , timestamp_of_bpu2_without_time = get_date_with_and_without_time_from_timestamp (
                #         timestamp_of_bpu2 )
                #     timestamp_of_bpu1_with_time , timestamp_of_bpu1_without_time = get_date_with_and_without_time_from_timestamp (
                #         timestamp_of_bpu1 )
                #     timestamp_of_bsu_with_time , timestamp_of_bsu_without_time = get_date_with_and_without_time_from_timestamp (
                #         timestamp_of_bsu )
                #
                #     # print ( "high_of_bpu2" )
                #     # print ( high_of_bpu2 )
                #
                #     #calcualte atr over 5 days before bpu2. bpu2 is not included
                #     # atr_over_this_period=5
                #
                #
                #
                #     asset_not_open_into_level_bool = \
                #         check_if_bsu_bpu1_bpu2_do_not_open_into_ath_level ( acceptable_backlash , atr , open_of_bsu ,
                #                                                             open_of_bpu1 , open_of_bpu2 ,
                #                                                             high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
                #                                                             low_of_bsu , low_of_bpu1 , low_of_bpu2 )
                #     asset_not_close_into_level_bool = \
                #         check_if_bsu_bpu1_bpu2_do_not_close_into_ath_level ( acceptable_backlash , atr , close_of_bsu ,
                #                                                              close_of_bpu1 , close_of_bpu2 ,
                #                                                              high_of_bsu , high_of_bpu1 , high_of_bpu2 ,
                #                                                              low_of_bsu , low_of_bpu1 , low_of_bpu2 )
                #
                #     if not asset_not_open_into_level_bool and not asset_not_close_into_level_bool:
                #         continue
                #
                #
                #     if atr>0:
                #         backlash=abs(all_time_high-true_high_of_bpu2)
                #         if (backlash<=atr*acceptable_backlash) and (all_time_high-high_of_bpu2)>=0:
                #             list_of_tickers_where_ath_is_also_limit_level.append ( stock_name )
                #
                #             list_of_tickers_where_atl_is_also_limit_level.append ( stock_name )
                #             df_with_level_atr_bpu_bsu_etc = pd.DataFrame ()
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "ticker"] = stock_name
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "exchange"] = exchange
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "short_name"] = short_name
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "ath"] = all_time_high
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "atr"] = atr
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "advanced_atr"] = advanced_atr
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "atr_over_this_period"] = atr_over_this_period
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "advanced_atr_over_this_period"] =\
                #                 advanced_atr_over_this_period
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "backlash"] = backlash
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "acceptable_backlash"] = acceptable_backlash
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "high_of_bsu"] = high_of_bsu
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "high_of_bpu1"] = high_of_bpu1
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "high_of_bpu2"] = high_of_bpu2
                #
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "true_high_of_bsu"] = true_high_of_bsu
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "true_high_of_bpu1"] = true_high_of_bpu1
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "true_high_of_bpu2"] = true_high_of_bpu2
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "close_of_bpu2"] = close_of_bpu2
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "open_of_tvx"] = open_of_tvx
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "volume_of_bsu"] = volume_of_bsu
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "volume_of_bpu1"] = volume_of_bpu1
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "volume_of_bpu2"] = volume_of_bpu2
                #
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "timestamp_of_bsu"] = timestamp_of_bsu
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "timestamp_of_bpu1"] = timestamp_of_bpu1
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "timestamp_of_bpu2"] = timestamp_of_bpu2
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "human_time_of_bsu"] = timestamp_of_bsu_with_time
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "human_time_of_bpu1"] = timestamp_of_bpu1_with_time
                #             df_with_level_atr_bpu_bsu_etc.loc[0 , "human_time_of_bpu2"] = timestamp_of_bpu2_with_time
                #
                #             df_with_level_atr_bpu_bsu_etc.to_sql (
                #                 table_where_ticker_which_had_rebound_situations_from_ath_will_be ,
                #                 engine_for_db_where_levels_formed_by_rebound_level_will_be ,
                #                 if_exists = 'append' )
        except:
            traceback.print_exc()






    print ( "list_of_tickers_where_atl_is_also_limit_level" )
    print ( list_of_tickers_where_atl_is_also_limit_level )
    print ( "list_of_tickers_where_ath_is_also_limit_level" )
    print ( list_of_tickers_where_ath_is_also_limit_level)



if __name__=="__main__":
    start_time=time.time ()
    db_where_ohlcv_data_for_stocks_is_stored="ohlcv_data_for_usdt_pairs_for_1d_timeframe"
    count_only_round_rebound_level=False
    db_where_levels_formed_by_rebound_level_will_be="historical_levels_for_cryptos"
    table_where_ticker_which_had_rebound_situations_from_ath_will_be = "rebound_situations_from_ath"
    table_where_ticker_which_had_rebound_situations_from_atl_will_be = "rebound_situations_from_atl"

    if count_only_round_rebound_level:
        db_where_levels_formed_by_rebound_level_will_be="round_historical_levels_for_cryptos"
    #0.05 means 5%
    acceptable_backlash=0.05
    atr_over_this_period=5
    advanced_atr_over_this_period=30
    count_min_volume_over_this_many_days=30
    search_for_tickers_with_rebound_situations(
                                              db_where_ohlcv_data_for_stocks_is_stored,
                                              db_where_levels_formed_by_rebound_level_will_be,
                                              table_where_ticker_which_had_rebound_situations_from_ath_will_be,
                                                table_where_ticker_which_had_rebound_situations_from_atl_will_be,
                                                acceptable_backlash,
                                                atr_over_this_period,
                                            advanced_atr_over_this_period,count_min_volume_over_this_many_days)

    end_time = time.time ()
    overall_time = end_time - start_time
    print ( 'overall time in minutes=' , overall_time / 60.0 )
    print ( 'overall time in hours=' , overall_time / 3600.0 )
    print ( 'overall time=' , str ( datetime.timedelta ( seconds = overall_time ) ) )
    print ( 'start_time=' , start_time )
    print ( 'end_time=' , end_time )