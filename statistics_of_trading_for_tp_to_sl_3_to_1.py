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
from sqlalchemy import text

def get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks):
    '''get list of all tables in db which is given as parameter'''
    inspector=inspect(engine_for_ohlcv_data_for_stocks)
    list_of_tables_in_db=inspector.get_table_names()

    return list_of_tables_in_db

def connect_to_postgres_db_without_deleting_it_first(database):
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

def get_df_with_statistics(database_name_with_historic_found_models):
    engine_for_ohlcv_data_for_cryptos, \
        connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first(database_name_with_historic_found_models)

    list_of_tables_in_ohlcv_db = \
        get_list_of_tables_in_db(engine_for_ohlcv_data_for_cryptos)
    print("list_of_tables_in_ohlcv_db")
    print(list_of_tables_in_ohlcv_db)

    overall_number_of_tp_achieved_when_sl_is_calculated = 0
    overall_number_of_tp_achieved_when_sl_is_technical = 0
    overall_number_of_sl_achieved_when_sl_is_calculated = 0
    overall_number_of_sl_achieved_when_sl_is_technical = 0




    for table_name in list_of_tables_in_ohlcv_db:
        table_with_ohlcv_data_df = \
            pd.read_sql_query(f'''select * from "{table_name}"''',
                              engine_for_ohlcv_data_for_cryptos)

        column_names = table_with_ohlcv_data_df.columns.tolist()
        print("column_names")
        print(column_names)

        table_with_ohlcv_data_df["base"]=""
        table_with_ohlcv_data_df["quote"] = ""
        for row_number in range(0,len(table_with_ohlcv_data_df)):
            ticker=table_with_ohlcv_data_df.loc[row_number,"ticker"]
            # print("ticker")
            # print(ticker)
            ticker_without_exchange=ticker.split("_on_")[0]
            # print("ticker_without_exchange")
            # print(ticker_without_exchange)
            if ":" in ticker_without_exchange:
                ticker_without_exchange=ticker_without_exchange.split(":")[0]
            base=ticker_without_exchange.split("_")[0]
            quote = ticker_without_exchange.split("_")[1]
            table_with_ohlcv_data_df["base"].iat[row_number]=base
            table_with_ohlcv_data_df["quote"].iat[row_number] = quote

            # print("base")
            # print(base)
            # print("quote")
            # print(quote)
        print("table_with_ohlcv_data_df1")
        print(table_with_ohlcv_data_df.tail(10).to_string())
        print(f"len(table_with_ohlcv_data_df)1 fro {table_name}")
        print(len(table_with_ohlcv_data_df))

        table_with_ohlcv_data_df=table_with_ohlcv_data_df.drop_duplicates(subset=["position_entry_timestamp","base"])


        print("table_with_ohlcv_data_df2")
        print(table_with_ohlcv_data_df.reset_index().tail(10).to_string())
        print(f"len(table_with_ohlcv_data_df)2 for {table_name}")
        print(len(table_with_ohlcv_data_df))





        entire_number_of_trades_where_calculated_take_profit_3_to_1_achieved = np.nan
        entire_number_of_trades_where_technical_take_profit_3_to_1_achieved = np.nan

        entire_number_of_trades_where_calculated_stop_loss_with_tp_3_to_1_achieved = np.nan
        entire_number_of_trades_where_technical_stop_loss_with_tp_3_to_1_achieved = np.nan



        number_of_neither_calc_tp_or_sl=np.nan
        number_of_neither_tech_tp_or_sl = np.nan

        if "calculated_take_profit_3_to_1_achieved" in column_names:
            try:
                # entire_number_of_trades_where_calculated_take_profit_3_to_1_achieved=\
                #     table_with_ohlcv_data_df["calculated_take_profit_3_to_1_achieved"].value_counts()[True]

                table_with_ohlcv_data_df1 = table_with_ohlcv_data_df[
                    table_with_ohlcv_data_df['neither_calculated_tp_3_to_1_or_sl_3_to_1_achieved'] == False]
                entire_number_of_trades_where_calculated_take_profit_3_to_1_achieved=\
                    sum(table_with_ohlcv_data_df1["calculated_take_profit_3_to_1_achieved"])

                overall_number_of_tp_achieved_when_sl_is_calculated=entire_number_of_trades_where_calculated_take_profit_3_to_1_achieved+\
                                                                    overall_number_of_tp_achieved_when_sl_is_calculated

                number_of_neither_calc_tp_or_sl = \
                table_with_ohlcv_data_df["neither_calculated_tp_3_to_1_or_sl_3_to_1_achieved"].loc[
                    table_with_ohlcv_data_df["neither_calculated_tp_3_to_1_or_sl_3_to_1_achieved"] == True].count()

            except:
                traceback.print_exc()

        if "technical_take_profit_3_to_1_achieved" in column_names:
            try:

                table_with_ohlcv_data_df1 = table_with_ohlcv_data_df[
                    table_with_ohlcv_data_df['neither_technical_tp_3_to_1_or_sl_3_to_1_achieved'] == False]
                entire_number_of_trades_where_technical_take_profit_3_to_1_achieved=\
                    sum(table_with_ohlcv_data_df1["technical_take_profit_3_to_1_achieved"])

                overall_number_of_tp_achieved_when_sl_is_technical=entire_number_of_trades_where_technical_take_profit_3_to_1_achieved+\
                                                                   overall_number_of_tp_achieved_when_sl_is_technical

                number_of_neither_tech_tp_or_sl = \
                table_with_ohlcv_data_df["neither_technical_tp_3_to_1_or_sl_3_to_1_achieved"].loc[
                    table_with_ohlcv_data_df["neither_technical_tp_3_to_1_or_sl_3_to_1_achieved"] == True].count()

            except:
                traceback.print_exc()

        print(f"entire_number_of_trades_where_calculated_take_profit_3_to_1_achieved for {table_name}")
        print(entire_number_of_trades_where_calculated_take_profit_3_to_1_achieved)

        print(f"entire_number_of_trades_where_technical_take_profit_3_to_1_achieved for {table_name}")
        print(entire_number_of_trades_where_technical_take_profit_3_to_1_achieved)
        
        ###################################################################
        
        if "calculated_stop_loss_with_tp_3_to_1_achieved" in column_names:
            try:
                # entire_number_of_trades_where_calculated_take_profit_3_to_1_achieved=\
                #     table_with_ohlcv_data_df["calculated_take_profit_3_to_1_achieved"].value_counts()[True]

                table_with_ohlcv_data_df1 = table_with_ohlcv_data_df[
                    table_with_ohlcv_data_df['neither_calculated_tp_3_to_1_or_sl_3_to_1_achieved'] == False]
                entire_number_of_trades_where_calculated_stop_loss_with_tp_3_to_1_achieved=\
                    sum(table_with_ohlcv_data_df1["calculated_stop_loss_with_tp_3_to_1_achieved"])

                overall_number_of_sl_achieved_when_sl_is_calculated=entire_number_of_trades_where_calculated_stop_loss_with_tp_3_to_1_achieved+\
                                                                    overall_number_of_sl_achieved_when_sl_is_calculated

                number_of_neither_calc_tp_or_sl = \
                table_with_ohlcv_data_df["neither_calculated_tp_3_to_1_or_sl_3_to_1_achieved"].loc[
                    table_with_ohlcv_data_df["neither_calculated_tp_3_to_1_or_sl_3_to_1_achieved"] == True].count()

                # entire_number_of_trades_where_calculated_stop_loss_with_tp_3_to_1_achieved=\
                #     table_with_ohlcv_data_df["stop_loss_with_calculated_tp_3_to_1_achieved"].loc[
                #     table_with_ohlcv_data_df["stop_loss_with_calculated_tp_3_to_1_achieved"] == False].count()

            except:
                traceback.print_exc()

        if "stop_loss_with_calculated_tp_3_to_1_achieved" in column_names:
            try:
                # entire_number_of_trades_where_calculated_take_profit_3_to_1_achieved=\
                #     table_with_ohlcv_data_df["calculated_take_profit_3_to_1_achieved"].value_counts()[True]

                table_with_ohlcv_data_df1 = table_with_ohlcv_data_df[
                    table_with_ohlcv_data_df['neither_calculated_tp_3_to_1_or_sl_3_to_1_achieved'] == False]
                entire_number_of_trades_where_calculated_stop_loss_with_tp_3_to_1_achieved=\
                    sum(table_with_ohlcv_data_df1["stop_loss_with_calculated_tp_3_to_1_achieved"])

                overall_number_of_sl_achieved_when_sl_is_calculated = entire_number_of_trades_where_calculated_stop_loss_with_tp_3_to_1_achieved + \
                                                                      overall_number_of_sl_achieved_when_sl_is_calculated

                number_of_neither_calc_tp_or_sl = \
                table_with_ohlcv_data_df["neither_calculated_tp_3_to_1_or_sl_3_to_1_achieved"].loc[
                    table_with_ohlcv_data_df["neither_calculated_tp_3_to_1_or_sl_3_to_1_achieved"] == True].count()

                # entire_number_of_trades_where_calculated_stop_loss_with_tp_3_to_1_achieved=\
                #     table_with_ohlcv_data_df["stop_loss_with_calculated_tp_3_to_1_achieved"].loc[
                #     table_with_ohlcv_data_df["stop_loss_with_calculated_tp_3_to_1_achieved"] == False].count()

            except:
                traceback.print_exc()



        if "stop_loss_with_technical_tp_3_to_1_achieved" in column_names:
            try:
                # entire_number_of_trades_where_technical_stop_loss_with_tp_3_to_1_achieved=\
                #     sum(table_with_ohlcv_data_df["stop_loss_with_technical_tp_3_to_1_achieved"])

                table_with_ohlcv_data_df1 = table_with_ohlcv_data_df[
                    table_with_ohlcv_data_df['neither_technical_tp_3_to_1_or_sl_3_to_1_achieved'] == False]

                entire_number_of_trades_where_technical_stop_loss_with_tp_3_to_1_achieved=\
                    table_with_ohlcv_data_df1["stop_loss_with_technical_tp_3_to_1_achieved"].loc[
                    table_with_ohlcv_data_df1["stop_loss_with_technical_tp_3_to_1_achieved"] == True].count()

                overall_number_of_sl_achieved_when_sl_is_technical = entire_number_of_trades_where_technical_stop_loss_with_tp_3_to_1_achieved + \
                                                                      overall_number_of_sl_achieved_when_sl_is_technical

                number_of_neither_tech_tp_or_sl=table_with_ohlcv_data_df["neither_technical_tp_3_to_1_or_sl_3_to_1_achieved"].loc[
                    table_with_ohlcv_data_df["neither_technical_tp_3_to_1_or_sl_3_to_1_achieved"] == True].count()



            except:
                traceback.print_exc()

        print(f"entire_number_of_trades_where_calculated_stop_loss_with_tp_3_to_1_achieved for {table_name}")
        print(entire_number_of_trades_where_calculated_stop_loss_with_tp_3_to_1_achieved)

        print(f"entire_number_of_trades_where_technical_stop_loss_with_tp_3_to_1_achieved for {table_name}")
        print(entire_number_of_trades_where_technical_stop_loss_with_tp_3_to_1_achieved)

        print("number_of_neither_calc_tp_or_sl")
        print(number_of_neither_calc_tp_or_sl)
        print("number_of_neither_tech_tp_or_sl")
        print(number_of_neither_tech_tp_or_sl)

        try:
            print("% of positive trades (sl is calculated")
            print(entire_number_of_trades_where_calculated_take_profit_3_to_1_achieved/(entire_number_of_trades_where_calculated_stop_loss_with_tp_3_to_1_achieved+entire_number_of_trades_where_calculated_take_profit_3_to_1_achieved))
        except:
            pass

        try:
            print("% of positive trades (sl is technical")
            print(entire_number_of_trades_where_technical_take_profit_3_to_1_achieved / (entire_number_of_trades_where_technical_stop_loss_with_tp_3_to_1_achieved+entire_number_of_trades_where_technical_take_profit_3_to_1_achieved))
        except:
            pass

        print("--"*80)
        # print(table_with_ohlcv_data_df.to_string())

if __name__=="__main__":
    database_name_with_historic_found_models="historical_levels_for_cryptos"
    get_df_with_statistics(database_name_with_historic_found_models)