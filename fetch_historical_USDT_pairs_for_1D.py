# -*- coding: utf-8 -*-
import numpy as np
import multiprocessing
import asyncio
import os
import sys
import time
import traceback
import db_config
import sqlalchemy
import psycopg2
import pandas as pd
# import talib
import datetime
import ccxt
# import ccxt.async_support as ccxt  # noqa: E402
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database,database_exists
from pytz import timezone
import pprint
from verify_that_asset_has_enough_volume_compared_to_bitcoin import check_volume_compared_to_bitcoin
from get_info_from_load_markets import get_asset_type2
from get_info_from_load_markets import get_fees
from get_info_from_load_markets import fetch_huobipro_ohlcv
from get_info_from_load_markets import get_active_trading_pairs_from_huobipro
from get_info_from_load_markets import get_exchange_object_and_limit_of_daily_candles
from get_info_from_load_markets import get_exchange_object
from get_info_from_load_markets import get_exchange_url
from get_info_from_load_markets import get_maker_taker_fees_for_huobi
from get_info_from_load_markets import get_limit_of_daily_candles_original_limits
from get_info_from_load_markets import fetch_entire_ohlcv
from get_info_from_load_markets import get_perpetual_swap_url
from verify_that_asset_has_enough_volume import check_volume_is_enough

def get_maker_and_taker_fees_and_is_shortable(exchange, trading_pair):

    maker_fee=np.nan
    taker_fee=np.nan
    is_shortable=np.nan

    # Get the symbol for the specified trading pair
    symbol = exchange.markets[trading_pair]['symbol']

    # Check if API keys are required for the exchange
    if exchange.apiKey is None or exchange.secret is None:
        return maker_fee, taker_fee, is_shortable
    
    # Retrieve the exchange info for the specified symbol
    exchange_info = exchange.load_trading_limits(symbol)
    print(f"exchange_info_for_{symbol}")
    pprint.pprint(exchange_info)
    #
    # print("exchange.markets[symbol]")
    # pprint.pprint(exchange.markets[symbol])

    # Extract the maker and taker fees
    maker_fee = exchange_info['maker']
    taker_fee = exchange_info['taker']



    # Check if the symbol is shortable
    is_shortable = exchange.markets[symbol].get('short', False)


    # Return the results as a tuple
    return maker_fee, taker_fee, is_shortable

def connect_to_postgres_db_with_deleting_it_first(database):
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database
    connection=None

    engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                             isolation_level = 'AUTOCOMMIT' ,
                             echo = False,
                             pool_pre_ping = True,
                             pool_size = 20 , max_overflow = 0,
                             connect_args={'connect_timeout': 10} )
    print ( f"{engine} created successfully" )

    # Create database if it does not exist.
    if not database_exists ( engine.url ):
        try:
            create_database ( engine.url )
        except:
            traceback.print_exc()
        print ( f'new database created for {engine}' )
        try:
            connection=engine.connect ()
        except:
            traceback.print_exc()
        print ( f'Connection to {engine} established after creating new database' )

    if database_exists ( engine.url ):
        print("database exists ok")

        try:
            engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{dummy_database}" ,
                                     isolation_level = 'AUTOCOMMIT' , echo = False )
        except:
            traceback.print_exc()
        try:
            engine.execute(f'''REVOKE CONNECT ON DATABASE {database} FROM public;''')
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''
                                ALTER DATABASE {database} allow_connections = off;
                                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database}';
    
                            ''' )
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''DROP DATABASE {database};''' )
        except:
            traceback.print_exc()

        try:
            engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                                     isolation_level = 'AUTOCOMMIT' , echo = False )
        except:
            traceback.print_exc()
        try:
            create_database ( engine.url )
        except:
            traceback.print_exc()
        print ( f'new database created for {engine}' )

    try:
        connection = engine.connect ()
    except:
        traceback.print_exc()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection

