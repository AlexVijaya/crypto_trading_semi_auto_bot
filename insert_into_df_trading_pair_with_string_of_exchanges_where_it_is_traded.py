import ccxt
import pprint
import ccxt
import ccxt
import pandas as pd
import time
import traceback
import re
import numpy as np
import huobi
import huobi_client
import db_config
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database,database_exists
from sqlalchemy import text
# from huobi_client.generic import GenericClient
def get_all_time_high_low(exchange_object, symbol):

    ticker = exchange_object.fetch_ticker(symbol)
    all_time_high = ticker['high']
    all_time_low = ticker['low']
    return all_time_high, all_time_low
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

def connect_to_postgres_db_with_deleting_it_first(database):
    dialect = db_config.dialect
    driver = db_config.driver
    password = db_config.password
    user = db_config.user
    host = db_config.host
    port = db_config.port

    dummy_database = db_config.dummy_database
    connection = None

    engine = create_engine(f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}",
                           isolation_level='AUTOCOMMIT',
                           echo=False,
                           pool_pre_ping=True,
                           pool_size=20, max_overflow=0,
                           connect_args={'connect_timeout': 10})
    print(f"{engine} created successfully")

    # Create database if it does not exist.
    if not database_exists(engine.url):
        try:
            create_database(engine.url)
        except:
            traceback.print_exc()
        print(f'new database created for {engine}')
        try:
            connection = engine.connect()
        except:
            traceback.print_exc()
        print(f'Connection to {engine} established after creating new database')

    if database_exists(engine.url):
        print("database exists ok")

        try:
            engine = create_engine(f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{dummy_database}",
                                   isolation_level='AUTOCOMMIT', echo=False)
        except:
            traceback.print_exc()
        try:
            engine.execute(f'''REVOKE CONNECT ON DATABASE {database} FROM public;''')
        except:
            traceback.print_exc()
        try:
            engine.execute(f'''
                                ALTER DATABASE {database} allow_connections = off;
                                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{database}';

                            ''')
        except:
            traceback.print_exc()
        try:
            engine.execute(f'''DROP DATABASE {database};''')
        except:
            traceback.print_exc()

        try:
            engine = create_engine(f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}",
                                   isolation_level='AUTOCOMMIT', echo=False)
        except:
            traceback.print_exc()
        try:
            create_database(engine.url)
        except:
            traceback.print_exc()
        print(f'new database created for {engine}')

    try:
        connection = engine.connect()
    except:
        traceback.print_exc()

    print(f'Connection to {engine} established. Database already existed.'
          f' So no new db was created')
    return engine, connection
def get_spread(exchange_instance, symbol):
    # exchange = getattr(ccxt, exchange_id)()
    orderbook = exchange_instance.fetch_order_book(symbol)
    bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
    ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
    spread = ask - bid if (bid is not None and ask is not None) else None
    return spread
def get_perpetual_swap_url(exchange_id, trading_pair):

    trading_pair=trading_pair.split(":")[0]
    base=trading_pair.split("/")[0]
    quote = trading_pair.split("/")[1]

    print(f"base = {base}")
    print(f"quote = {quote}")

    if exchange_id == 'binance':
        return f"https://www.binance.com/en/futures/{trading_pair.replace('/','').upper()}"
    elif exchange_id == 'huobipro':
        return f"https://www.huobi.com/en-us/futures/linear_swap/exchange#contract_code={base}-{quote}&contract_type=swap&type=isolated"
    elif exchange_id == 'bybit':
        return f"https://www.bybit.com/trade/{quote.lower()}/{trading_pair.replace('/','').upper()}"
    elif exchange_id == 'hitbtc3':
        return f"https://www.hitbtc.com/futures/{base.lower()}-to-{quote.lower()}"
    elif exchange_id == 'mexc' or exchange_id == 'mexc3':
        return f"https://futures.mexc.com/exchange/{trading_pair.replace('/','_').upper()}?type=linear_swap"
    elif exchange_id == 'bitfinex' or exchange_id == 'bitfinex2':
        # return f"https://trading.bitfinex.com/t/{trading_pair.replace('/','')+'F0:USDTF0'}"
        base=trading_pair.split('/')[0]
        quote=trading_pair.split('/')[1]
        if quote=='USDT':
            return f"https://trading.bitfinex.com/t/{base}F0:USTF0"
        if quote=='BTC':
            return f"https://trading.bitfinex.com/t/{base}F0:{quote}F0"
    elif exchange_id == 'gateio':
        return f"https://www.gate.io/en/futures_trade/{quote}/{trading_pair.replace('/','_').upper()}"
    elif exchange_id == 'kucoin':
        return f"https://futures.kucoin.com/trade/{trading_pair.replace('/','-')}-SWAP"
    elif exchange_id == 'coinex':
        # return f"https://www.coinex.com/swap/{trading_pair.replace('/','').upper()}"
        return f"https://www.coinex.com/futures/{trading_pair.replace('/','-').upper()}"
    elif exchange_id == 'poloniex':
        return f"https://www.poloniex.com/futures/trade/{base.upper}{quote.upper}PERP"
    elif exchange_id == 'lbank2':
        return f"https://www.lbank.com/futures/{base.lower}{quote.lower}/"
    elif exchange_id == 'lbank':
        return f"https://www.lbank.com/futures/{base.lower}{quote.lower}/"
    else:
        return "Exchange not supported"

