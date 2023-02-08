import ccxt
import pandas as pd


def get_bar_open_times():
    # Initialize empty list to store data
    data = []

    # Get list of all available exchanges
    exchanges = ccxt.exchanges

    # Iterate through each exchange
    for exchange in exchanges:
        try:
            # Initialize the exchange object
            exchange_obj = getattr(ccxt, exchange)()

            # Get the next candle open time for the exchange
            next_bar_time = exchange_obj.milliseconds()

            # Append data to list
            data.append({'exchange': exchange, 'time_when_next_bar_opens': next_bar_time})

        except:
            continue

    # Create DataFrame from data
    df = pd.DataFrame(data)

    # Add a new column for human-readable time
    df['time_when_next_bar_opens_human_readable'] =\
        pd.to_datetime(df['time_when_next_bar_opens'], unit='ms')
    print("df")
    print(df.to_string())
    return df

if __name__=="__main__":
    get_bar_open_times()