def add_time_of_next_candle_print_to_df(data_df):
    try:
        # Set the timezone for Moscow
        moscow_tz = timezone('Europe/Moscow')
        almaty_tz = timezone('Asia/Almaty')
        data_df['open_time_datatime_format'] = pd.to_datetime(data_df['open_time'])
        data_df['open_time_without_date'] = data_df['open_time_datatime_format'].dt.strftime('%H:%M:%S')
        # Convert the "open_time" column from UTC to Moscow time
        data_df['open_time_msk'] =\
            data_df['open_time_datatime_format'].dt.tz_localize('UTC').dt.tz_convert(moscow_tz)

        data_df['open_time_msk_time_only'] = data_df['open_time_msk'].dt.strftime('%H:%M:%S')

        # Convert the "open_time_datatime_format" column from UTC to Almaty time
        data_df['open_time_almaty'] =  data_df['open_time_msk'].dt.tz_convert('Asia/Almaty')

        # Create a new column called "open_time_almaty_time" that contains the time in string format
        data_df['open_time_almaty_time_only'] = data_df['open_time_almaty'].dt.strftime('%H:%M:%S')
    except:
        traceback.print_exc()

def connect_to_postres_db_and_delete_it_first(database):
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database

    engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                             isolation_level = 'AUTOCOMMIT' ,
                             echo = False,
                             pool_pre_ping = True,
                             pool_size = 20 , max_overflow = 0,
                             connect_args={'connect_timeout': 10} )
    print ( f"{engine} created successfully" )

    # Create database if it does not exist.
    if not database_exists ( engine.url ):
        create_database ( engine.url )
        print ( f'new database created for {engine}' )
        connection=engine.connect ()
        print ( f'Connection to {engine} established after creating new database' )

    if database_exists ( engine.url ):
        print("database exists ok")

        engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{dummy_database}" ,
                                 isolation_level = 'AUTOCOMMIT' , echo = False )
        try:
            engine.execute(f'''REVOKE CONNECT ON DATABASE {database} FROM public;''')
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''
                                ALTER DATABASE {database} allow_connections = off;
                                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database}';
    
                            ''' )
        except:
            traceback.print_exc()
        try:
            engine.execute ( f'''DROP DATABASE {database};''' )
        except:
            traceback.print_exc()

        engine = create_engine ( f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}" ,
                                 isolation_level = 'AUTOCOMMIT' , echo = False )
        create_database ( engine.url )
        print ( f'new database created for {engine}' )

    connection = engine.connect ()

    print ( f'Connection to {engine} established. Database already existed.'
            f' So no new db was created' )
    return engine , connection

def check_if_stable_coin_is_the_first_part_of_ticker(trading_pair):
    trading_pair_has_stable_coin_name_as_its_first_part=False
    stablecoin_tickers = [
    "USDT_","USDC_","BUSD_","DAI_","FRAX_","TUSD_","USDP_","USDD_",
    "GUSD_","XAUT_","USTC_","EURT_","LUSD_","ALUSD_","EURS_","USDX_",
    "MIM_","sEUR_","WBTC_","sGBP_","sJPY_","sKRW_","sAUD_","GEM_",
    "sXAG_","sXAU_","sXDR_","sBTC_","sETH_","sCNH_","sCNY_","sHKD_",
    "sSGD_","sCHF_","sCAD_","sNZD_","sLTC_","sBCH_","sBNB_","sXRP_",
    "sADA_","sLINK_","sXTZ_","sDOT_","sFIL_","sYFI_","sCOMP_","sAAVE_",
    "sSNX_","sMKR_","sUNI_","sBAL_","sCRV_","sLEND_","sNEXO_","sUMA_",
    "sMUST_","sSTORJ_","sREN_","sBSV_","sDASH_","sZEC_","sEOS_","sXTZ_",
    "sATOM_","sVET_","sTRX_","sADA_","sDOGE_","sDGB_"
]

    for first_part_in_trading_pair in stablecoin_tickers:
        if first_part_in_trading_pair in trading_pair:
            trading_pair_has_stable_coin_name_as_its_first_part=True
            break
        else:
            continue
    return trading_pair_has_stable_coin_name_as_its_first_part




new_counter=0
not_active_pair_counter = 0
list_of_inactive_pairs=[]

def get_hisorical_data_from_exchange_for_many_symbols(last_bitcoin_price,exchange,
                                                            engine,timeframe='1d'):
    print("exchange=",exchange)
    global new_counter
    global list_of_inactive_pairs
    global not_active_pair_counter
    exchange_object=False
    limit_of_daily_candles=np.nan
    active_trading_pairs_list=[]
    # active_trading_pairs_list_from_huobipro=[]
    try:
        # active_trading_pairs_list_from_huobipro=[]
        # if exchange in ["huobipro"]:
        #     active_trading_pairs_list_from_huobipro = get_active_trading_pairs_from_huobipro()
        exchange_object, limit_of_daily_candles=\
            get_limit_of_daily_candles_original_limits(exchange)


        # exchange_object = getattr ( ccxt , exchange ) ()
        exchange_object.enableRateLimit = True
        # exchange_object.fetch_markets()
        # exchange_object_huobipro=np.nan

        # if exchange in ['huobipro']:
        #     exchange_object_huobipro= ccxt.huobipro()
        # shortable_markets=''
        # try:
        #     # shortable_markets = [market['symbol'] for market in markets if market.get('margin', {}).get('short', False)]
        #     # shortable_markets = [market['symbol'] for market in markets if
        #     #                      'margin' in market and market['margin'].get('short', False)]
        #     shortable_markets = [market['symbol'] for market in markets if
        #                          'margin_enabled' in market and market['margin_enabled']]
        # except:
        #     traceback.print_exc()
        # print(f"shortable_markets for {exchange}")
        # print(shortable_markets)
    except:
        traceback.print_exc()

    try:
        # connection_to_usdt_trading_pairs_ohlcv = \
        #     sqlite3.connect ( os.path.join ( os.getcwd () ,
        #                                      "datasets" ,
        #                                      "sql_databases" ,
        #                                      "all_exchanges_multiple_tables_historical_data_for_usdt_trading_pairs.db" ) )
        markets=np.nan
        try:
            markets=exchange_object.load_markets ()
        except:
            pass
        # print("markets___")
        # pprint.pprint(markets)
        # time.sleep(10000)





        list_of_all_symbols_from_exchange=exchange_object.symbols
        print(f"list_of_all_symbols_from_exchange={exchange}")
        print(list_of_all_symbols_from_exchange)

        list_of_trading_pairs_with_USDT = []
        list_of_trading_pairs_with_USD = []
        list_of_trading_pairs_with_BTC = []


        # if exchange in ["huobipro"]:
        #     list_of_all_symbols_from_exchange=active_trading_pairs_list_from_huobipro

        for trading_pair in list_of_all_symbols_from_exchange:
            # for item in counter_gen():
            #     print ("item=",item)



            try:
                print ( "exchange=" , exchange )
                print ( "usdt_pair=" , trading_pair )
                if "UP/" in trading_pair or "DOWN/" in trading_pair or "BEAR/" in \
                        trading_pair or "BULL/" in trading_pair:
                    continue
                if ("/USDT" in trading_pair) or ("/USDC" in trading_pair) \
                        or( "/BUSD" in trading_pair) or ( "/BTC" in trading_pair) or\
                        ( "/HT" in trading_pair)  :
                    print("usdt_pair1=", trading_pair)
                    new_counter = new_counter + 1
                    print("new_counter=",new_counter)
                    list_of_trading_pairs_with_USDT.append(trading_pair)
                    # print ( f"list_of_trading_pairs_with_USDT_on_{exchange}\n" ,
                    #         list_of_trading_pairs_with_USDT )

                    # if ('active' in exchange_object.markets[trading_pair]) or (exchange_object.markets[trading_pair]['active']):

                    # #collect data from 5 years ago
                    # data = exchange_object.fetch_ohlcv ( trading_pair , timeframe, since=1516147200000)
                    #
                    # collect data from 2011 years ago
                    data_df=np.nan

                    # if exchange in ["exmo"]:
                    #     try:
                    #         data = exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=3000)
                    #         # print ( f"counter_for_{exchange}=" , counter )
                    #         header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
                    #         data_df = pd.DataFrame(data, columns=header).set_index('Timestamp')
                    #
                    #     except:
                    #         traceback.print_exc()
                    # elif exchange in ["huobipro"]:
                    #     data_df=fetch_huobipro_ohlcv(trading_pair,
                    #                                  exchange_object_huobipro,
                    #                                  timeframe='1d')


                    # elif exchange in ["gateio"]:
                    #     try:
                    #         data = exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=1000)
                    #         # print ( f"counter_for_{exchange}=" , counter )
                    #         header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
                    #         data_df = pd.DataFrame(data, columns=header).set_index('Timestamp')
                    #
                    #     except:
                    #         traceback.print_exc()

                    # else:
                    #data = exchange_object.fetch_ohlcv(trading_pair, timeframe, since=1293829200000)
                    asset_type=''
                    try:
                        asset_type=get_asset_type2(markets, trading_pair.replace("_", "/"))
                        print(f"asset_type for {trading_pair} on {exchange}")

                        print(asset_type)
                        if asset_type=="option":
                            continue
                        if asset_type=="future":
                            continue
                    except:
                        traceback.print_exc()



                    # try:
                    #     data = exchange_object.fetch_ohlcv(trading_pair, timeframe,
                    #                                        limit=limit_of_daily_candles)
                    #     # print ( f"counter_for_{exchange}=" , counter )
                    #     header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
                    #     data_df = pd.DataFrame(data, columns=header).set_index('Timestamp')
                    #
                    # except:
                    #     traceback.print_exc()
                    try:
                        data_df=fetch_entire_ohlcv(exchange_object,exchange,trading_pair,timeframe,limit_of_daily_candles)
                    except:
                        traceback.print_exc()

                    # if exchange in ["huobi", "huobipro"]:
                    #     try:
                    #         data_df=fetch_huobipro_ohlcv(trading_pair, timeframe='1d')
                    #     except:
                    #         traceback.print_exc()

                    # try:
                    #     data_4h = await exchange_object.fetch_ohlcv ( trading_pair , '1d' )
                    #
                    #     data_df_4h = pd.DataFrame ( data_4h , columns = header ).set_index ( 'Timestamp' )
                    #     print(f"data_df_4h_for_{trading_pair} on exchange {exchange}\n",
                    #           data_df_4h)
                    #     data_df_4h['open_time'] = \
                    #         [dt.datetime.fromtimestamp ( x / 1000.0 ) for x in data_df_4h.index]
                    #     data_df_4h.set_index ( 'open_time' )
                    #     # print ( "list_of_dates=\n" , list_of_dates )
                    #     # time.sleep(5)
                    #     data_df_4h['psar'] = talib.SAR ( data_df_4h.high ,
                    #                                   data_df_4h.low ,
                    #                                   acceleration = 0.02 ,
                    #                                   maximum = 0.2 )
                    #     print ( "data_df_4h\n" , data_df_4h )
                    #
                    #     data_df_4h.to_sql ( f"{trading_pair}_on_{exchange}" ,
                    #                      connection_to_usdt_trading_pairs_4h_ohlcv ,
                    #                      if_exists = 'replace' )
                    #
                    #
                    # except Exception as e:
                    #     print("something is wrong with 4h timeframe"
                    #           f"for {trading_pair} on exchange {exchange}\n",e)
                    print ( "=" * 80 )
                    print ( f'ohlcv for {trading_pair} on exchange {exchange}\n' )
                    print ( data_df )





                    trading_pair=trading_pair.replace("/","_")

                    data_df['ticker'] = trading_pair
                    data_df['exchange'] = exchange
                    # print("markets[trading_pair]")

                    # print(markets[trading_pair])


                    # add asset type to df
                    try:
                        data_df['asset_type'] = asset_type
                    except:
                        data_df['asset_type'] = np.nan
                        traceback.print_exc()

                    # add maker and taker fees
                    try:
                        if exchange!='huobipro':
                            maker_fee, taker_fee=get_fees(markets, trading_pair.replace("_","/"))
                            data_df['maker_fee'] = maker_fee
                            data_df['taker_fee'] = taker_fee

                    except:
                        data_df['maker_fee'] = np.nan
                        data_df['taker_fee'] = np.nan
                        traceback.print_exc()

                    try:
                        if exchange == "huobipro":
                            maker_fee, taker_fee = get_maker_taker_fees_for_huobi(exchange_object)
                            data_df['maker_fee'] = maker_fee
                            data_df['taker_fee'] = taker_fee
                            print("fees for huobi pro")
                            print("maker_fee for huobi")
                            print(maker_fee)
                            print("taker_fee for huobi")
                            print(taker_fee)
                    except:
                        data_df['maker_fee'] = np.nan
                        data_df['taker_fee'] = np.nan
                        traceback.print_exc()

                    # add asset type to df
                    # try:
                    #     data_df['asset_type'] = asset_type
                    # except:
                    #     data_df['asset_type'] = np.nan
                    #     traceback.print_exc()




                    # get info if asset is shortable , get maker and taker fees
                    # try:
                    #     trading_pair_initial = trading_pair.replace("_", "/")
                    #     maker_fee, taker_fee, is_shortable = \
                    #         get_maker_and_taker_fees_and_is_shortable(exchange_object, trading_pair_initial)
                    #     data_df['maker_fee'] = maker_fee
                    #     data_df['taker_fee'] = taker_fee
                    #     data_df['is_shortable'] = is_shortable
                    # except:
                    #     traceback.print_exc()

                    #exclude levereged tockens
                    if "3L" in trading_pair:
                        continue
                    if "3S" in trading_pair:
                        continue

                    if "4L" in trading_pair:
                        continue
                    if "4S" in trading_pair:
                        continue

                    if "5L" in trading_pair:
                        continue
                    if "5S" in trading_pair:
                        continue

                    # add url of trading pair to df
                    try:
                        # market = markets[trading_pair.replace("_", "/")]
                        # market_id = market['id']
                        url_of_trading_pair =\
                            get_exchange_url(exchange, exchange_object, trading_pair.replace("_", "/"))
                        data_df['url_of_trading_pair'] = url_of_trading_pair
                    except:
                        data_df['url_of_trading_pair'] = np.nan
                        traceback.print_exc()

                    # add url of trading pair to df
                    if asset_type=='swap':
                        try:

                            url_of_trading_pair = \
                                get_perpetual_swap_url(exchange, trading_pair.replace("_", "/"))
                            data_df['url_of_trading_pair'] = url_of_trading_pair
                        except:
                            data_df['url_of_trading_pair'] = np.nan
                            traceback.print_exc()





                    #если  в крипе мало данных , то ее не добавляем
                    # if len(data_df)<10:

                    #     continue

                    number_of_available_days_in_dataframe=len(data_df)

                    # # slice last 30 days for volume calculation
                    # min_volume_over_these_many_last_days=30
                    # data_df_n_days_slice=data_df.iloc[:-1].tail(min_volume_over_these_many_last_days).copy()
                    # data_df_n_days_slice["volume_by_close"]=\
                    #     data_df_n_days_slice["volume"]*data_df_n_days_slice["close"]
                    # print("data_df_n_days_slice")
                    # print(data_df_n_days_slice)
                    # min_volume_over_last_n_days_in_dollars=min(data_df_n_days_slice["volume_by_close"])
                    # print("min_volume_over_last_n_days_in_dollars")
                    # print(min_volume_over_last_n_days_in_dollars)
                    #
                    # #проверить, что объем за последние n дней не меньше, чем 2 цены биткойна
                    # if "_BTC" not in trading_pair:
                    #     if min_volume_over_last_n_days_in_dollars<1*last_bitcoin_price:
                    #         print(f"{trading_pair} discarded due to low volume")
                    #         continue
                    # else:
                    #     if min_volume_over_last_n_days_in_dollars<1:
                    #         print(f"{trading_pair} discarded due to low volume")
                    #         continue

                    # #проверить, что объем за последние n дней не меньше, чем 1 цены биткойна
                    min_volume_over_these_many_last_days = 7
                    min_volume_in_bitcoin=2
                    min_acceptable_volume_in_usd=100000
                    asset_has_enough_volume=False
                    # asset_has_enough_volume=check_volume_compared_to_bitcoin(trading_pair,
                    #                                                          min_volume_over_these_many_last_days,
                    #                                                          data_df,
                    #                                                          min_volume_in_bitcoin,
                    #                                                          last_bitcoin_price)
                    asset_has_enough_volume=check_volume_is_enough(trading_pair,
                                     min_volume_over_these_many_last_days,
                                     data_df,
                                     min_acceptable_volume_in_usd
                                     )



                    if not asset_has_enough_volume:
                        continue



                    current_timestamp=time.time()
                    last_timestamp_in_df=data_df.tail(1).index.item()/1000.0
                    print("current_timestamp=",current_timestamp)
                    print("data_df.tail(1).index.item()=",data_df.tail(1).index.item()/1000.0)

                    # if not trading_pair['active']:
                    #     continue

                    #check if the pair is active
                    timeframe_in_seconds=convert_string_timeframe_into_seconds(timeframe)
                    if not abs(current_timestamp-last_timestamp_in_df)<(timeframe_in_seconds):
                        print(f"not quite active trading pair {trading_pair} on {exchange}")
                        not_active_pair_counter=not_active_pair_counter+1
                        print("not_active_pair_counter=",not_active_pair_counter)
                        list_of_inactive_pairs.append(f"{trading_pair}_on_{exchange}")
                        continue
                    print("1program got here")
                    # try:
                    #     data_df['Timestamp'] = \
                    #         [datetime.datetime.timestamp(float(x)) for x in data_df.index]
                    #
                    # except Exception as e:
                    #     print("error_message")
                    #     traceback.print_exc()
                    #     time.sleep(3000000)
                    data_df["Timestamp"] = (data_df.index)

                    try:
                        data_df["open_time"] = data_df["Timestamp"].apply(lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
                    except Exception as e:
                        print("error_message")
                        traceback.print_exc()

                    data_df['Timestamp'] = data_df["Timestamp"] / 1000.0
                        # time.sleep(3000000)
                    print("2program got here")
                    # data_df["open_time"] = data_df.index
                    print("3program got here")
                    data_df.index = range(0, len(data_df))
                    print("4program got here")
                    # data_df = populate_dataframe_with_td_indicator ( data_df )

                    data_df["exchange"] = exchange
                    print("5program got here")
                    data_df["short_name"] = np.nan
                    print("6program got here")
                    data_df["country"] = np.nan
                    data_df["long_name"] = np.nan
                    data_df["sector"] = np.nan
                    # data_df["long_business_summary"] = long_business_summary
                    data_df["website"] = np.nan
                    data_df["quote_type"] = np.nan
                    data_df["city"] = np.nan
                    data_df["exchange_timezone_name"] = np.nan
                    data_df["industry"] = np.nan
                    data_df["market_cap"] = np.nan
                    # data_df["number_of_available_days_in_dataframe"] = number_of_available_days_in_dataframe

                    data_df.set_index("open_time")
                    # try:
                    #     # Set the timezone for Moscow
                    #     moscow_tz = timezone('Europe/Moscow')
                    #     almaty_tz = timezone('Asia/Almaty')
                    #     data_df['open_time_datatime_format'] = pd.to_datetime(data_df['open_time'])
                    #     data_df['open_time_without_date'] = data_df['open_time_datatime_format'].dt.strftime('%H:%M:%S')
                    #     # Convert the "open_time" column from UTC to Moscow time
                    #     data_df['open_time_msk'] =\
                    #         data_df['open_time_datatime_format'].dt.tz_localize('UTC').dt.tz_convert(moscow_tz)
                    #
                    #     data_df['open_time_msk_time_only'] = data_df['open_time_msk'].dt.strftime('%H:%M:%S')
                    #
                    #     # Convert the "open_time_datatime_format" column from UTC to Almaty time
                    #     data_df['open_time_almaty'] =  data_df['open_time_msk'].dt.tz_convert('Asia/Almaty')
                    #
                    #     # Create a new column called "open_time_almaty_time" that contains the time in string format
                    #     data_df['open_time_almaty_time_only'] = data_df['open_time_almaty'].dt.strftime('%H:%M:%S')
                    # except:
                    #     traceback.print_exc()
                    add_time_of_next_candle_print_to_df(data_df)
                    print("2program got here")
                    trading_pair_has_stablecoin_as_first_part=\
                        check_if_stable_coin_is_the_first_part_of_ticker(trading_pair)

                    # if "BUSD/" in trading_pair:
                    #     time.sleep(3000000)
                    if trading_pair_has_stablecoin_as_first_part:
                        print(f"discarded pair due to stable coin being the first part is {trading_pair}")
                        continue

                    print(f"{trading_pair} was added to df")


                    data_df.to_sql ( f"{trading_pair}_on_{exchange}" ,
                                     engine ,
                                     if_exists = 'replace' )



                # elif "/USD" in trading_pair and "/USDT" not in trading_pair:
                #     #print(trading_pair)
                #     list_of_trading_pairs_with_USD.append(trading_pair)

                # elif "/BTC" in trading_pair:
                #     #print(trading_pair)
                #     list_of_trading_pairs_with_BTC.append(trading_pair)


                else:
                    continue






                    #print ( "data=" , data )
            except ccxt.base.errors.RequestTimeout:
                print("found ccxt.base.errors.RequestTimeout error inner")
                continue


            except ccxt.RequestTimeout:
                print("found ccxt.RequestTimeout error inner")
                continue


            except Exception as e:
                print(f"problem with {trading_pair} on {exchange}\n", e)
                traceback.print_exc ()
                continue
            finally:

                continue

        # connection_to_usdt_trading_pairs_ohlcv.close()

    # except Exception as e:
    #     print ( f"found {e} error outer" )
    #     traceback.print_exc ()
    #
    #     traceback.print_exc()



    except Exception as e:
        print(f"problem with {exchange}\n", e)
        traceback.print_exc()

        #await exchange_object.close ()

    finally:

        print("exchange object is closed")

def convert_string_timeframe_into_seconds(timeframe):
    timeframe_in_seconds=0
    if timeframe=='1d':
        timeframe_in_seconds=86400
    if timeframe == '12h':
        timeframe_in_seconds = 86400/2
    if timeframe == '6h':
        timeframe_in_seconds = 86400/4
    if timeframe == '4h':
        timeframe_in_seconds = 86400/6
    if timeframe == '8h':
        timeframe_in_seconds = 86400/3
    return timeframe_in_seconds

def get_real_time_bitcoin_price():
    binance = ccxt.binance()
    btc_ticker = binance.fetch_ticker('BTC/USDT')
    last_bitcoin_price=btc_ticker['close']
    return last_bitcoin_price

def fetch_historical_usdt_pairs_asynchronously(last_bitcoin_price,engine,exchanges_list,timeframe):
    start=time.perf_counter()
    # exchanges_list=['aax', 'ascendex', 'bequant', 'bibox', 'bigone',
    #                 'binance', 'binancecoinm', 'binanceus', 'binanceusdm',
    #                 'bit2c', 'bitbank', 'bitbay', 'bitbns', 'bitcoincom',
    #                 'bitfinex', 'bitfinex2', 'bitflyer', 'bitforex', 'bitget',
    #                 'bithumb', 'bitmart', 'bitmex', 'bitopro', 'bitpanda', 'bitrue',
    #                 'bitso', 'bitstamp', 'bitstamp1', 'bittrex', 'bitvavo', 'bkex',
    #                 'bl3p', 'blockchaincom', 'btcalpha', 'btcbox', 'btcmarkets',
    #                 'btctradeua', 'btcturk', 'buda', 'bw', 'bybit', 'bytetrade',
    #                 'cdax', 'cex', 'coinbase', 'coinbaseprime', 'coinbasepro',
    #                 'coincheck', 'coinex', 'coinfalcon', 'coinflex', 'coinmate',
    #                 'coinone', 'coinspot', 'crex24', 'cryptocom', 'currencycom',
    #                 'delta', 'deribit', 'digifinex', 'eqonex', 'exmo', 'flowbtc',
    #                 'fmfwio', 'ftx', 'ftxus', 'gateio', 'gemini', 'hitbtc', 'hitbtc3',
    #                 'hollaex', 'huobi', 'huobijp', 'huobipro', 'idex',
    #                 'independentreserve', 'indodax', 'itbit', 'kraken', 'kucoin',
    #                 'kucoinfutures', 'kuna', 'latoken', 'lbank', 'lbank2', 'liquid',
    #                 'luno', 'lykke', 'mercado', 'mexc', 'mexc3', 'ndax', 'novadax',
    #                 'oceanex', 'okcoin', 'okex', 'okex5', 'okx', 'paymium', 'phemex',
    #                 'poloniex', 'probit', 'qtrade', 'ripio', 'stex', 'therock',
    #                 'tidebit', 'tidex', 'timex', 'upbit', 'vcc', 'wavesexchange',
    #                 'wazirx', 'whitebit', 'woo', 'xena', 'yobit', 'zaif', 'zb',
    #                 'zipmex', 'zonda']


    # connection_to_usdt_trading_pairs_daily_ohlcv = \
    #     sqlite3.connect ( os.path.join ( os.getcwd () ,
    #                                      "datasets" ,
    #                                      "sql_databases" ,
    #                                      "async_all_exchanges_multiple_tables_historical_data_for_usdt_trading_pairs.db" ) )

    # connection_to_usdt_trading_pairs_4h_ohlcv = \
    #     sqlite3.connect ( os.path.join ( os.getcwd () ,
    #                                      "datasets" ,
    #                                      "sql_databases" ,
    #                                      "async_all_exchanges_multiple_tables_historical_data_for_usdt_trading_pairs_4h.db" ) )

    # coroutines = [await get_hisorical_data_from_exchange_for_many_symbols(exchange ) for exchange in  exchanges_list]
    # await asyncio.gather(*coroutines, return_exceptions = True)
    #
    for exchange in exchanges_list:
        if exchange not in ['binance','huobipro','bybit','mexc',
                            'mexc3',
                            'bitfinex2','exmo','gateio','kucoin','coinex']:
            continue

        # if exchange!="lbank2":
        #     continue

        get_hisorical_data_from_exchange_for_many_symbols(last_bitcoin_price, exchange,
                                                          engine, timeframe)
    #connection_to_usdt_trading_pairs_daily_ohlcv.close()
    # connection_to_usdt_trading_pairs_4h_ohlcv.close ()
    print("list_of_inactive_pairs\n",list_of_inactive_pairs)
    print("len(list_of_inactive_pairs=",len(list_of_inactive_pairs))
    end = time.perf_counter ()
    print("time in seconds is ", end-start)
    print ( "time in minutes is " , (end - start)/60.0 )
    print ( "time in hours is " , (end - start) / 60.0/60.0 )

def fetch_all_ohlcv_tables(timeframe,database_name,last_bitcoin_price):

    engine , connection_to_ohlcv_for_usdt_pairs =\
        connect_to_postgres_db_with_deleting_it_first (database_name)
    exchanges_list = ccxt.exchanges
    how_many_exchanges = len ( exchanges_list )
    step_for_exchanges = 50

    # fetch_historical_usdt_pairs_asynchronously(engine,exchanges_list)

    process_list = []
    for exchange_counter in \
            range ( 0 , len ( exchanges_list ) ,
                    step_for_exchanges ):
        print ( "exchange_counter=" , exchange_counter )
        print (
            f"exchanges[{exchange_counter}:{exchange_counter} + {step_for_exchanges}]" )
        print ( exchanges_list[
                exchange_counter:exchange_counter + step_for_exchanges] )

        # for number_of_exchange , exchange \
        #         in enumerate ( exchanges_list[exchange_counter:exchange_counter +
        #                                                               how_many_separate_processes_to_spawn_each_corresponding_to_one_exchange] ):
        print ( exchanges_list[
                exchange_counter:exchange_counter + step_for_exchanges] )

        p = multiprocessing.Process ( target =
                                      fetch_historical_usdt_pairs_asynchronously ,
                                      args = (last_bitcoin_price,engine , exchanges_list[
                                                       exchange_counter:exchange_counter + step_for_exchanges],timeframe) )
        p.start ()
        process_list.append ( p )
    for process in process_list:
        process.join ()

    try:
        connection_to_ohlcv_for_usdt_pairs.close ()
    except:
        traceback.print_exc()


if __name__=="__main__":
    timeframe='1d'
    # last_bitcoin_price=get_real_time_bitcoin_price()
    last_bitcoin_price=28000
    print("last_bitcoin_price")
    print(last_bitcoin_price)
    database_name="ohlcv_data_for_usdt_pairs_for_1d_timeframe"
    fetch_all_ohlcv_tables(timeframe,database_name,last_bitcoin_price)
#asyncio.run(get_hisorical_data_from_exchange_for_many_symbols_and_exchanges())