def is_scientific_notation(number_string):
    return bool(re.match(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$', str(number_string)))
def scientific_to_decimal(number):
    """
    Converts a number in scientific notation to a decimal number.

    Args:
        number (str): A string representing a number in scientific notation.

    Returns:
        float: The decimal value of the input number.
    """
    num_float=float(number)
    num_str = '{:.{}f}'.format(num_float, abs(int(str(number).split('e')[1])))
    return float(num_str)

def scientific_to_decimal2(number):
    """
    Converts a number in scientific notation to a decimal number.

    Args:
        number (str): A string representing a number in scientific notation.

    Returns:
        float: The decimal value of the input number.
    """
    if 'e' in number:
        mantissa, exponent = number.split('e')
        return float(mantissa) * 10 ** int(exponent)
    else:
        return float(number)

def count_zeros(number):

    number_str = str(number)  # convert the number to a string
    if is_scientific_notation(number_str):

        # print("number_str")
        # print(number_str)
        # print(bool('e' in number_str))
        # print(type(number_str))
        if 'e-' in number_str:
            mantissa, exponent = number_str.split('e-')
            # print("mantissa")
            # print(mantissa)
            # print("exponent")
            # print(int(float(exponent)))
            return int(float(exponent))

    count = 0
    for digit in number_str:
        if digit == '0':
            count += 1
        elif digit == '.':
            continue # stop counting zeros at the decimal point
        else:
            break # skip non-zero digits
    return count

def fetch_huobipro_ohlcv(symbol, exchange,timeframe='1d'):

    ohlcv = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe)
    df = pd.DataFrame(ohlcv, columns=['Timestamp', 'open', 'high', 'low', 'close', 'volume'])
    # df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Timestamp', inplace=True)

    return df
def get_huobipro_fees(trading_pair):
    exchange = ccxt.huobipro()
    symbol_info = exchange.load_markets()[trading_pair]
    # print("symbol_info")
    # print(symbol_info)
    maker_fee = symbol_info['maker']
    taker_fee = symbol_info['taker']
    return maker_fee, taker_fee

def get_fees(markets, trading_pair):
    market=markets[trading_pair]
    # pprint.pprint(market)
    return market['maker'], market['taker']
def get_asset_type(exchange_name, trading_pair):
    exchange = getattr(ccxt, exchange_name)()
    market = exchange.load_markets()[trading_pair]
    # print("market1")
    pprint.pprint(market)
    # market=markets[trading_pair]
    print("pprint.pprint(exchange.describe())")
    pprint.pprint(exchange.describe())


    return market['type']

def get_exchange_url(exchange_id, exchange_object,symbol):
    exchange = exchange_object
    market = exchange.market(symbol)
    if exchange_id == 'binance':
        return f"https://www.binance.com/en/trade/{market['base']}_{''.join(market['quote'].split('/'))}?layout=pro&type=spot"
    elif exchange_id == 'huobipro':
        return f"https://www.huobi.com/en-us/exchange/{market['base'].lower()}_{market['quote'].lower()}/"
    elif exchange_id == 'bybit':
        return f"https://www.bybit.com/ru-RU/trade/spot/{market['base']}/{market['quote']}"
    elif exchange_id == 'hitbtc3':
        return f"https://hitbtc.com/{market['base']}-to-{market['quote']}"
    elif exchange_id == 'mexc' or exchange_id == 'mexc3':
        return f"https://www.mexc.com/exchange/{market['base']}_{market['quote']}"
    elif exchange_id == 'bitfinex' or exchange_id == 'bitfinex2':
        return f"https://trading.bitfinex.com/t/{market['base']}:{market['quote']}?type=exchange"
    elif exchange_id == 'exmo':
        return f"https://exmo.me/en/trade/{market['base']}_{market['quote']}"
    elif exchange_id == 'gateio':
        return f"https://www.gate.io/trade/{market['base'].upper()}_{market['quote'].upper()}"
    elif exchange_id == 'kucoin':
        return f"https://trade.kucoin.com/{market['base']}-{market['quote']}"
    elif exchange_id == 'coinex':
        return f"https://www.coinex.com/exchange/{market['base'].lower()}-{market['quote'].lower()}"
    elif exchange_id == 'poloniex':
        return f"https://www.poloniex.com/trade/{market['base'].upper()}_{market['quote'].upper()}/?type=spot"
    elif exchange_id == 'lbank2':
        return f"https://www.lbank.com/trade/{market['base'].lower()}_{market['quote'].lower()}/"
    elif exchange_id == 'lbank':
        return f"https://www.lbank.com/trade/{market['base'].lower()}_{market['quote'].lower()}/"
    # elif exchange_id == 'bitstamp':
    #     return f"https://www.bitstamp.net/markets/{market['base'].lower()}/{market['quote'].lower()}/"
    else:
        return "Exchange not supported"

def get_asset_type2(markets, trading_pair):
    market = markets[trading_pair]
    return market['type']

# def get_asset_type(markets, trading_pair):
#     # exchange = getattr(ccxt, exchange_name)()
#     # market = exchange.load_markets()[trading_pair]
#     market=markets[trading_pair]
#     return market['type']

def get_taker_tiered_fees(exchange_object):
    trading_fees = exchange_object.describe()['fees']['linear']['trading']
    taker_fees = trading_fees['tiers']['taker']
    return taker_fees

def fetch_entire_ohlcv(exchange_object,exchange_name,trading_pair, timeframe,limit_of_daily_candles):
    # exchange_id = 'bybit'
    # exchange_class = getattr(ccxt, exchange_id)
    # exchange = exchange_class()

    # limit_of_daily_candles = 200
    data = []
    header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
    data_df1 = pd.DataFrame(columns=header)
    data_df=np.nan

    # Fetch the most recent 200 days of data
    data += exchange_object.fetch_ohlcv(trading_pair, timeframe, limit=limit_of_daily_candles)
    first_timestamp_in_df=0
    first_timestamp_in_df_for_gateio=0

    # Fetch previous 200 days of data consecutively
    for i in range(1, 100):

        print("i=", i)
        print("data[0][0] - i * 86400000 * limit_of_daily_candles")
        # print(data[0][0] - i * 86400000 * limit_of_daily_candles)
        try:
            previous_data = exchange_object.fetch_ohlcv(trading_pair,
                                                 timeframe,
                                                 limit=limit_of_daily_candles,
                                                 since=data[-1][0] - i * 86400000 * limit_of_daily_candles)
            data = previous_data + data
        finally:

            data_df1 = pd.DataFrame(data, columns=header)
            if data_df1.iloc[0]['Timestamp'] == first_timestamp_in_df:
                break
            first_timestamp_in_df = data_df1.iloc[0]['Timestamp']
            # print("data_df12")
            # print(data_df1)

            # if exchange_name == "gateio" and first_timestamp_in_df == 1364688000000:
            #     for i in range(1, 100000):
            #         limit_of_daily_candles_for_gateio = 2
            #         print("i=", i)
            #         print("data[0][0] - i * 86400000 * limit_of_daily_candles")
            #         print(data[0][0] - i * 86400000 * limit_of_daily_candles_for_gateio)
            #         try:
            #             additional_previous_data_for_gateio = exchange.fetch_ohlcv(trading_pair,
            #                                                                        timeframe,
            #                                                                        limit=limit_of_daily_candles_for_gateio,
            #                                                                        since=data[0][
            #                                                                                  0] - i * 86400000 * limit_of_daily_candles_for_gateio)
            #             data = additional_previous_data_for_gateio + data
            #             print("data_for_gateio")
            #             print(data)
            #         except:
            #             traceback.print_exc()
            #
            #         data_df1 = pd.DataFrame(data, columns=header)
            #         print("data_df123")
            #         print(data_df1)
            #
            #         if data_df1.iloc[0]['Timestamp'] == first_timestamp_in_df_for_gateio:
            #             break
            #         first_timestamp_in_df_for_gateio = data_df1.iloc[0]['Timestamp']

            # try:
            #     data_df1["open_time"] = data_df1["Timestamp"].apply(
            #         lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
            # except Exception as e:
            #     print("error_message")
            #     traceback.print_exc()
            # data_df1 = data_df1.set_index('Timestamp')
            # print("data_df1")
            # print(data_df1)

            # if len(previous_data) == 0:
            #     break

    header = ['Timestamp', 'open', 'high', 'low', 'close', 'volume']
    data_df = pd.DataFrame(data, columns=header)
    # try:
    #     data_df["open_time"] = data_df["Timestamp"].apply(
    #         lambda x: pd.to_datetime(x, unit='ms').strftime('%Y-%m-%d %H:%M:%S'))
    # except Exception as e:
    #     print("error_message")
    #     traceback.print_exc()
    data_df.drop_duplicates(subset=["Timestamp"],keep="first",inplace=True)
    data_df.sort_values("Timestamp",inplace=True)
    data_df = data_df.set_index('Timestamp')


    return data_df

def get_maker_taker_fees_for_huobi(exchange_object):
    fees = exchange_object.describe()['fees']['trading']
    maker_fee = fees['maker']
    taker_fee = fees['taker']
    return maker_fee, taker_fee
def get_maker_tiered_fees(exchange_object):
    print("exchange_object")
    print(exchange_object)

    print("exchange_object.describe()['fees']")
    print(exchange_object.describe()['fees'])

    trading_fees = exchange_object.describe()['fees']['linear']['trading']
    maker_fees = trading_fees['tiers']['maker']
    return maker_fees


def get_tuple_with_lists_taker_and_maker_fees(exchange_object):


    # retrieve fee structure from exchange
    fee_structure = exchange_object.describe()['fees']['trading']['taker']
    print("fee_structure")
    print(fee_structure)
    print("exchange_object.describe()['fees']")
    print(exchange_object.describe()['fees'])

    # calculate taker fees for each tier
    taker_fees = []
    for tier in fee_structure:
        fee = tier[1]
        if tier[0] == 0:
            taker_fees.append((0, fee))
        else:
            prev_tier = taker_fees[-1]
            taker_fees.append((prev_tier[1], fee))

    # calculate maker fees for each tier
    maker_fees = []
    for tier in fee_structure:
        fee = tier[2]
        if tier[0] == 0:
            maker_fees.append((0, fee))
        else:
            prev_tier = maker_fees[-1]
            maker_fees.append((prev_tier[1], fee))

    return (taker_fees, maker_fees)
def get_dict_taker_and_maker_fees(exchange_object):


    # retrieve fee structure from exchange
    fee_structure = exchange_object.describe()['fees']['trading']['taker']
    print("fee_structure")
    print(fee_structure)
    print("exchange_object.describe()['fees']")
    print(exchange_object.describe()['fees'])

    # calculate taker fees for each tier
    taker_fees = {}
    for tier in fee_structure:
        fee = tier[1]
        if tier[0] == 0:
            taker_fees['0'] = fee
        else:
            prev_tier_fee = taker_fees[str(tier[0] - 1)]
            taker_fees[str(tier[0])] = fee if fee != prev_tier_fee else None

    # calculate maker fees for each tier
    maker_fees = {}
    for tier in fee_structure:
        fee = tier[2]
        if tier[0] == 0:
            maker_fees['0'] = fee
        else:
            prev_tier_fee = maker_fees[str(tier[0] - 1)]
            maker_fees[str(tier[0])] = fee if fee != prev_tier_fee else None

    return {'taker_fees': taker_fees, 'maker_fees': maker_fees}

def get_huobi_margin_pairs():
    huobi = ccxt.huobipro()


    # Check if Huobi supports margin trading
    if 'margin' in huobi.load_markets():
        # Get list of assets available for margin trading
        margin_symbols = huobi.load_markets(True)['margin']
        # Filter margin symbols to get only those with USDT as the quote currency
        margin_pairs = [symbol for symbol in margin_symbols if symbol.endswith('/USDT')]
        return margin_pairs
    else:
        print('Huobi does not support margin trading')
        return []

def get_shortable_assets_for_gateio():
    # Create a Gate.io exchange object
    exchange = ccxt.gateio()
    # print("exchange.load_markets()")
    # pprint.pprint(exchange.load_markets())

    # Load the exchange markets
    markets = exchange.load_markets()

    # Get the list of shortable assets
    shortable_assets = []
    for symbol, market in markets.items():
        if 'info' in market and 'shortable' in market['info'] and market['info']['shortable']:
            shortable_assets.append(symbol)

    return shortable_assets

def get_shortable_assets_for_binance():
    # create a Binance exchange instance
    exchange = ccxt.binance()

    # retrieve the exchange info
    exchange_info = exchange.load_markets()

    # retrieve the symbols that are shortable
    shortable_assets = []
    for symbol in exchange_info:
        market_info = exchange_info[symbol]
        if market_info.get('info', {}).get('isMarginTradingAllowed') == True:
            shortable_assets.append(symbol)

    return shortable_assets

def get_active_trading_pairs_from_huobipro():
    exchange = ccxt.huobipro()
    pairs = exchange.load_markets()
    active_pairs = []
    for pair in pairs.values():
        if pair['active']:
            active_pairs.append(pair['symbol'])
    return active_pairs
def get_exchange_object_and_limit_of_daily_candles(exchange_name):
    exchange_object = None
    limit = None

    # if exchange_name == 'binance':
    #     exchange_object = ccxt.binance()
    #     limit = 2000
    # elif exchange_name == 'huobipro':
    #     exchange_object = ccxt.huobipro()
    #     limit = 2000
    # elif exchange_name == 'bybit':
    #     exchange_object = ccxt.bybit()
    #     limit = 200
    # elif exchange_name == 'hitbtc3':
    #     exchange_object = ccxt.hitbtc3()
    #     limit = 1000
    # elif exchange_name == 'mexc':
    #     exchange_object = ccxt.mexc()
    #     limit = 2000
    # elif exchange_name == 'mexc3':
    #     exchange_object = ccxt.mexc3()
    #     limit = 2000
    # elif exchange_name == 'bitfinex':
    #     exchange_object = ccxt.bitfinex()
    #     limit = 1000
    # elif exchange_name == 'bitfinex2':
    #     exchange_object = ccxt.bitfinex2()
    #     limit = 1000
    # elif exchange_name == 'exmo':
    #     exchange_object = ccxt.exmo()
    #     limit = 2000
    # elif exchange_name == 'gateio':
    #     exchange_object = ccxt.gateio()
    #     limit = 2000
    # elif exchange_name == 'kucoin':
    #     exchange_object = ccxt.kucoin()
    #     limit = 2000
    # elif exchange_name == 'coinex':
    #     exchange_object = ccxt.coinex()
    #     limit = 2000
    # return exchange_object, limit



    if exchange_name == 'binance':
        exchange_object = ccxt.binance()
        limit = 2000
    elif exchange_name == 'huobipro':
        exchange_object = ccxt.huobipro()
        limit = 1000
    elif exchange_name == 'bybit':
        exchange_object = ccxt.bybit()
        limit = 20000
    elif exchange_name == 'hitbtc3':
        exchange_object = ccxt.hitbtc3()
        limit = 10000
    elif exchange_name == 'mexc':
        exchange_object = ccxt.mexc()
        limit = 2000
    elif exchange_name == 'mexc3':
        exchange_object = ccxt.mexc3()
        limit = 2000
    elif exchange_name == 'bitfinex':
        exchange_object = ccxt.bitfinex()
        limit = 1000
    elif exchange_name == 'bitfinex2':
        exchange_object = ccxt.bitfinex2()
        limit = 1000
    elif exchange_name == 'exmo':
        exchange_object = ccxt.exmo()
        limit = 3000
    elif exchange_name == 'gateio':
        exchange_object = ccxt.gateio()
        limit = 20000
    elif exchange_name == 'kucoin':
        exchange_object = ccxt.kucoin()
        limit = 20000

    elif exchange_name == 'coinex':
        exchange_object = ccxt.coinex()
        limit = 20000
    return exchange_object, limit

def get_limit_of_daily_candles_original_limits(exchange_name):
    exchange_object = None
    limit = None

    if exchange_name == 'binance':
        exchange_object = ccxt.binance()
        limit = 1000
    elif exchange_name == 'huobipro':
        exchange_object = ccxt.huobipro()
        limit = 1000
    elif exchange_name == 'bybit':
        exchange_object = ccxt.bybit()
        limit = 200
    elif exchange_name == 'hitbtc3':
        exchange_object = ccxt.hitbtc3()
        limit = 1000
    elif exchange_name == 'mexc':
        exchange_object = ccxt.mexc()
        limit = 1000
    elif exchange_name == 'mexc3':
        exchange_object = ccxt.mexc3()
        limit = 1000
    elif exchange_name == 'bitfinex':
        exchange_object = ccxt.bitfinex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    })
        limit = 1000
    elif exchange_name == 'bitfinex2':
        exchange_object = ccxt.bitfinex2({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    })
        limit = 1000
    elif exchange_name == 'exmo':
        exchange_object = ccxt.exmo()
        limit = 2000
    elif exchange_name == 'gateio':
        exchange_object = ccxt.gateio()
        limit = 1000
    elif exchange_name == 'kucoin':
        exchange_object = ccxt.kucoin()
        limit = 2000
    elif exchange_name == 'coinex':
        exchange_object = ccxt.coinex()
        limit = 2000
    elif exchange_name == 'poloniex':
        exchange_object = ccxt.poloniex()
        limit = 500
    elif exchange_name == 'lbank2':
        exchange_object = ccxt.lbank2()
        limit = 1000
    elif exchange_name == 'lbank':
        exchange_object = ccxt.lbank()
        limit = 1000
    return exchange_object, limit

