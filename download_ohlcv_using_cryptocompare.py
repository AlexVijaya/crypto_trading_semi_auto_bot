import requests
import pprint
from api_config import cryptocompare_api
import cryptocompare
def fetch_all_exchanges():
    exchanges_list=cryptocompare.get_exchanges()
    return exchanges_list
def fetch_okex_trading_pairs_from_okex():
    trading_pairs_dict_list = cryptocompare.get_pairs(exchange='okex')
    trading_pairs_list=[]
    for trading_pair_dict in trading_pairs_dict_list:
        # print("trading_pair_dict")
        # print(trading_pair_dict)
        base=trading_pair_dict["exchange_fsym"]
        quote = trading_pair_dict["exchange_tsym"]
        trading_pair=base+"/"+quote
        trading_pairs_list.append(trading_pair)

    return trading_pairs_list
# def fetch_okex_trading_pairs():
#     url = 'https://min-api.cryptocompare.com/data/v3/exchange/symbol'
#     params = {
#         'api_key': cryptocompare_api,
#         'e': 'OKEX'
#     }
#     response = requests.get(url, params=params)
#     # data = response.json()['data']
#     # print(data)
#     pprint.pprint(response.json())
#     trading_pairs = []
#     for pair in data:
#         trading_pairs.append(pair['symbol'])
#     return trading_pairs

if __name__=="__main__":
    trading_pairs_list=fetch_okex_trading_pairs_from_okex()
    all_exchanges_list=fetch_all_exchanges()
    print("trading_pairs_list")
    print(trading_pairs_list)
    print("all_exchanges_list")
    print(all_exchanges_list)