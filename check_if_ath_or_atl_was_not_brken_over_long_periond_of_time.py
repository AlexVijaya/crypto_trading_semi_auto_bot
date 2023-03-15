import numpy as np


def check_ath_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                       number_of_days_where_ath_was_not_broken,
                       ath,
                       row_of_last_ath):
    # Calculate the row index to start selecting data from
    start_row_index = max(0, row_of_last_ath - number_of_days_where_ath_was_not_broken)

    # Select the relevant rows from the numpy array
    selected_rows = table_with_ohlcv_data_df_slice_numpy_array[start_row_index:row_of_last_ath + 1]

    # Determine if the high was broken during the selected period
    ath_is_not_broken_for_a_long_time = True
    max_high_over_given_perion = np.max(selected_rows[:, 2])
    if max_high_over_given_perion > ath:
        ath_is_not_broken_for_a_long_time = False

    return ath_is_not_broken_for_a_long_time


def check_atl_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                       number_of_days_where_atl_was_not_broken,
                       atl,
                       row_of_last_atl):
    # Calculate the row index to start selecting data from
    start_row_index = max(0, row_of_last_atl - number_of_days_where_atl_was_not_broken)

    # Select the relevant rows from the numpy array
    selected_rows = table_with_ohlcv_data_df_slice_numpy_array[start_row_index:row_of_last_atl + 1]

    # Determine if the low was broken during the selected period
    atl_is_not_broken_for_a_long_time = True
    min_low_over_given_period = np.min(selected_rows[:, 3])
    if min_low_over_given_period < atl:
        atl_is_not_broken_for_a_long_time = False

    return atl_is_not_broken_for_a_long_time