def get_all_exchanges():
    exchanges = ccxt.exchanges
    return exchanges

    # if exchange_name == 'binance':
    #     exchange_object = ccxt.binance()
    #     limit = 10000
    # elif exchange_name == 'huobipro':
    #     exchange_object = ccxt.huobipro()
    #     limit = 1000
    # elif exchange_name == 'bybit':
    #     exchange_object = ccxt.bybit()
    #     limit = 20000
    # elif exchange_name == 'hitbtc3':
    #     exchange_object = ccxt.hitbtc3()
    #     limit = 10000
    # elif exchange_name == 'mexc':
    #     exchange_object = ccxt.mexc()
    #     limit = 2000
    # elif exchange_name == 'mexc3':
    #     exchange_object = ccxt.mexc3()
    #     limit = 2000
    # elif exchange_name == 'bitfinex':
    #     exchange_object = ccxt.bitfinex()
    #     limit = 10000
    # elif exchange_name == 'bitfinex2':
    #     exchange_object = ccxt.bitfinex2()
    #     limit = 10000
    # elif exchange_name == 'exmo':
    #     exchange_object = ccxt.exmo()
    #     limit = 3000
    # elif exchange_name == 'gateio':
    #     exchange_object = ccxt.gateio()
    #     limit = 20000
    # elif exchange_name == 'kucoin':
    #     exchange_object = ccxt.kucoin()
    #     limit = 20000
    # elif exchange_name == 'coinex':
    #     exchange_object = ccxt.coinex()
    #     limit = 20000
    # return exchange_object, limit

