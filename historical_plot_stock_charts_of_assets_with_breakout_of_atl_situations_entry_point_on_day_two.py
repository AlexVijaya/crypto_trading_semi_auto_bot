import shutil
import time
import os
import pandas as pd
import datetime

from pathlib import Path
import traceback
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pdfkit
import imgkit
import numpy as np
import plotly.express as px
from datetime import datetime
# from if_asset_is_close_to_hh_or_ll import find_asset_close_to_hh_and_ll
import datetime as dt
import check_if_asset_is_approaching_its_atl
import db_config
# from sqlalchemy import MetaData
from sqlalchemy import inspect
import logging
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import create_database , database_exists


def select_df_slice_with_td_sel_and_buy_with_count_more_than_1(data_df):
    data_df_slice_seq_sell = data_df.loc[data_df["seq_sell"] >= 1]
    data_df_slice_seq_buy = data_df.loc[data_df["seq_buy"] >= 1]

    return data_df_slice_seq_buy , data_df_slice_seq_sell


def get_date_with_and_without_time_from_timestamp(timestamp):
    open_time = \
        dt.datetime.fromtimestamp ( timestamp )
    # last_timestamp = historical_data_for_stock_ticker_df["Timestamp"].iloc[-1]
    # last_date_with_time = historical_data_for_stock_ticker_df["open_time"].iloc[-1]
    # print ( "type(last_date_with_time)\n" , type ( last_date_with_time ) )
    # print ( "last_date_with_time\n" , last_date_with_time )
    date_with_time = open_time.strftime ( "%Y/%m/%d %H:%M:%S" )
    date_without_time = date_with_time.split ( " " )
    print ( "date_with_time\n" , date_without_time[0] )
    date_without_time = date_without_time[0]
    print ( "date_without_time\n" , date_without_time )
    date_without_time = date_without_time.replace ( "/" , "_" )
    date_with_time = date_with_time.replace ( "/" , "_" )
    date_with_time = date_with_time.replace ( " " , "__" )
    date_with_time = date_with_time.replace ( ":" , "_" )
    return date_with_time , date_without_time


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
        connection = engine.connect ()
        print ( f'Connection to {engine} established after creating new database' )

    connection = engine.connect ()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection


def import_ohlcv_and_levels_formed_by_highs_for_plotting(stock_ticker ,
                                                         connection_to_stock_tickers_ohlcv):
    # path_to_stock_tickers_ohlcv=os.path.join ( os.getcwd () ,
    #                                      "datasets" ,
    #                                      "sql_databases" ,
    #                                      "async_all_exchanges_multiple_tables_historical_data_for_stock_tickers.db" )
    # connection_to_stock_tickers_ohlcv = \
    #     sqlite3.connect (  path_to_stock_tickers_ohlcv)
    print ( "stock_ticker=" , stock_ticker )

    historical_data_for_stock_ticker_df = \
        pd.read_sql ( f'''select * from "{stock_ticker}" ;''' ,
                      connection_to_stock_tickers_ohlcv )

    # connection_to_stock_tickers_ohlcv.close()

    return historical_data_for_stock_ticker_df


def calculate_how_many_last_days_to_plot(data_df , first_high_unix_timestamp):
    last_timestamp = data_df["Timestamp"].iat[-1]
    plot_this_many_last_days = (last_timestamp - first_high_unix_timestamp) / 86400 + 10
    plot_this_many_last_days = int ( plot_this_many_last_days )
    if plot_this_many_last_days <= len ( data_df ):
        return plot_this_many_last_days
    else:
        return plot_this_many_last_days - 10


