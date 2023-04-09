def check_volume_compared_to_bitcoin(trading_pair,
                                     min_volume_over_these_many_last_days,
                                     data_df,
                                     min_volume_in_bitcoin,
                                     last_bitcoin_price):
    """
    Checks if the trading pair has enough volume over the specified number of days
    and if the volume is not less than 2 prices of bitcoin for USD pairs or the minimum volume for BTC pairs.

    Args:
        trading_pair (str): The trading pair to check for volume.
        min_volume_over_these_many_last_days (int): The number of days to look back for volume.
        data_df (pandas.DataFrame): The DataFrame containing the trading data.
        min_volume_in_bitcoin (float): The minimum volume in bitcoin to be considered sufficient.
        last_bitcoin_price (float): The last price of bitcoin.

    Returns:
        asset_has_enough_volume (bool): True if the trading pair has enough volume, False otherwise.
    """

    data_df_n_days_slice = data_df.iloc[:-1].tail(min_volume_over_these_many_last_days).copy()
    data_df_n_days_slice["volume_by_close"] = data_df_n_days_slice["volume"] * data_df_n_days_slice["close"]

    min_volume_over_last_n_days_for_usd_pairs = min(data_df_n_days_slice["volume_by_close"])
    min_volume_over_last_n_days_for_btc_pairs = min(data_df_n_days_slice["volume_by_close"])

    asset_has_enough_volume = True

    if "_BTC" not in trading_pair:
        if min_volume_over_last_n_days_for_usd_pairs < min_volume_in_bitcoin * last_bitcoin_price:
            print(f"{trading_pair} discarded due to low volume")
            asset_has_enough_volume = False
    else:
        if min_volume_over_last_n_days_for_btc_pairs < min_volume_in_bitcoin:
            print(f"{trading_pair} discarded due to low volume")
            asset_has_enough_volume = False

    return asset_has_enough_volume