def get_active_trading_pairs_from_exchange(exchange_object):

    pairs = exchange_object.load_markets()
    active_pairs = []
    for pair in pairs.values():
        if pair['active']:
            active_pairs.append(pair['symbol'])
    return active_pairs

def get_ohlcv_kucoin(pair):
    exchange = ccxt.kucoin()
    exchange.load_markets()
    symbol = exchange.market(pair)['symbol']
    timeframe = '1d'
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    return ohlcv

def get_ohlcv_okex(pair):
    exchange = ccxt.okex()
    exchange.load_markets()
    symbol = exchange.market(pair)['symbol']
    timeframe = '1d'
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    return ohlcv
def get_trading_pairs(exchange_object):

    markets = exchange_object.load_markets()
    trading_pairs = list(markets.keys())
    return trading_pairs
def get_exchange_object2(exchange_name):
    exchange_objects = {
        # 'aax': ccxt.aax(),
        # 'aofex': ccxt.aofex(),
        'ace': ccxt.ace(),
        'alpaca': ccxt.alpaca(),
        'ascendex': ccxt.ascendex(),
        'bequant': ccxt.bequant(),
        # 'bibox': ccxt.bibox(),
        'bigone': ccxt.bigone(),
        'binance': ccxt.binance(),
        'binanceus': ccxt.binanceus(),
        'binancecoinm': ccxt.binancecoinm(),
        'binanceusdm':ccxt.binanceusdm(),
        'bit2c': ccxt.bit2c(),
        'bitbank': ccxt.bitbank(),
        'bitbay': ccxt.bitbay(),
        'bitbns': ccxt.bitbns(),
        'bitcoincom': ccxt.bitcoincom(),
        'bitfinex': ccxt.bitfinex(),
        'bitfinex2': ccxt.bitfinex2(),
        'bitflyer': ccxt.bitflyer(),
        'bitforex': ccxt.bitforex(),
        'bitget': ccxt.bitget(),
        'bithumb': ccxt.bithumb(),
        # 'bitkk': ccxt.bitkk(),
        'bitmart': ccxt.bitmart(),
        # 'bitmax': ccxt.bitmax(),
        'bitmex': ccxt.bitmex(),
        'bitpanda': ccxt.bitpanda(),
        'bitso': ccxt.bitso(),
        'bitstamp': ccxt.bitstamp(),
        'bitstamp1': ccxt.bitstamp1(),
        'bittrex': ccxt.bittrex(),
        'bitrue':ccxt.bitrue(),
        'bitvavo': ccxt.bitvavo(),
        # 'bitz': ccxt.bitz(),
        'bl3p': ccxt.bl3p(),
        # 'bleutrade': ccxt.bleutrade(),
        # 'braziliex': ccxt.braziliex(),
        'bkex': ccxt.bkex(),
        'btcalpha': ccxt.btcalpha(),
        'btcbox': ccxt.btcbox(),
        'btcmarkets': ccxt.btcmarkets(),
        # 'btctradeim': ccxt.btctradeim(),
        'btcturk': ccxt.btcturk(),
        'btctradeua':ccxt.btctradeua(),
        'buda': ccxt.buda(),
        'bybit': ccxt.bybit(),
        # 'bytetrade': ccxt.bytetrade(),
        # 'cdax': ccxt.cdax(),
        'cex': ccxt.cex(),
        # 'chilebit': ccxt.chilebit(),
        'coinbase': ccxt.coinbase(),
        'coinbaseprime': ccxt.coinbaseprime(),
        'coinbasepro': ccxt.coinbasepro(),
        'coincheck': ccxt.coincheck(),
        # 'coinegg': ccxt.coinegg(),
        'coinex': ccxt.coinex(),
        'coinfalcon': ccxt.coinfalcon(),
        'coinsph':ccxt.coinsph(),
        # 'coinfloor': ccxt.coinfloor(),
        # 'coingi': ccxt.coingi(),
        # 'coinmarketcap': ccxt.coinmarketcap(),
        'cryptocom': ccxt.cryptocom(),
        'coinmate': ccxt.coinmate(),
        'coinone': ccxt.coinone(),
        'coinspot': ccxt.coinspot(),
        # 'crex24': ccxt.crex24(),
        'currencycom': ccxt.currencycom(),
        'delta': ccxt.delta(),
        'deribit': ccxt.deribit(),
        'digifinex': ccxt.digifinex(),
        # 'dsx': ccxt.dsx(),
        # 'dx': ccxt.dx(),
        # 'eqonex': ccxt.eqonex(),
        # 'eterbase': ccxt.eterbase(),
        'exmo': ccxt.exmo(),
        # 'exx': ccxt.exx(),
        # 'fcoin': ccxt.fcoin(),
        # 'fcoinjp': ccxt.fcoinjp(),
        # 'ftx': ccxt.ftx(),
        'flowbtc':ccxt.flowbtc(),
        'fmfwio': ccxt.fmfwio(),
        'gate':ccxt.gate(),
        'gateio': ccxt.gateio(),
        'gemini': ccxt.gemini(),
        # 'gopax': ccxt.gopax(),
        # 'hbtc': ccxt.hbtc(),
        'hitbtc': ccxt.hitbtc(),
        # 'hitbtc2': ccxt.hitbtc2(),
        # 'hkbitex': ccxt.hkbitex(),
        'hitbtc3': ccxt.hitbtc3(),
        'hollaex': ccxt.hollaex(),
        'huobijp': ccxt.huobijp(),
        'huobipro': ccxt.huobipro(),
        # 'ice3x': ccxt.ice3x(),
        'idex': ccxt.idex(),
        # 'idex2': ccxt.idex2(),
        'indodax': ccxt.indodax(),
        'independentreserve': ccxt.independentreserve(),

        'itbit': ccxt.itbit(),
        'kraken': ccxt.kraken(),
        'krakenfutures': ccxt.krakenfutures(),
        'kucoin': ccxt.kucoin(),
        'kuna': ccxt.kuna(),
        # 'lakebtc': ccxt.lakebtc(),
        'latoken': ccxt.latoken(),
        'lbank': ccxt.lbank(),
        # 'liquid': ccxt.liquid(),
        'luno': ccxt.luno(),
        'lykke': ccxt.lykke(),
        'mercado': ccxt.mercado(),
        'mexc':ccxt.mexc(),
        'mexc3' : ccxt.mexc3(),
        # 'mixcoins': ccxt.mixcoins(),
        'paymium':ccxt.paymium(),
        'poloniexfutures':ccxt.poloniexfutures(),
        'ndax': ccxt.ndax(),
        'novadax': ccxt.novadax(),
        'oceanex': ccxt.oceanex(),
        'okcoin': ccxt.okcoin(),
        'okex': ccxt.okex(),
        'okex5':ccxt.okex5(),
        'okx':ccxt.okx(),
        'bitopro': ccxt.bitopro(),
        'huobi': ccxt.huobi(),
        'lbank2': ccxt.lbank2(),
        'blockchaincom': ccxt.blockchaincom(),
        'btcex': ccxt.btcex(),
        'kucoinfutures': ccxt.kucoinfutures(),
        # 'okex3': ccxt.okex3(),
        # 'p2pb2b': ccxt.p2pb2b(),
        # 'paribu': ccxt.paribu(),
        'phemex': ccxt.phemex(),
        'tokocrypto':ccxt.tokocrypto(),
        'poloniex': ccxt.poloniex(),
        'probit': ccxt.probit(),
        # 'qtrade': ccxt.qtrade(),
        'ripio': ccxt.ripio(),
        # 'southxchange': ccxt.southxchange(),
        'stex': ccxt.stex(),
        # 'stronghold': ccxt.stronghold(),
        # 'surbitcoin': ccxt.surbitcoin(),
        # 'therock': ccxt.therock(),
        # 'tidebit': ccxt.tidebit(),
        'tidex': ccxt.tidex(),
        'timex': ccxt.timex(),
        'upbit': ccxt.upbit(),
        # 'vcc': ccxt.vcc(),
        'wavesexchange': ccxt.wavesexchange(),
        'woo':ccxt.woo(),
        'wazirx':ccxt.wazirx(),
        'whitebit': ccxt.whitebit(),
        # 'xbtce': ccxt.xbtce(),
        # 'xena': ccxt.xena(),
        'yobit': ccxt.yobit(),
        'zaif': ccxt.zaif(),
        'zb': ccxt.zb(),
        'zonda':ccxt.zonda()
    }
    exchange_object = exchange_objects.get(exchange_name)
    if exchange_object is None:
        raise ValueError(f"Exchange '{exchange_name}' is not available via CCXT.")
    return exchange_object
