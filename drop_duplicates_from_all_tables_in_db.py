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
def drop_table(table_name, engine):
    conn = engine.connect()
    query = text(f'''DROP TABLE IF EXISTS {table_name}''')
    conn.execute(query)
    conn.close()
def get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks):
    '''get list of all tables in db which is given as parameter'''
    inspector=inspect(engine_for_ohlcv_data_for_stocks)
    list_of_tables_in_db=inspector.get_table_names()

    return list_of_tables_in_db

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

def drop_all_duplicates_from_all_tables_in_postgres_database(database_name_with_historic_found_models):
    engine_for_ohlcv_data_for_cryptos, \
        connection_to_ohlcv_data_for_stocks = \
        connect_to_postres_db_without_deleting_it_first(database_name_with_historic_found_models)

    list_of_tables_in_ohlcv_db = \
        get_list_of_tables_in_db(engine_for_ohlcv_data_for_cryptos)
    print("list_of_tables_in_ohlcv_db")
    print(list_of_tables_in_ohlcv_db)
    for table_name in list_of_tables_in_ohlcv_db:
        table_with_ohlcv_data_df = \
            pd.read_sql_query(f'''select * from "{table_name}"''',
                              engine_for_ohlcv_data_for_cryptos)

        if table_name!="fast_breakout_situations_of_ath":
            continue
        print(table_with_ohlcv_data_df.tail(10).to_string())
        cols_to_check = ['ticker', 'advanced_atr', 'min_volume_over_last_n_days']

        try:
            table_with_ohlcv_data_df.set_index("level_0",inplace=True)
        except:
            pass
        # remove duplicates, using all columns except "level_0"
        table_with_ohlcv_data_df=\
            table_with_ohlcv_data_df.drop_duplicates(subset=cols_to_check).reset_index(drop=True)

        table_with_ohlcv_data_df.to_sql(f"{table_name}_copy",
                                        connection_to_ohlcv_data_for_stocks,
                                        if_exists='replace',index=False)
        print(table_with_ohlcv_data_df.tail(10).to_string())
        drop_table(table_name, engine_for_ohlcv_data_for_cryptos)
        engine_for_ohlcv_data_for_cryptos.execute(f'''ALTER TABLE {table_name}_copy RENAME TO {table_name};''')


if __name__=="__main__":
    database_name="historical_levels_for_cryptos"
    drop_all_duplicates_from_all_tables_in_postgres_database(database_name)