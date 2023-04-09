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
# from huobi_client.generic import GenericClient
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

def get_spread_at_timestamp(exchange_object, symbol, timestamp):
    # exchange = getattr(ccxt, exchange_name)()
    order_book = exchange_object.fetch_order_book(symbol, timestamp=timestamp)
    bid = order_book['bids'][0][0] if len(order_book['bids']) > 0 else None
    ask = order_book['asks'][0][0] if len(order_book['asks']) > 0 else None
    spread = ask - bid if (bid is not None and ask is not None) else None
    return spread

def get_spread(exchange_instance, symbol):
    # exchange = getattr(ccxt, exchange_id)()
    orderbook = exchange_instance.fetch_order_book(symbol)
    bid = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
    ask = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None
    spread = ask - bid if (bid is not None and ask is not None) else None
    return spread

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
        limit = 10000
    elif exchange_name == 'bitfinex2':
        exchange_object = ccxt.bitfinex2()
        limit = 10000
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
        exchange_object = ccxt.bitfinex()
        limit = 1000
    elif exchange_name == 'bitfinex2':
        exchange_object = ccxt.bitfinex2()
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




def get_exchange_object(exchange_name):
    exchange_objects = {
        'binance': ccxt.binance(),
        'huobipro': ccxt.huobipro(),
        'bybit': ccxt.bybit(),
        'hitbtc3': ccxt.hitbtc3(),
        'mexc': ccxt.mexc(),
        'mexc3': ccxt.mexc3(),
        'bitfinex': ccxt.bitfinex(),
        'bitfinex2': ccxt.bitfinex2(),
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
    for exchange_name in ['binance','huobipro','bybit',
                            'mexc3',
                            'bitfinex2','exmo','gateio','kucoin','coinex']:
        # if exchange_name!="hitbtc3":
        #     continue
        try:
    #         print("exchange_name")
    #         print (exchange_name)
    #         # print(get_asset_type(exchange_name, 'BTC/USDT'))
            exchange_object=get_exchange_object(exchange_name)
            markets=exchange_object.load_markets()
            trading_pair='BTC/USDT'
            timeframe='1d'
            exchange_object1,limit_of_daily_candles=get_limit_of_daily_candles_original_limits(exchange_name)
    #         print(f"limit_of_daily_candles_for{exchange_name}")
    #         print(limit_of_daily_candles)
    #         # maker_tiered_fees,taker_tiered_fees=get_maker_taker_fees_for_huobi(exchange_object)
    #         # # taker_tiered_fees = get_t(exchange_object)
    #         # print(f"maker_tiered_fees for {exchange_name}")
    #         # print(maker_tiered_fees)
    #         # print(f"taker_tiered_fees for {exchange_name}")
    #         # print(taker_tiered_fees)
            list_of_all_symbols_from_exchange = exchange_object.symbols
    #
            for trading_pair in  list_of_all_symbols_from_exchange:
                # print("trading_pair")
                # print(trading_pair)
                if trading_pair!='BTC/USDT':
                    continue
                # ohlcv_df=\
                #     fetch_entire_ohlcv(exchange_object,
                #                        exchange_name,
                #                        trading_pair,
                #                        timeframe,limit_of_daily_candles)
                # print("final_ohlcv_df")
                # print(ohlcv_df)
                # asset_type=get_asset_type2(markets,trading_pair)
                spread=get_spread(exchange_object,trading_pair)
                print(f"spread for {exchange_name}")
                print(spread)
                # timestamp_of_spread=1586333711
                # spread_at_timestamp = get_spread_at_timestamp(exchange_object, trading_pair,timestamp_of_spread)
                # print(f"spread_at_timestamp for {exchange_name}")
                # print(spread_at_timestamp)
        except:
            traceback.print_exc()

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