def get_exchange_object(exchange_name):
    exchange_objects = {
        'binance': ccxt.binance(),
        'huobipro': ccxt.huobipro(),
        'bybit': ccxt.bybit(),
        'hitbtc3': ccxt.hitbtc3(),
        'mexc': ccxt.mexc(),
        'mexc3': ccxt.mexc3(),
        'bitfinex': ccxt.bitfinex({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'bitfinex2': ccxt.bitfinex2({
        'rateLimit': 6000,  # Set a custom rate limit of 6000 ms (6 seconds)
        'enableRateLimit': True  # Enable rate limiting
    }),
        'exmo': ccxt.exmo(),
        'gateio': ccxt.gateio(),
        'kucoin': ccxt.kucoin(),
        'coinex': ccxt.coinex(),
        'bitstamp': ccxt.bitstamp()}
    return exchange_objects.get(exchange_name)


def get_exchange_object_for_binance_via_vpn():
    exchange = ccxt.binance({
        'apiKey': 'your-api-key',
        'secret': 'your-api-secret',
        'timeout': 30000,
        'enableRateLimit': True,
        'proxy': 'https://your-vpn-server.com:port',
        'proxyCredentials': {
            'username': 'your-username',
            'password': 'your-password'
        }
    })
def get_ohlcv_from_huobi_pro():
    # create a new instance of the CCXT Huobi Pro exchange
    exchange = ccxt.huobipro()

    # retrieve a list of all symbols on the Huobi Pro exchange
    symbols = exchange.load_markets()

    # loop through each symbol and retrieve its OHLCV data
    for symbol in symbols:
        candles = exchange.fetch_ohlcv(symbol, '1d')
        df = pd.DataFrame(candles, columns=['Timestamp', 'open', 'high', 'low', 'close', 'volume'])
        # df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df.set_index('Timestamp', inplace=True)

        # print the OHLCV data for the symbol
        print(f"Symbol: {symbol}")
        for candle in candles:
            print(
                f"Time: {candle[0]}, Open: {candle[1]}, High: {candle[2]}, Low: {candle[3]}, Close: {candle[4]}, Volume: {candle[5]}")

# def get_huobi_ohlcv():
#     # create a new instance of the Huobi API client
#     # create a new instance of the Huobi API client
#     # client = GenericClient(api_key='your_api_key', secret_key='your_secret_key')
#
#     # retrieve a list of all symbols on the Huobi Pro exchange
#     symbols = client.get_symbols()
#
#     # create an empty DataFrame to store the OHLCV data
#     df = pd.DataFrame()
#
#     # loop through each symbol and retrieve its OHLCV data
#     for symbol in symbols:
#         # retrieve the OHLCV data for the symbol
#         candles = client.get_candles(symbol['symbol'], '1day')
#
#         # create a DataFrame for the OHLCV data
#         candles_df = pd.DataFrame(candles, columns=['Timestamp', 'open', 'high', 'low', 'close', 'volume'])
#         candles_df['Timestamp'] = pd.to_datetime(candles_df['Timestamp'], unit='s')
#         candles_df.set_index('Timestamp', inplace=True)
#         candles_df.columns = [f"{symbol['symbol']}_{col}" for col in candles_df.columns]
#
#         # merge the OHLCV data for the symbol into the main DataFrame
#         df = pd.concat([df, candles_df], axis=1, sort=True)
#
#     return df
def check_if_stable_coin_is_the_first_part_of_ticker(trading_pair):
    trading_pair_has_stable_coin_name_as_its_first_part=False
    stablecoin_tickers = [
        "USDT/", "USDC/", "BUSD/", "DAI/", "FRAX/", "TUSD/", "USDP/", "USDD/",
        "GUSD/", "XAUT/", "USTC/", "EURT/", "LUSD/", "ALUSD/", "EURS/", "USDX/",
        "MIM/", "sEUR/", "WBTC/", "sGBP/", "sJPY/", "sKRW/", "sAUD/", "GEM/",
        "sXAG/", "sXAU/", "sXDR/", "sBTC/", "sETH/", "sCNH/", "sCNY/", "sHKD/",
        "sSGD/", "sCHF/", "sCAD/", "sNZD/", "sLTC/", "sBCH/", "sBNB/", "sXRP/",
        "sADA/", "sLINK/", "sXTZ/", "sDOT/", "sFIL/", "sYFI/", "sCOMP/", "sAAVE/",
        "sSNX/", "sMKR/", "sUNI/", "sBAL/", "sCRV/", "sLEND/", "sNEXO/", "sUMA/",
        "sMUST/", "sSTORJ/", "sREN/", "sBSV/", "sDASH/", "sZEC/", "sEOS/", "sXTZ/",
        "sATOM/", "sVET/", "sTRX/", "sADA/", "sDOGE/", "sDGB/"
    ]

    for first_part_in_trading_pair in stablecoin_tickers:
        if first_part_in_trading_pair in trading_pair:
            trading_pair_has_stable_coin_name_as_its_first_part=True
            break
        else:
            continue
    return trading_pair_has_stable_coin_name_as_its_first_part
def return_list_of_all_stablecoin_bases_with_slash():
    stablecoin_bases_with_slash_list = [
        "USDT/", "USDC/", "BUSD/", "DAI/", "FRAX/", "TUSD/", "USDP/", "USDD/",
        "GUSD/", "XAUT/", "USTC/", "EURT/", "LUSD/", "ALUSD/", "EURS/", "USDX/",
        "MIM/", "sEUR/", "WBTC/", "sGBP/", "sJPY/", "sKRW/", "sAUD/", "GEM/",
        "sXAG/", "sXAU/", "sXDR/", "sBTC/", "sETH/", "sCNH/", "sCNY/", "sHKD/",
        "sSGD/", "sCHF/", "sCAD/", "sNZD/", "sLTC/", "sBCH/", "sBNB/", "sXRP/",
        "sADA/", "sLINK/", "sXTZ/", "sDOT/", "sFIL/", "sYFI/", "sCOMP/", "sAAVE/",
        "sSNX/", "sMKR/", "sUNI/", "sBAL/", "sCRV/", "sLEND/", "sNEXO/", "sUMA/",
        "sMUST/", "sSTORJ/", "sREN/", "sBSV/", "sDASH/", "sZEC/", "sEOS/", "sXTZ/",
        "sATOM/", "sVET/", "sTRX/", "sADA/", "sDOGE/", "sDGB/"
    ]
    return stablecoin_bases_with_slash_list

def get_exchanges_for_trading_pair(df, trading_pair):
    exchanges = []
    for col in df.columns:
        if trading_pair in df[col].values:
            exchanges.append(col)
    return exchanges
def remove_leveraged_pairs(filtered_pairs):
    levereged_tokens_string_list=["3S", "3L", "2S", "2L", "4S", "4L", "5S", "5L","6S", "6L"]
    for token in levereged_tokens_string_list:
        filtered_pairs = [pair for pair in filtered_pairs if token not in pair]
    return filtered_pairs

def remove_futures_with_expiration_and_options(filtered_pairs):
    futures_with_expiration_and_options_ends_with_this_string=["-P", "-C", "-M",":P", ":C", ":M"]
    for ending in futures_with_expiration_and_options_ends_with_this_string:
        filtered_pairs = [pair for pair in filtered_pairs if ending not in pair]
    return filtered_pairs


def add_exchange_count(df,exchange_map):
    # Create a new DataFrame to store the results
    result_df = pd.DataFrame(columns=['trading_pair', 'exchange_count'])

    # Define a dictionary to map exchange ids to exchange names


    # Iterate over each row in the input DataFrame
    for index, row in df.iterrows():
        # Get the trading pair and the list of exchanges where it is traded
        trading_pair = index
        exchanges = [col for col in df.columns if row[col] != '']

        # Map exchange ids to exchange names
        exchanges = [exchange_map.get(exchange, exchange) for exchange in exchanges]

        # Combine exchange names for the same exchange
        unique_exchanges = []
        for exchange in exchanges:
            is_subexchange = False
            for other_exchange in exchanges:
                if exchange != other_exchange and exchange in other_exchange:
                    is_subexchange = True
                    break
            if not is_subexchange:
                unique_exchanges.append(exchange)

        # Count the number of exchanges where the trading pair is traded
        exchange_count = len(unique_exchanges)

        # Add a new row to the result DataFrame
        result_df = result_df.append({'trading_pair': trading_pair, 'exchange_count': exchange_count},
                                     ignore_index=True)

    # Set the trading_pair column as the index of the result DataFrame
    result_df.set_index('trading_pair', inplace=True)

    return result_df

def add_exchange_count_without_append_to_df(df, exchange_map):
    # Create a new DataFrame to store the results
    result_df = pd.DataFrame(columns=['trading_pair', 'exchange_count'])

    # Define a dictionary to map exchange ids to exchange names

    # Iterate over each row in the input DataFrame
    for index, row in df.iterrows():
        # Get the trading pair and the list of exchanges where it is traded
        trading_pair = index
        exchanges = [col for col in df.columns if row[col] != '']

        # Map exchange ids to exchange names
        exchanges = [exchange_map.get(exchange, exchange) for exchange in exchanges]

        # Combine exchange names for the same exchange
        unique_exchanges = []
        for exchange in exchanges:
            is_subexchange = False
            for other_exchange in exchanges:
                if exchange != other_exchange and exchange in other_exchange:
                    is_subexchange = True
                    break
            if not is_subexchange:
                unique_exchanges.append(exchange)

        # Count the number of exchanges where the trading pair is traded
        exchange_count = len(unique_exchanges)

        # Add a new row to the result DataFrame
        result_df.loc[trading_pair] = [trading_pair, exchange_count]

    # Set the trading_pair column as the index of the result DataFrame
    result_df.set_index('trading_pair', inplace=True)

    return result_df
def get_exchanges_for_trading_pairs(df):
    # Create a set of all unique trading pairs in the DataFrame
    trading_pairs = set(df.values.flatten())

    # Create a dictionary to store the exchanges where each trading pair is traded
    trading_pair_exchanges = {}
    for pair in trading_pairs:
        print("pair")
        print(pair)
        exchanges = [col for col in df.columns if pair in df[col].values]
        trading_pair_exchanges[pair] = '_'.join(exchanges)

    # Create a new DataFrame from the trading_pair_exchanges dictionary
    new_df = pd.DataFrame.from_dict(trading_pair_exchanges, orient='index', columns=['exchanges_where_pair_is_traded'])
    new_df.index.name = 'trading_pair'

    return new_df

def remove_not_needed_exchanges(reduced_list, list_of_not_needed_exchanges):
    print("reduced_list")
    print(reduced_list)
    print("list_of_not_needed_exchanges")
    print(list_of_not_needed_exchanges)
    return [exchange for exchange in reduced_list if exchange not in list_of_not_needed_exchanges]

def extract_unique_exchanges(row):
    exchanges_list = row['exchanges_where_pair_is_traded'].split('_')
    reduced_list = []
    list_of_not_needed_exchanges=[]
    # for exchange in exchanges:
    for exchange in exchanges_list:
        found = False
        for other_exchange in exchanges_list:
            if other_exchange.startswith(exchange) and other_exchange != exchange:
                found = True
                list_of_not_needed_exchanges.append(other_exchange)
                break
        if not found:

            reduced_list.append(exchange)

    print("list_of_not_needed_exchanges")
    print(list_of_not_needed_exchanges)
    reduced_list_ultimate=remove_not_needed_exchanges(exchanges_list, list_of_not_needed_exchanges)

    return '_'.join(reduced_list_ultimate)
def calculate_number_of_exchanges_where_trading_pair_is_traded_on(row):
    exchanges_list = row.split('_')
    return(len(exchanges_list))
def get_exchange_map_from_exchange_id_to_exchange_name(exchange_ids):
    exchange_map = {}
    for exchange_id in exchange_ids:
        exchange_object=get_exchange_object2(exchange_id)
        exchange_name = exchange_object.name
        exchange_map[exchange_id] = exchange_name
    return exchange_map

def add_exchange_count2(df, exchange_map):
    # Create a new DataFrame to store the results
    result_df = pd.DataFrame(columns=['trading_pair', 'exchange_count'])

    # Define a dictionary to map exchange ids to exchange names

    # Iterate over each row in the input DataFrame
    for index, row in df.iterrows():
        # Get the trading pair and the list of exchanges where it is traded
        trading_pair = index
        exchanges = [col for col in df.columns if row[col] != '']

        # Map exchange ids to exchange names
        exchanges = [exchange_map.get(exchange, exchange) for exchange in exchanges]

        # Combine exchange names for the same exchange
        unique_exchanges = []
        for exchange in exchanges:
            is_subexchange = False
            for other_exchange in exchanges:
                if exchange != other_exchange and exchange in other_exchange:
                    is_subexchange = True
                    break
            if not is_subexchange:
                unique_exchanges.append(exchange)

        # Count the number of exchanges where the trading pair is traded
        exchange_count = len(unique_exchanges)

        # Add a new row to the result DataFrame
        result_df.loc[len(result_df)] = [trading_pair, exchange_count]

    # Set the trading_pair column as the index of the result DataFrame
    result_df.set_index('trading_pair', inplace=True)

    return result_df

def drop_table(table_name, engine):
    conn = engine.connect()
    query = text(f'''DROP TABLE IF EXISTS "{table_name}"''')
    conn.execute(query)
    conn.close()
def remove_trading_pairs_which_contain_stablecoin_as_base(filtered_pairs,stablecoin_bases_with_slash_list):
    filtered_pairs = [pair for pair in filtered_pairs if
                      not any(pair.startswith(ticker) for ticker in stablecoin_bases_with_slash_list)]
    return filtered_pairs

def get_all_time_high_low_string(df_with_strings_where_each_pair_is_traded):
    for i, row in df_with_strings_where_each_pair_is_traded.iterrows():
        exchanges_where_pair_is_traded = row["exchanges_where_pair_is_traded"]
        all_time_high_str, all_time_low_str = [], []
        for exchange_id in exchanges_where_pair_is_traded.split("_"):
            all_time_high, all_time_low = get_all_time_high_low(exchange_id, row.name)
            all_time_high_str.append(str(all_time_high))
            all_time_low_str.append(str(all_time_low))
        all_time_high_str = "_".join(all_time_high_str)
        all_time_low_str = "_".join(all_time_low_str)
        df_with_strings_where_each_pair_is_traded.loc[i, "string_of_all_aths"] = all_time_high_str
        df_with_strings_where_each_pair_is_traded.loc[i, "string_of_all_atls"] = all_time_low_str
    return df_with_strings_where_each_pair_is_traded
if __name__=="__main__":
    # list_of_shortable_assets_for_binance=get_shortable_assets_for_binance()
    # print("list_of_shortable_assets_for_binance")
    # print(list_of_shortable_assets_for_binance)
    #
    # list_of_shortable_assets_for_huobipro = get_huobi_margin_pairs()
    # print("list_of_shortable_assets_for_huobipro")
    # print(list_of_shortable_assets_for_huobipro)
    #
    # list_of_shortable_assets_for_gateio = get_shortable_assets_for_gateio()
    # print("list_of_shortable_assets_for_gateio")
    # print(list_of_shortable_assets_for_gateio)


    # print("get_market_type('huobipro', 'BTC/USDT')")
    # for exchange_name in ['binance','huobipro','bybit','poloniex',
    #                         'mexc3',
    #                         'bitfinex2','exmo','gateio','kucoin','coinex']:
        # if exchange_name!="hitbtc3":
        #     continue
        # try:
    #         print("exchange_name")
    #         print (exchange_name)
    #         # print(get_asset_type(exchange_name, 'BTC/USDT'))
    #         exchange_object=get_exchange_object(exchange_name)
    #         markets=exchange_object.load_markets()
    #         trading_pair='BTC/USDT'
    #         timeframe='1d'
    #         exchange_object1,limit_of_daily_candles=get_limit_of_daily_candles_original_limits(exchange_name)
    #         print(f"limit_of_daily_candles_for{exchange_name}")
    #         print(limit_of_daily_candles)
    #         # maker_tiered_fees,taker_tiered_fees=get_maker_taker_fees_for_huobi(exchange_object)
    #         # # taker_tiered_fees = get_t(exchange_object)
    #         # print(f"maker_tiered_fees for {exchange_name}")
    #         # print(maker_tiered_fees)
    #         # print(f"taker_tiered_fees for {exchange_name}")
    #         # print(taker_tiered_fees)
    #         list_of_all_symbols_from_exchange = exchange_object.symbols
    # #
    #         for trading_pair in  list_of_all_symbols_from_exchange:
    #             # print("trading_pair")
    #             # print(trading_pair)
    #             if trading_pair!='BTC/USDT':
    #                 continue
    #             # ohlcv_df=\
    #             #     fetch_entire_ohlcv(exchange_object,
    #             #                        exchange_name,
    #             #                        trading_pair,
    #             #                        timeframe,limit_of_daily_candles)
    #             # print("final_ohlcv_df")
    #             # print(ohlcv_df)
    #             asset_type=get_asset_type2(markets,trading_pair)
    #             if asset_type=="spot":
    #
    #                 url=get_exchange_url(exchange_name,exchange_object,trading_pair)
    #                 print(f"url_for_swap for {exchange_name}")
    #                 print(url)
    #     except:
    #         traceback.print_exc()

    # trading_pair="BTC/USDT"
    # timeframe="1d"
    # ohlcv_df=fetch_bybit_ohlcv(trading_pair, timeframe)
    # print("ohlcv_df")
    # print(ohlcv_df)

    #
    # print("get_market_type('huobipro', 'BTC/USDT')")
    # for exchange_name in ['binance', 'huobipro', 'bybit',
    #                       'hitbtc3', 'mexc', 'mexc3', 'bitfinex',
    #                       'bitfinex2', 'exmo', 'gateio', 'kucoin', 'coinex']:
    #
    #     exchange = getattr(ccxt, exchange_name)()
    #     markets=exchange.load_markets()
    #     print(get_asset_type2(markets, 'BTC/USDT'))
    #     print(get_fees(markets, 'BTC/USDT'))
    # maker_fee, taker_fee=get_huobipro_fees("1INCH/USDT:USDT")

    # print(maker_fee)
    # print(taker_fee)
    # ohlcv_df=get_ohlcv_kucoin("1INCH/USDT")
    # print("ohlcv_df")
    # print(ohlcv_df)
    # exchange = ccxt.gateio()
    # ohlcv_data = exchange.fetch_ohlcv('ANKR/USDT', timeframe='1d')
    # print("ohlcv_data for ANKR/USDT")
    # print(ohlcv_data)
    #
    # time.sleep(50000)
    # for exchange_name in ['binance','huobipro','bybit',
    #                         'hitbtc3','mexc','mexc3','bitfinex',
    #                         'bitfinex2','exmo','gateio','kucoin','coinex']:
    #     exchange_object, limit=get_exchange_object_and_limit_of_daily_candles(exchange_name)
    #     exchange_object.load_markets()
    #     # symbol = exchange_object.market(pair)['symbol']
    #     timeframe = '1d'
    #     ohlcv = exchange_object.fetch_ohlcv("BSV/USDT", timeframe)
    #     # ohlcv = get_ohlcv_okex("BTC/USDT")
    #     print(f"ohlcv for {exchange_name}")
    #     print(ohlcv)

    # active_trading_pairs_list=get_active_trading_pairs_from_huobipro()
    # print("active_trading_pairs_list")
    # print(active_trading_pairs_list)
    # for symbol in active_trading_pairs_list:
    #     exchange = ccxt.huobipro()
    #     ohlcv_df=fetch_huobipro_ohlcv(symbol, exchange, timeframe='1d')
    #     trading_pair = symbol.replace("/", "_")
    #
    #     ohlcv_df['ticker'] = symbol
    #     ohlcv_df['exchange'] = "huobipro"
    #
    #     print("ohlcv_df")
    #     print(ohlcv_df)
    # zeros_in_number=count_zeros(9.701e-05)
    # print("zeros_in_number")
    # print(zeros_in_number)
    # get_ohlcv_from_huobi_pro()
    # ohlcv_df=get_huobi_ohlcv()
    # print("ohlcv_df")
    # print(ohlcv_df)
    db_with_trading_pair_statistics="db_with_trading_pair_statistics"
    table_name_where_exchanges_with_all_available_trading_pairs_are="available_trading_pairs_for_each_exchange"
    table_with_strings_where_each_pair_is_traded="exchanges_where_each_pair_is_traded"
    engine_for_db_with_trading_pair_statistics, connection_to_db_with_trading_pair_statistics=\
        connect_to_postgres_db_without_deleting_it_first(db_with_trading_pair_statistics)
    drop_table(table_with_strings_where_each_pair_is_traded,engine_for_db_with_trading_pair_statistics)
    # list_of_all_exchanges=get_all_exchanges()
    # data_dict={}
    # # exchange_map=get_exchange_map_from_exchange_id_to_exchange_name(list_of_all_exchanges)
    # # print("exchange_map")
    # # print(exchange_map)
    # for exchange_name in list_of_all_exchanges:
    #     try:
    #         exchange_object=get_exchange_object2(exchange_name)
    #         list_of_trading_pairs_for_one_exchange=get_trading_pairs(exchange_object)
    #
    #         print(f"list_of_trading_pairs_for_one_exchange for {exchange_name}" )
    #         print(list_of_trading_pairs_for_one_exchange)
    #         print(f"number of all pairs for {exchange_name} is  {len(list_of_trading_pairs_for_one_exchange)}")
    #
    #         filtered_pairs = [pair for pair in list_of_trading_pairs_for_one_exchange if "/USDT" in pair]
    #         print(f"filtered_pairs for {exchange_name}")
    #         print(filtered_pairs)
    #         print(f"number of all usdt pairs for {exchange_name} is  {len(filtered_pairs)}")
    #         stablecoin_bases_with_slash_list=return_list_of_all_stablecoin_bases_with_slash()
    #         filtered_pairs =\
    #             remove_trading_pairs_which_contain_stablecoin_as_base(
    #                 filtered_pairs,
    #                 stablecoin_bases_with_slash_list)
    #         print(filtered_pairs)
    #         filtered_pairs=remove_leveraged_pairs(filtered_pairs)
    #         filtered_pairs=remove_futures_with_expiration_and_options(filtered_pairs)
    #         print(f"number of all usdt pairs without stablecoin base and without levereged tokens "
    #               f"for {exchange_name} is  {len(filtered_pairs)}")
    #         data_dict[exchange_name] = filtered_pairs
    #
    #     except:
    #         traceback.print_exc()
    # df_with_trading_pairs_for_each_exchange = pd.DataFrame.from_dict(data_dict, orient='index')
    # df_with_trading_pairs_for_each_exchange = df_with_trading_pairs_for_each_exchange.transpose()
    # # print("df_with_trading_pairs")
    # # print(df_with_trading_pairs_for_each_exchange.head(200).to_string())
    # # trading_pair="PIAS/USDT"
    # # exchanges_for_trading_pair_list=get_exchanges_for_trading_pair(df_with_trading_pairs_for_each_exchange)
    # # print("exchanges_for_"trading_pair_list")
    # # print(exchanges_for_tra"ding_pair_list)

    #
    # # df_with_strings_where_each_pair_is_traded_plus_exchange_count=\
    # #     add_exchange_count2(df_with_strings_where_each_pair_is_traded, exchange_map)
    #
    # # apply the function to each row and create the new column
    # df_with_strings_where_each_pair_is_traded['unique_exchanges_where_pair_is_traded'] =\
    #     df_with_strings_where_each_pair_is_traded.apply(extract_unique_exchanges, axis=1)
    #
    # df_with_trading_pairs_for_each_exchange.to_sql(table_name_where_exchanges_with_all_available_trading_pairs_are,
    #                engine_for_db_with_trading_pair_statistics,
    #                if_exists='replace')
    df_with_trading_pairs_for_each_exchange = \
        pd.read_sql_query(f'''select * from "{table_name_where_exchanges_with_all_available_trading_pairs_are}"''',
                          engine_for_db_with_trading_pair_statistics)
    print("df_with_trading_pairs_for_each_exchange")
    print(df_with_trading_pairs_for_each_exchange)
    df_with_trading_pairs_for_each_exchange = df_with_trading_pairs_for_each_exchange.drop('index', axis=1)
    df_with_strings_where_each_pair_is_traded = get_exchanges_for_trading_pairs(df_with_trading_pairs_for_each_exchange)
    print("df_with_strings_where_each_pair_is_traded")
    print(df_with_strings_where_each_pair_is_traded)


    # apply the function to each row and create the new column
    df_with_strings_where_each_pair_is_traded['unique_exchanges_where_pair_is_traded'] =\
        df_with_strings_where_each_pair_is_traded.apply(extract_unique_exchanges, axis=1)

    df_with_strings_where_each_pair_is_traded['number_of_exchanges_where_pair_is_traded_on']=\
        df_with_strings_where_each_pair_is_traded['unique_exchanges_where_pair_is_traded'].apply(calculate_number_of_exchanges_where_trading_pair_is_traded_on)




    df_with_strings_where_each_pair_is_traded.to_sql(table_with_strings_where_each_pair_is_traded,
                                                   engine_for_db_with_trading_pair_statistics,
                                                   if_exists='replace')