def plot_ohlcv_charts_with_breakout_of_atl_situations_entry_point_next_day(name_of_folder_where_plots_will_be ,
                                                                 db_where_ohlcv_data_for_stocks_is_stored ,
                                                                 db_where_levels_formed_by_fast_breakout_of_atl_are_stored ,
                                                                 table_where_levels_formed_by_fast_breakout_of_atl_are_stored):
    start_time = time.time ()
    current_timestamp = time.time ()
    counter = 0

    engine_for_stock_tickers_ohlcv_db , connection_to_stock_tickers_ohlcv = \
        connect_to_postres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored )

    engine_for_db_where_levels_formed_by_fast_breakout_of_atl_are_stored , \
    connection_to_db_where_levels_formed_by_fast_breakout_of_atl_are_stored = \
        connect_to_postres_db_without_deleting_it_first ( db_where_levels_formed_by_fast_breakout_of_atl_are_stored )

    table_of_tickers_with_fast_breakout_of_atl_df = pd.read_sql (
        f'''select * from {table_where_levels_formed_by_fast_breakout_of_atl_are_stored} ;''' ,
        connection_to_db_where_levels_formed_by_fast_breakout_of_atl_are_stored )

    print ( "len(table_of_tickers_with_fast_breakout_of_atl_df)" )
    print ( len ( table_of_tickers_with_fast_breakout_of_atl_df ) )

    table_of_tickers_with_fast_breakout_of_atl_df.drop_duplicates ( ignore_index = True , inplace = True )
    print ( "len(table_of_tickers_with_fast_breakout_of_atl_df)" )
    print ( len ( table_of_tickers_with_fast_breakout_of_atl_df ) )
    for row_with_level_formed_by_atl_and_ready_for_fast_breakout in range ( 0 ,
                                                                            len ( table_of_tickers_with_fast_breakout_of_atl_df ) ):
        # print("table_of_tickers_with_fast_breakout_of_atl_df[[row_with_level_formed_by_atl_and_ready_for_fast_breakout]]")
        counter = counter + 1

        try:
            print (
                " table_of_tickers_with_fast_breakout_of_atl_df.loc[[row_with_level_formed_by_atl_and_ready_for_fast_breakout]].to_string ()" )
            print ( table_of_tickers_with_fast_breakout_of_atl_df.loc[
                        [row_with_level_formed_by_atl_and_ready_for_fast_breakout]].to_string () )
            one_row_df = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                [row_with_level_formed_by_atl_and_ready_for_fast_breakout]]
            stock_ticker = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'ticker']
            exchange = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'exchange']
            short_name = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'short_name']
            print ( "stock_ticker=" , stock_ticker )
            print ( "exchange=" , exchange )
            atl = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'atl']
            low_of_bsu = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'low_of_bsu']
            # low_of_bsu = table_of_tickers_with_fast_breakout_of_atl_df.loc[
            #     row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'low_of_bsu']

            # low_of_pre_breakout_bar = table_of_tickers_with_fast_breakout_of_atl_df.loc[row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'low_of_pre_breakout_bar']

            timestamp_of_bsu = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'timestamp_of_bsu']
            timestamp_of_pre_breakout_bar = \
                table_of_tickers_with_fast_breakout_of_atl_df.loc[
                    row_with_level_formed_by_atl_and_ready_for_fast_breakout ,
                    'timestamp_of_pre_breakout_bar']

            human_date_of_bsu = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'human_date_of_bsu']
            human_date_of_pre_breakout_bar = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'human_date_of_pre_breakout_bar']

            min_volume_over_last_n_days = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'min_volume_over_last_n_days']
            count_min_volume_over_this_many_days = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'count_min_volume_over_this_many_days']
            count_min_volume_over_this_many_days = int ( count_min_volume_over_this_many_days )

            # atr_over_this_period = int ( atr_over_this_period )

            advanced_atr = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'advanced_atr']
            advanced_atr_over_this_period = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'advanced_atr_over_this_period']
            advanced_atr_over_this_period = int ( advanced_atr_over_this_period )

            

            human_date_of_pre_breakout_bar_list = human_date_of_pre_breakout_bar.split ( " " )
            human_date_of_pre_breakout_bar = human_date_of_pre_breakout_bar_list[0]

            open_of_breakout_bar = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'open_of_breakout_bar']
            high_of_breakout_bar = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'high_of_breakout_bar']
            low_of_breakout_bar = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'low_of_breakout_bar']
            close_of_breakout_bar = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'close_of_breakout_bar']
            open_of_bar_next_day_after_breakout_bar = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'open_of_bar_next_day_after_breakout_bar']

            # true_low_of_bsu = table_of_tickers_with_fast_breakout_of_atl_df.loc[
            #     row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'true_low_of_bsu']
            # true_low_of_pre_breakout_bar = table_of_tickers_with_fast_breakout_of_atl_df.loc[
            #     row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'true_low_of_pre_breakout_bar']

            volume_of_bsu = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'volume_of_bsu']
            # volume_of_pre_breakout_bar = table_of_tickers_with_fast_breakout_of_atl_df.loc[
            #     row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'volume_of_pre_breakout_bar']
            volume_of_breakout_bar = table_of_tickers_with_fast_breakout_of_atl_df.loc[
                row_with_level_formed_by_atl_and_ready_for_fast_breakout , 'volume_of_breakout_bar']

            list_of_timestamps = []
            list_of_unix_timestamps_for_highs = []
            for key in one_row_df.keys ():
                print ( "key=" , key )
                if "timestamp" in key:
                    if one_row_df[key].iat[0] == one_row_df[key].iat[0]:
                        timestamp_of_high = one_row_df[key].iat[0]
                        if type ( timestamp_of_high ) == str:
                            timestamp_of_high = int ( timestamp_of_high )
                        if timestamp_of_high == None:
                            continue
                        list_of_unix_timestamps_for_highs.append ( timestamp_of_high )
                        date_object = datetime.fromtimestamp ( timestamp_of_high )
                        string_of_date_and_time = date_object.strftime ( '%Y-%m-%d %H:%M:%S' )

                        list_of_timestamps.append ( string_of_date_and_time )

            print ( "list_of_timestamps=" , list_of_timestamps )
            print ( "list_of_unix_timestamps_for_highs=" , list_of_unix_timestamps_for_highs )
            first_high_unix_timestamp = list_of_unix_timestamps_for_highs[0]
            last_high_unix_timestamp = list_of_unix_timestamps_for_highs[-1]

            data_df = import_ohlcv_and_levels_formed_by_highs_for_plotting ( stock_ticker ,
                                                                             connection_to_stock_tickers_ohlcv )
            # data_df_slice_seq_buy , data_df_slice_seq_sell = \
            #     select_df_slice_with_td_sel_and_buy_with_count_more_than_1 ( data_df )
            plot_this_many_last_days_in_second_plot = \
                calculate_how_many_last_days_to_plot ( data_df , first_high_unix_timestamp )
            # stock_ticker_without_slash = stock_ticker.replace ( "/" , "" )
            #
            # # deleting : symbol because somehow it does not get to plot
            # if ":" in stock_ticker:
            #     print ( 'found pair with :' , stock_ticker )
            #     stock_ticker = stock_ticker.replace ( ":" , '__' )
            #     print ( 'found pair with :' , stock_ticker )

            print (
                f'{stock_ticker} on {exchange} is number {row_with_level_formed_by_atl_and_ready_for_fast_breakout + 1} '
                f'out of {len ( table_of_tickers_with_fast_breakout_of_atl_df )}' )

            last_timestamp = data_df["Timestamp"].iat[-1]
            last_date_with_time , last_date_without_time = \
                get_date_with_and_without_time_from_timestamp ( last_timestamp )

            try:
                number_of_charts = 2
                where_to_plot_html = os.path.join ( os.getcwd () ,
                                                    'datasets' ,
                                                    'plots' ,
                                                    name_of_folder_where_plots_will_be , f'{last_date_with_time}' ,
                                                    'stock_plots_html' ,
                                                    f'{counter}_{stock_ticker}_on_{exchange}.html' )

                where_to_plot_pdf = os.path.join ( os.getcwd () ,
                                                   'datasets' ,
                                                   'plots' ,
                                                   name_of_folder_where_plots_will_be , f'{last_date_with_time}' ,
                                                   'stock_plots_pdf' ,
                                                   f'{counter}_{stock_ticker}_on_{exchange}.pdf' )
                where_to_plot_svg = os.path.join ( os.getcwd () ,
                                                   'datasets' ,
                                                   'plots' ,
                                                   name_of_folder_where_plots_will_be , f'{last_date_with_time}' ,
                                                   'stock_plots_svg' ,
                                                   f'{counter}_{stock_ticker}_on_{exchange}.svg' )
                where_to_plot_jpg = os.path.join ( os.getcwd () ,
                                                   'datasets' ,
                                                   'plots' ,
                                                   name_of_folder_where_plots_will_be , f'{last_date_with_time}' ,
                                                   'stock_plots_jpg' ,
                                                   f'{counter}_{stock_ticker}_on_{exchange}.jpg' )

                where_to_plot_png = os.path.join ( os.getcwd () ,
                                                   'datasets' ,
                                                   'plots' ,
                                                   name_of_folder_where_plots_will_be , f'{last_date_with_time}' ,
                                                   'stock_plots_png' ,
                                                   f'{counter}_{stock_ticker}_on_{exchange}.png' )
                # create directory for crypto_exchange_plots parent folder
                # if it does not exists
                path_to_databases = os.path.join ( os.getcwd () ,
                                                   'datasets' ,
                                                   'plots' ,
                                                   name_of_folder_where_plots_will_be ,
                                                   f'{last_date_with_time}' )
                Path ( path_to_databases ).mkdir ( parents = True , exist_ok = True )
                # create directories for all hh images
                formats = ['png' , 'svg' , 'pdf' , 'html' , 'jpg']
                for img_format in formats:
                    path_to_special_format_images_of_mirror_charts = \
                        os.path.join ( os.getcwd () ,
                                       'datasets' ,
                                       'plots' ,
                                       name_of_folder_where_plots_will_be , f'{last_date_with_time}' ,
                                       f'stock_plots_{img_format}' )
                    Path ( path_to_special_format_images_of_mirror_charts ).mkdir ( parents = True , exist_ok = True )

                fig = make_subplots ( rows = number_of_charts , cols = 1 ,
                                      shared_xaxes = False ,
                                      subplot_titles = ('1d' , '1d') ,
                                      vertical_spacing = 0.05 )
                fig.update_layout ( height = 1500 * number_of_charts ,
                                    width = 4000 , margin = {'t': 300} ,
                                    title_text = f'{stock_ticker} '
                                                 f'with level formed by atl={atl} with pre_breakout_bar on {human_date_of_pre_breakout_bar}' + '<br> '
                                                                                                                                                             f'"{short_name}"' ,
                                    font = dict (
                                        family = "Courier New, monospace" ,
                                        size = 40 ,
                                        color = "RebeccaPurple"
                                    ) )
                fig.update_xaxes ( rangeslider = {'visible': False} , row = 1 , col = 1 )
                fig.update_xaxes ( rangeslider = {'visible': False} , row = 2 , col = 1 )
                config = dict ( {'scrollZoom': True} )
                # print(type("historical_data_for_stock_ticker_df['open_time']\n",
                #            historical_data_for_stock_ticker_df.loc[3,'open_time']))

                try:
                    fig.add_trace ( go.Ohlc ( name = f'{stock_ticker} on {exchange}' ,
                                              x = data_df['open_time'] ,
                                              open = data_df['open'] ,
                                              high = data_df['high'] ,
                                              low = data_df['low'] ,
                                              close = data_df['close'] ,
                                              increasing_line_color = 'green' , decreasing_line_color = 'red'
                                              ) , row = 1 , col = 1 , secondary_y = False )
                except Exception as e:
                    print ( "error" , e )
                    traceback.print_exc ()

                # plot bsu
                try:
                    timestamp = list_of_timestamps[0]
                    print ( "timestamp_of_bsu" , timestamp )
                    timestamp = datetime.strptime ( timestamp , "%Y-%m-%d %H:%M:%S" )
                    fig.add_scatter ( x = [timestamp] ,
                                      y = [low_of_bsu] , mode = "markers" ,
                                      marker = dict ( color = 'cyan' , size = 15 ) ,
                                      name = "bsu" , row = 1 , col = 1 )
                except Exception as e:
                    print ( "error" , e )
                    traceback.print_exc ()

                # plot pre_breakout_bar
                # try:
                #     timestamp = list_of_timestamps[1]
                #     timestamp = datetime.strptime ( timestamp , "%Y-%m-%d %H:%M:%S" )
                #     fig.add_scatter ( x = [timestamp] ,
                #                       y = [low_of_pre_breakout_bar] , mode = "markers" ,
                #                       marker = dict ( color = 'cyan' , size = 15 ) ,
                #                       name = "pre_breakout_bar" , row = 1 , col = 1 )
                # except Exception as e:
                #     print ( "error" , e )
                #     traceback.print_exc ()

                # plot bpu2
                # try:
                #     timestamp = list_of_timestamps[2]
                #     timestamp = datetime.strptime ( timestamp , "%Y-%m-%d %H:%M:%S" )
                #     fig.add_scatter ( x = [timestamp] ,
                #                       y = [low_of_bpu2] , mode = "markers" ,
                #                       marker = dict ( color = 'cyan' , size = 15 ) ,
                #                       name = "bpu2" , row = 1 , col = 1 )
                # except Exception as e:
                #     print ( "error" , e )
                #     traceback.print_exc ()

                # plot the same on the second subplot
                data_df_slice_drop_head = \
                    data_df.loc[data_df["Timestamp"] >= (first_high_unix_timestamp - (86400 * 15))]
                data_df_slice_drop_head_than_tail = \
                    data_df_slice_drop_head.loc[(last_high_unix_timestamp + (86400 * 15)) >= data_df["Timestamp"]]

                try:
                    fig.add_trace ( go.Ohlc ( name = f'{stock_ticker} on {exchange}' ,
                                              x = data_df_slice_drop_head_than_tail['open_time'] ,
                                              open = data_df_slice_drop_head_than_tail['open'] ,
                                              high = data_df_slice_drop_head_than_tail['high'] ,
                                              low = data_df_slice_drop_head_than_tail['low'] ,
                                              close = data_df_slice_drop_head_than_tail['close'] ,
                                              increasing_line_color = 'green' , decreasing_line_color = 'red'
                                              ) , row = 2 , col = 1 , secondary_y = False )
                except Exception as e:
                    print ( "error" , e )
                    traceback.print_exc ()

                ##################### plot dots
                # plot bsu

                try:
                    timestamp = list_of_timestamps[0]
                    timestamp = datetime.strptime ( timestamp , "%Y-%m-%d %H:%M:%S" )
                    fig.add_scatter ( x = [timestamp] ,
                                      y = [low_of_bsu] , mode = "markers+text" ,
                                      marker = dict ( color = 'cyan' , size = 2 ) ,
                                      text = "bsu" ,
                                      textposition = 'bottom center' ,
                                      name = "bsu" , row = 2 , col = 1 )
                except Exception as e:
                    print ( "error" , e )
                    traceback.print_exc ()

                # plot pre_breakout bar vertical line
                try:
                    timestamp = list_of_timestamps[1]
                    print ( "timestamp_of_bsu" , timestamp )
                    timestamp = datetime.strptime ( timestamp , "%Y-%m-%d %H:%M:%S" )
                    fig.add_vline ( x = timestamp , line_dash = "dash" , line_color = "black" , opacity = 0.5 )
                except Exception as e:
                    print ( "error" , e )
                    traceback.print_exc ()

                # plot pre_breakout_bar
                # try:
                #     timestamp = list_of_timestamps[1]
                #     timestamp = datetime.strptime ( timestamp , "%Y-%m-%d %H:%M:%S" )
                #     fig.add_scatter ( x = [timestamp] ,
                #                       y = [low_of_pre_breakout_bar] , mode = "markers+text" ,
                #                       marker = dict ( color = 'cyan' , size = 2 ) ,
                #                       text="pre_breakout_bar",
                #                         textposition = 'top center',
                #                       name = "pre_breakout_bar" , row = 2 , col = 1 )
                # except Exception as e:
                #     print ( "error" , e )
                #     traceback.print_exc ()

                #############################################################

                min_low_in_second_plot = data_df_slice_drop_head_than_tail['low'].min ()
                max_high_in_second_plot = data_df_slice_drop_head_than_tail['high'].max ()

                upper_border_of_atr = low_of_bsu - 0.5 * advanced_atr
                lower_border_of_atr = upper_border_of_atr - advanced_atr
                date_where_to_plot_atr_bar_unix_timestamp = data_df_slice_drop_head_than_tail["Timestamp"].iat[1]
                print ( "date_where_to_plot_atr_bar_unix_timestamp" )
                print ( date_where_to_plot_atr_bar_unix_timestamp )
                date_where_to_plot_atr_bar_with_time , date_where_to_plot_atr_bar_without_time = \
                    get_date_with_and_without_time_from_timestamp ( date_where_to_plot_atr_bar_unix_timestamp )
                print ( "date_where_to_plot_atr_bar_without_time" )
                print ( date_where_to_plot_atr_bar_without_time )

                print ( "date_where_to_plot_atr_bar_without_time" )
                print ( date_where_to_plot_atr_bar_without_time )
                date_where_to_plot_atr_bar_without_time = \
                    date_where_to_plot_atr_bar_without_time.replace ( "_" , "-" )

                try:
                    # Create scatter trace of atr (vertical line)
                    timestamp = list_of_timestamps[0]

                    timestamp = datetime.strptime ( timestamp , "%Y-%m-%d %H:%M:%S" )
                    fig.add_scatter (
                        x = [date_where_to_plot_atr_bar_without_time ,
                             date_where_to_plot_atr_bar_without_time] ,
                        y = [lower_border_of_atr , upper_border_of_atr] ,
                        marker = dict ( color = 'magenta' , size = 30 ) ,
                        line = dict ( color = 'magenta' , width = 15 ) ,

                        mode = "lines+text" , row = 2 , col = 1
                    )
                except:
                    traceback.print_exc ()
                # add annotation advanced_atr
                try:
                    timestamp = list_of_timestamps[0]

                    timestamp = datetime.strptime ( timestamp , "%Y-%m-%d %H:%M:%S" )

                    fig.add_scatter ( x = [date_where_to_plot_atr_bar_without_time] ,
                                      y = [lower_border_of_atr] , mode = "markers+text" ,
                                      marker = dict ( color = 'magenta' , size = 2 ) ,
                                      text = f"advanced_atr({advanced_atr_over_this_period})" ,
                                      textposition = 'bottom right' ,
                                      name = "advanced_atr" , row = 2 , col = 1 )
                except Exception as e:
                    print ( "error" , e )
                    traceback.print_exc ()

                # #plot red dots on nines at seq buy
                # try:
                #     list_of_timestamps_in_df_slice=list(data_df['Timestamp'].tail (
                #                                          plot_this_many_last_days_in_second_plot ))
                #     first_timestamp_in_df_slice=list_of_timestamps_in_df_slice[0]
                #
                #     data_df_slice_seq_buy_several_last_days_are_left=\
                #         data_df_slice_seq_buy.loc[data_df_slice_seq_buy["Timestamp"]>=first_timestamp_in_df_slice]
                #
                #     data_df_slice_seq_buy_several_last_days_are_left_exceed_low_true=\
                #         data_df_slice_seq_buy_several_last_days_are_left.loc[(data_df_slice_seq_buy_several_last_days_are_left["seq_buy"]==9)&(data_df_slice_seq_buy_several_last_days_are_left["exceed_low"]==True)]
                #
                #
                #     print("data_df_slice_seq_buy_several_last_days_are_left_exceed_low_true")
                #     print ( data_df_slice_seq_buy_several_last_days_are_left_exceed_low_true.to_string() )
                #
                #     for row_number in range(0,len(data_df_slice_seq_buy_several_last_days_are_left_exceed_low_true)):
                #         try:
                #             fig.add_scatter ( x = [data_df_slice_seq_buy_several_last_days_are_left_exceed_low_true["open_time"].iat[row_number] ],
                #                               y = [data_df_slice_seq_buy_several_last_days_are_left_exceed_low_true["low"].iat[row_number]],
                #                               mode = "markers" ,
                #                               marker = dict ( color = 'red' , size = 20,symbol="diamond" ) ,
                #                               name = "exceed low at nine" , row = 2 , col = 1 )
                #         except:
                #             traceback.print_exc()
                #
                #
                #     # fig.add_scatter (
                #     #     x = data_df_slice_seq_buy_several_last_days_are_left["open_time"] ,
                #     #     y = data_df_slice_seq_buy_several_last_days_are_left["low"] ,
                #     #     mode = "markers+text" ,
                #     #     marker = dict ( color = "rgba(255, 0, 0, 0)" , size = 15 ) ,
                #     #     opacity=1,
                #     #     text=data_df_slice_seq_buy_several_last_days_are_left["seq_buy"],
                #     #     textposition = 'bottom center' ,
                #     #     textfont = dict ( color = "#05f54d", size=20,  ),
                #     #
                #     #     name = "td_count_for_lows" , row = 2 , col = 1 )
                #
                # except Exception as e:
                #     print ( "error" , e )
                #     traceback.print_exc ()
                #
                #
                # #plot green dots on nines seq sell
                # try:
                #     list_of_timestamps_in_df_slice = list ( data_df['Timestamp'].tail (
                #         plot_this_many_last_days_in_second_plot ) )
                #     first_timestamp_in_df_slice = list_of_timestamps_in_df_slice[0]
                #
                #     data_df_slice_seq_sell_several_last_days_are_left = \
                #         data_df_slice_seq_sell.loc[data_df_slice_seq_sell["Timestamp"] >= first_timestamp_in_df_slice]
                #
                #     data_df_slice_seq_sell_several_last_days_are_left_exceed_high_true = \
                #         data_df_slice_seq_sell_several_last_days_are_left.loc[
                #             (data_df_slice_seq_sell_several_last_days_are_left["seq_sell"] == 9) & (
                #                     data_df_slice_seq_sell_several_last_days_are_left["exceed_high"] == True)]
                #
                #     print("data_df_slice_seq_sell_several_last_days_are_left_exceed_high_true")
                #     print ( data_df_slice_seq_sell_several_last_days_are_left_exceed_high_true.to_string() )
                #     # print ( "data_df_slice_seq_sell" )
                #     # print ( data_df_slice_seq_sell.to_string () )
                #
                #     for row_number in range(0,len(data_df_slice_seq_sell_several_last_days_are_left_exceed_high_true)):
                #         try:
                #             fig.add_scatter ( x = [data_df_slice_seq_sell_several_last_days_are_left_exceed_high_true["open_time"].iat[row_number] ],
                #                               y = [data_df_slice_seq_sell_several_last_days_are_left_exceed_high_true["high"].iat[row_number]],
                #                               mode = "markers" ,
                #                               marker = dict ( color = 'green' , size = 20,symbol="diamond" ) ,
                #                               name = "exceed high at nine" , row = 2 , col = 1 )
                #         except:
                #             traceback.print_exc()
                #
                # except:
                #     traceback.print_exc ()

                fig.add_hline ( y = atl )

                # plot all lines with usual atr
                # stop_loss=ath + (atr * 0.05)
                # calculated_backlash_from_atr=atr * 0.05
                # sell_limit=ath - (atr * 0.5)
                # take_profit = sell_limit - (atr * 0.5) * 3
                #
                # fig.add_hline ( y = stop_loss , row = 2 , col = 1 , line_color = "green" )
                # fig.add_hline ( y = ath-calculated_backlash_from_atr , row = 2 , col = 1 , line_color = "black" )
                # fig.add_hline ( y = sell_limit , row = 2 , col = 1 , line_color = "red" )
                # fig.add_hline ( y = take_profit , row = 2 , col = 1 , line_color = "green" )

                # plot all lines with advanced atr (stop loss is calculated)
                calculated_stop_loss = atl + (advanced_atr * 0.05)
                sell_order = atl - (advanced_atr * 0.5)
                take_profit = sell_order - (calculated_stop_loss - sell_order) * 3
                # round decimals for ease of looking at
                sell_order = round ( sell_order , 6 )
                calculated_stop_loss = round ( calculated_stop_loss , 6 )
                take_profit = round ( take_profit , 6 )

                # plot all lines with advanced atr (stop loss is technical)
                technical_stop_loss = high_of_breakout_bar + (0.05 * advanced_atr)
                distance_between_technical_stop_loss_and_sell_order = technical_stop_loss-sell_order
                take_profit_when_stop_loss_is_technical =sell_order - (technical_stop_loss-sell_order ) * 3
                distance_between_technical_stop_loss_and_sell_order_in_atr = \
                    distance_between_technical_stop_loss_and_sell_order / advanced_atr
                # round technical stop loss and take profit for ease of looking at
                technical_stop_loss = round ( technical_stop_loss , 6 )
                take_profit_when_stop_loss_is_technical = \
                    round ( take_profit_when_stop_loss_is_technical , 6 )
                distance_between_technical_stop_loss_and_sell_order_in_atr=\
                    round(distance_between_technical_stop_loss_and_sell_order_in_atr,6)

                technical_stop_loss_possible = np.nan
                if distance_between_technical_stop_loss_and_sell_order < 2 * advanced_atr:
                    technical_stop_loss_possible = True
                else:
                    technical_stop_loss_possible = False

                if technical_stop_loss_possible == False:
                    # only calculated stop loss is acceptable
                    fig.add_hline ( y = calculated_stop_loss , row = 2 , col = 1 , line_color = "magenta" ,
                                    opacity = 0.5 )

                    fig.add_hline ( y = sell_order , row = 2 , col = 1 , line_color = "magenta" , opacity = 0.5 )
                    fig.add_hline ( y = take_profit , row = 2 , col = 1 , line_color = "magenta" )
                else:
                    # both technical and calculated stop losses are acceptable
                    fig.add_hline ( y = calculated_stop_loss , row = 2 , col = 1 , line_color = "magenta" ,
                                    opacity = 0.5 )

                    fig.add_hline ( y = sell_order , row = 2 , col = 1 , line_color = "magenta" , opacity = 0.5 )
                    fig.add_hline ( y = take_profit , row = 2 , col = 1 , line_color = "magenta" )
                    fig.add_hline ( y = technical_stop_loss , row = 2 , col = 1 , line_color = "green" ,
                                    opacity = 0.5 )

                    # fig.add_hline ( y = sell_order , row = 2 , col = 1 , line_color = "green" , opacity = 0.5 )
                    fig.add_hline ( y = take_profit_when_stop_loss_is_technical , row = 2 , col = 1 ,
                                    line_color = "green" )

                # fig.update_xaxes ( patch = dict ( type = 'category' ) , row = 1 , col = 1 )

                # fig.update_layout ( height = 700  , width = 20000 * i, title_text = 'Charts of some crypto assets' )
                fig.update_layout ( margin_autoexpand = True )
                # fig['layout'][f'xaxis{0}']['title'] = 'dates for ' + symbol
                fig.layout.annotations[0].update ( text = '1d' , align = 'right' )
                fig.layout.annotations[1].update ( text = '1d' , align = 'right' )
                fig.update_annotations ( font = dict ( family = "Helvetica" , size = 60 ) )
                try:
                    fig.add_annotation ( text =
                                         f"low_of_bsu={low_of_bsu}"
                                         f" | open_of_breakout_bar={open_of_breakout_bar}"
                                         f" | high_of_breakout_bar={high_of_breakout_bar}"
                                         f" | close_of_breakout_bar={close_of_breakout_bar}"
                                         f" | next_day_open_after_breakout={open_of_bar_next_day_after_breakout_bar}"
                                         f" | volume_of_bsu={int ( volume_of_bsu )}" + "<br>"
                                         f" | volume_of_breakout_bar={int ( volume_of_breakout_bar )}"
                                         f" | min_volume_over_last_{count_min_volume_over_this_many_days}_days={int ( min_volume_over_last_n_days )}"
                                         f" | advanced_atr({advanced_atr_over_this_period})={advanced_atr}"
                                         f" | calculated_SL={calculated_stop_loss}" 
                                         f" | technical_SL={technical_stop_loss}"+ "<br>"
                                         f" | sell_order={sell_order}"
                                         f" | TP_(SL_is_calculated)={take_profit}"
                                         f" | TP_(SL_is_technical)={take_profit_when_stop_loss_is_technical}"
                                         f" | technical_SL-sell_order={distance_between_technical_stop_loss_and_sell_order_in_atr} ATR"
                                         ,
                                         xref = "x domain" , yref = "y domain" ,
                                         font = dict (
                                             family = "Courier New, monospace" ,
                                             size = 35 ,
                                             color = "blue"
                                         )
                                         , bordercolor = "green" ,
                                         borderwidth = 2 ,
                                         borderpad = 4 ,
                                         bgcolor = "white" ,
                                         x = 1 ,
                                         y = 1 ,
                                         row = 2 , col = 1 ,
                                         showarrow = False )
                except:
                    traceback.print_exc ()
                fig.update_layout ( showlegend = False )
                # fig.layout.annotations[0].update ( text = f"{stock_ticker} "
                #                                           f"with level formed by_high={ath}" )
                fig.print_grid ()

                fig.write_html ( where_to_plot_html )

                # convert html to svg
                imgkit.from_file ( where_to_plot_html , where_to_plot_svg )
                # convert html to png

                # imgkit.from_file ( where_to_plot_html ,
                #                    where_to_plot_png ,
                #                    options = {'format': 'png'} )

                # convert html to jpg

                imgkit.from_file ( where_to_plot_html ,
                                   where_to_plot_jpg ,
                                   options = {'format': 'jpeg'} )

            except Exception as e:
                print ( "error" , e )
                traceback.print_exc ()



        except Exception as e:
            print ( "error" , e )
            traceback.print_exc ()
            pass

    connection_to_stock_tickers_ohlcv.close ()
    connection_to_db_where_levels_formed_by_fast_breakout_of_atl_are_stored.close ()
    end_time = time.time ()
    overall_time = end_time - start_time
    print ( 'overall time in minutes=' , overall_time / 60.0 )
    print ( 'overall time in hours=' , overall_time / 60.0 / 60.0 )


if __name__ == "__main__":
    name_of_folder_where_plots_will_be = 'historical_breakout_of_atl_entry_point_on_day_two'
    db_where_ohlcv_data_for_stocks_is_stored = "ohlcv_data_for_usdt_pairs_for_1d_timeframe"
    db_where_levels_formed_by_fast_breakout_of_atl_are_stored = "historical_levels_for_cryptos"
    table_where_levels_formed_by_fast_breakout_of_atl_are_stored = "breakout_situations_of_atl_position_entry_on_day_after_next_day"
    try:
        plot_ohlcv_charts_with_breakout_of_atl_situations_entry_point_next_day ( name_of_folder_where_plots_will_be ,
                                                                                 db_where_ohlcv_data_for_stocks_is_stored ,
                                                                                 db_where_levels_formed_by_fast_breakout_of_atl_are_stored ,
                                                                                 table_where_levels_formed_by_fast_breakout_of_atl_are_stored )
    except:
        traceback.print_exc ()