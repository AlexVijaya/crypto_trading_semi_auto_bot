import traceback

import numpy as np
import pandas as pd
from sqlalchemy import inspect
from sqlalchemy import create_engine
import db_config
from sqlalchemy_utils import create_database,database_exists
from collections import Counter

def drop_duplicates_in_string_in_which_names_are_separated_by_underscores(string):
    unique_items = []
    for item in string.split('_'):
        if item not in unique_items:
            unique_items.append(item)
    return '_'.join(unique_items)

def get_list_of_all_tables_in_0000_ohlcv_df(engine_for_ohlcv_data_for_stocks_0000):
    list_of_tables_in_ohlcv_db_0000 = \
        get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_0000)
    return list_of_tables_in_ohlcv_db_0000

def get_list_of_all_tables_in_1600_ohlcv_df(engine_for_ohlcv_data_for_stocks_1600):
    list_of_tables_in_ohlcv_db_1600 = \
            get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks_1600)
    return list_of_tables_in_ohlcv_db_1600
def get_enginge_for_0000_ohlcv_database(db_where_ohlcv_data_for_stocks_is_stored_0000):
    # db_where_ohlcv_data_for_stocks_is_stored_1600 = "ohlcv_1d_data_for_usdt_pairs_1600"
    engine_for_ohlcv_data_for_stocks_0000 , \
    connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored_0000 )

    # engine_for_ohlcv_data_for_stocks_1600, \
    #     connection_to_ohlcv_data_for_stocks_1600 = \
    #     connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored_1600)
    return engine_for_ohlcv_data_for_stocks_0000

def get_enginge_for_1600_ohlcv_database(db_where_ohlcv_data_for_stocks_is_stored_1600):
    # db_where_ohlcv_data_for_stocks_is_stored_1600 = "ohlcv_1d_data_for_usdt_pairs_1600"
    # engine_for_ohlcv_data_for_stocks_0000 , \
    # connection_to_ohlcv_data_for_stocks = \
    #     connect_to_postgres_db_without_deleting_it_first ( db_where_ohlcv_data_for_stocks_is_stored_0000 )

    engine_for_ohlcv_data_for_stocks_1600, \
        connection_to_ohlcv_data_for_stocks_1600 = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored_1600)
    return engine_for_ohlcv_data_for_stocks_1600

def fill_df_with_info_if_ath_was_broken_on_other_exchanges(stock_name,
                                                           db_where_ohlcv_data_for_stocks_is_stored_0000,
                                                           db_where_ohlcv_data_for_stocks_is_stored_1600,
                                                           table_with_ohlcv_data_df,
                                                           engine_for_ohlcv_data_for_stocks_0000,
                                                           engine_for_ohlcv_data_for_stocks_1600,
                                                           all_time_high_in_stock,
                                                           list_of_tables_in_ohlcv_db_1600,
                                                           levels_formed_by_ath_df,
                                                           row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero):
    ################################################################################
    ######################################################################################
    # we will iterate over each row of this df to understand if ath or ath was broken on a 2 year time period on different exchanges
    df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000 = \
        return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
            db_where_ohlcv_data_for_stocks_is_stored_0000)

    print("df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000")
    print(df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.to_string())
    #########################################################################################################

    ######################################################################################

    # we will iterate over each row of this df to understand if ath or ath was broken on a 2 year time period on different exchanges
    df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600 = \
        return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
            db_where_ohlcv_data_for_stocks_is_stored_1600)

    print("df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600")
    print(df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600.to_string())
    #######################################################################################################

    # get base of trading pair
    base = get_base_of_trading_pair(trading_pair=stock_name)

    # # get base of trading pair
    # exchange_of_pair = get_exchange_of_trading_pair(trading_pair=stock_name)
    # get ohlcv_data_df from different exchanges for one base in trading_pair

    counter_of_number_of_exchanges_where_level_had_been_broken = 0
    string_of_exchanges_where_level_was_broken = ""
    string_of_all_exchanges_where_pair_is_traded = ""
    string_of_exchanges_where_level_was_not_broken = ""

    for col in df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.columns:
        print("column_name")
        print(col)
        if 'table_name' in col:
            ################################
            table_with_ohlcv_data_df = table_with_ohlcv_data_df[
                ["Timestamp", "open", "high", "low", "close", "volume"]]
            table_with_ohlcv_data_df_numpy_array = table_with_ohlcv_data_df.to_numpy()
            # print("table_with_ohlcv_data_df_numpy_array")
            # print(table_with_ohlcv_data_df_numpy_array)
            last_ath_timestamp, last_ath_row_number_in_the_original_table = \
                get_last_ath_timestamp_and_row_number(table_with_ohlcv_data_df_numpy_array,
                                                      all_time_high_in_stock)

            for trading_pair_with_exchange_table_name_in_ohlcv_database in [
                df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.loc[base, col]]:
                if pd.isna(trading_pair_with_exchange_table_name_in_ohlcv_database):
                    print("trading_pair_with_exchange_table_name_in_ohlcv_database is nan")
                    continue
                print("trading_pair_with_exchange_table_name_in_ohlcv_databaseue_of_cell_if_df_it_should_be_table_name")
                print(trading_pair_with_exchange_table_name_in_ohlcv_database)

                table_with_0000_ohlcv_data_df_on_other_exchanges = \
                    pd.read_sql_query(f'''select * from "{trading_pair_with_exchange_table_name_in_ohlcv_database}"''',
                                      engine_for_ohlcv_data_for_stocks_0000)
                print("table_with_ohlcv_data_df_on_other_exchanges1")
                print(table_with_0000_ohlcv_data_df_on_other_exchanges.tail(5).to_string())
                print("trading_pair_with_exchange_table_name_in_ohlcv_database1")
                print(trading_pair_with_exchange_table_name_in_ohlcv_database)

                exchange_of_pair = get_exchange_of_trading_pair(
                    trading_pair=trading_pair_with_exchange_table_name_in_ohlcv_database)
                print("exchange_of_pair")
                print(exchange_of_pair)

                row_number_in_ohlcv_table_on_other_exchanges = \
                    get_row_number_when_timestamp_is_not_index(table_with_0000_ohlcv_data_df_on_other_exchanges,
                                                               last_ath_timestamp)
                print("row_number_in_ohlcv_table_on_other_exchanges")
                print(row_number_in_ohlcv_table_on_other_exchanges)
                table_with_0000_ohlcv_data_df_on_other_exchanges = table_with_0000_ohlcv_data_df_on_other_exchanges[
                    ["Timestamp", "open", "high", "low", "close", "volume"]]
                table_with_ohlcv_data_df_on_other_exchanges_numpy_array = table_with_0000_ohlcv_data_df_on_other_exchanges.to_numpy()
                high_on_another_exchange = find_high_for_timestamp(last_ath_timestamp,
                                                                   table_with_ohlcv_data_df_on_other_exchanges_numpy_array)
                number_of_days_where_ath_was_not_broken = 2 * 366
                ath_is_not_broken_for_a_long_time = check_ath_breakout(
                    table_with_ohlcv_data_df_on_other_exchanges_numpy_array,
                    number_of_days_where_ath_was_not_broken,
                    high_on_another_exchange,
                    row_number_in_ohlcv_table_on_other_exchanges)
                print(f"ath for {base} is not broken = {ath_is_not_broken_for_a_long_time}")

                string_of_all_exchanges_where_pair_is_traded = string_of_all_exchanges_where_pair_is_traded + "_" + exchange_of_pair
                string_of_all_exchanges_where_pair_is_traded = remove_first_underscore(
                    string_of_all_exchanges_where_pair_is_traded)
                if ath_is_not_broken_for_a_long_time == False:
                    counter_of_number_of_exchanges_where_level_had_been_broken = \
                        counter_of_number_of_exchanges_where_level_had_been_broken + 1
                    string_of_exchanges_where_level_was_broken = string_of_exchanges_where_level_was_broken + "_" + exchange_of_pair
                    string_of_exchanges_where_level_was_broken = remove_first_underscore(
                        string_of_exchanges_where_level_was_broken)
                else:
                    string_of_exchanges_where_level_was_not_broken = string_of_exchanges_where_level_was_not_broken + "_" + exchange_of_pair
                    string_of_exchanges_where_level_was_not_broken = remove_first_underscore(
                        string_of_exchanges_where_level_was_not_broken)

                # check if pair with the same base is traded on huobi and other 1600 exchanges
                if base in df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600.index:
                    print(f"base = {base} is on 1600 exchange")
                    tables_which_start_with_base_in_1600_ohlcv_db = [table for table in list_of_tables_in_ohlcv_db_1600
                                                                     if table.startswith(f'{base}_')]
                    for table_which_start_with_base_in_1600_ohlcv_db in tables_which_start_with_base_in_1600_ohlcv_db:
                        print("table_which_start_with_base_in_1600_ohlcv_db")
                        print(table_which_start_with_base_in_1600_ohlcv_db)
                        table_with_1600_ohlcv_data_df_on_other_exchanges = \
                            pd.read_sql_query(
                                f'''select * from "{table_which_start_with_base_in_1600_ohlcv_db}"''',
                                engine_for_ohlcv_data_for_stocks_1600)
                        table_with_1600_ohlcv_data_df_on_other_exchanges = \
                        table_with_1600_ohlcv_data_df_on_other_exchanges[
                            ["Timestamp", "open", "high", "low", "close", "volume"]]
                        print("table_with_1600_ohlcv_data_df_on_other_exchanges")
                        print(table_with_1600_ohlcv_data_df_on_other_exchanges)
                        closest_timestamp, high_corresponding_to_closest_timestamp, closest_timestamp_plus_one_day, high_plus_one_day = \
                            find_closest_timestamp_high_high_plus_one_day_using_index(
                                table_with_1600_ohlcv_data_df_on_other_exchanges, last_ath_timestamp)
                        max_high_on_1600_exchange = max(high_corresponding_to_closest_timestamp, high_plus_one_day)
                        print("high_corresponding_to_closest_timestamp")
                        print(high_corresponding_to_closest_timestamp)
                        print("high_plus_one_day")
                        print(high_plus_one_day)

                        timestamp_of_possible_ath_on_1600_exchange = np.nan
                        if max_high_on_1600_exchange == high_corresponding_to_closest_timestamp:
                            timestamp_of_possible_ath_on_1600_exchange = closest_timestamp
                        else:
                            timestamp_of_possible_ath_on_1600_exchange = closest_timestamp_plus_one_day
                        print("max_high_on_1600_exchange")
                        print(max_high_on_1600_exchange)
                        row_number_of_possible_ath_on_1600_exchange = \
                            get_row_number_when_timestamp_is_not_index(table_with_1600_ohlcv_data_df_on_other_exchanges,
                                                                       timestamp_of_possible_ath_on_1600_exchange)
                        table_with_ohlcv_data_df_on_other_exchanges_numpy_array_on_1600_exchange = \
                            table_with_1600_ohlcv_data_df_on_other_exchanges.to_numpy()
                        ath_is_not_broken_for_a_long_time_on_1600_exchange_ = check_ath_breakout(
                            table_with_ohlcv_data_df_on_other_exchanges_numpy_array_on_1600_exchange,
                            number_of_days_where_ath_was_not_broken,
                            max_high_on_1600_exchange,
                            row_number_of_possible_ath_on_1600_exchange)
                        exchange_of_pair_for_1600_exchange = get_exchange_of_trading_pair(
                            trading_pair=table_which_start_with_base_in_1600_ohlcv_db)
                        print("exchange_of_pair_for_1600_exchange")
                        print(exchange_of_pair_for_1600_exchange)
                        string_of_all_exchanges_where_pair_is_traded = string_of_all_exchanges_where_pair_is_traded + "_" + exchange_of_pair_for_1600_exchange
                        string_of_all_exchanges_where_pair_is_traded = remove_first_underscore(
                            string_of_all_exchanges_where_pair_is_traded)
                        if ath_is_not_broken_for_a_long_time_on_1600_exchange_ == False:
                            counter_of_number_of_exchanges_where_level_had_been_broken = \
                                counter_of_number_of_exchanges_where_level_had_been_broken + 1
                            string_of_exchanges_where_level_was_broken = string_of_exchanges_where_level_was_broken + "_" + exchange_of_pair_for_1600_exchange
                            string_of_exchanges_where_level_was_broken = remove_first_underscore(
                                string_of_exchanges_where_level_was_broken)
                        else:
                            string_of_exchanges_where_level_was_not_broken = string_of_exchanges_where_level_was_not_broken + "_" + exchange_of_pair_for_1600_exchange
                            string_of_exchanges_where_level_was_not_broken = remove_first_underscore(
                                string_of_exchanges_where_level_was_not_broken)

    try:
        string_of_exchanges_where_level_was_broken = \
            drop_duplicates_in_string_in_which_names_are_separated_by_underscores(
                string_of_exchanges_where_level_was_broken)
        string_of_exchanges_where_level_was_not_broken = \
            drop_duplicates_in_string_in_which_names_are_separated_by_underscores(
                string_of_exchanges_where_level_was_not_broken)
        string_of_all_exchanges_where_pair_is_traded = \
            drop_duplicates_in_string_in_which_names_are_separated_by_underscores(
                string_of_all_exchanges_where_pair_is_traded)
    except:
        traceback.print_exc()

    levels_formed_by_ath_df.at[
        row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "number_of_exchanges_where_level_had_been_broken"] = counter_of_number_of_exchanges_where_level_had_been_broken
    levels_formed_by_ath_df.at[
        row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_exchanges_where_level_was_broken"] = string_of_exchanges_where_level_was_broken
    levels_formed_by_ath_df.at[
        row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_exchanges_where_level_was_not_broken"] = string_of_exchanges_where_level_was_not_broken
    levels_formed_by_ath_df.at[
        row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_all_exchanges_where_pair_is_traded"] = string_of_all_exchanges_where_pair_is_traded

    return levels_formed_by_ath_df

def fill_df_with_info_if_atl_was_broken_on_other_exchanges(stock_name,
                                                           db_where_ohlcv_data_for_stocks_is_stored_0000,
                                                           db_where_ohlcv_data_for_stocks_is_stored_1600,
                                                           table_with_ohlcv_data_df,
                                                           engine_for_ohlcv_data_for_stocks_0000,
                                                           engine_for_ohlcv_data_for_stocks_1600,
                                                           all_time_low_in_stock,
                                                           list_of_tables_in_ohlcv_db_1600,
                                                           levels_formed_by_atl_df,
                                                           row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero):
    # we will iterate over each row of this df to understand if ath or atl was broken on a 2 year time period on different exchanges
    df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000 = \
        return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
            db_where_ohlcv_data_for_stocks_is_stored_0000)

    print("df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000")
    print(df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.to_string())
    #########################################################################################################

    ######################################################################################

    # we will iterate over each row of this df to understand if ath or atl was broken on a 2 year time period on different exchanges
    df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600 = \
        return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
            db_where_ohlcv_data_for_stocks_is_stored_1600)

    print("df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600")
    print(df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600.to_string())
    #######################################################################################################

    # get base of trading pair
    base = get_base_of_trading_pair(trading_pair=stock_name)

    # # get base of trading pair
    # exchange_of_pair = get_exchange_of_trading_pair(trading_pair=stock_name)
    # get ohlcv_data_df from different exchanges for one base in trading_pair

    counter_of_number_of_exchanges_where_level_had_been_broken = 0
    string_of_exchanges_where_level_was_broken = ""
    string_of_all_exchanges_where_pair_is_traded = ""
    string_of_exchanges_where_level_was_not_broken = ""

    for col in df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.columns:
        print("column_name")
        print(col)
        if 'table_name' in col:
            ################################
            table_with_ohlcv_data_df = table_with_ohlcv_data_df[
                ["Timestamp", "open", "high", "low", "close", "volume"]]
            table_with_ohlcv_data_df_numpy_array = table_with_ohlcv_data_df.to_numpy()
            # print("table_with_ohlcv_data_df_numpy_array")
            # print(table_with_ohlcv_data_df_numpy_array)
            last_atl_timestamp, last_atl_row_number_in_the_original_table = \
                get_last_atl_timestamp_and_row_number(table_with_ohlcv_data_df_numpy_array,
                                                      all_time_low_in_stock)

            for trading_pair_with_exchange_table_name_in_ohlcv_database in [
                df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_0000.loc[base, col]]:
                if pd.isna(trading_pair_with_exchange_table_name_in_ohlcv_database):
                    print("trading_pair_with_exchange_table_name_in_ohlcv_database is nan")
                    continue
                print("trading_pair_with_exchange_table_name_in_ohlcv_databaseue_of_cell_if_df_it_should_be_table_name")
                print(trading_pair_with_exchange_table_name_in_ohlcv_database)

                table_with_0000_ohlcv_data_df_on_other_exchanges = \
                    pd.read_sql_query(f'''select * from "{trading_pair_with_exchange_table_name_in_ohlcv_database}"''',
                                      engine_for_ohlcv_data_for_stocks_0000)
                print("table_with_ohlcv_data_df_on_other_exchanges1")
                print(table_with_0000_ohlcv_data_df_on_other_exchanges.tail(5).to_string())
                print("trading_pair_with_exchange_table_name_in_ohlcv_database1")
                print(trading_pair_with_exchange_table_name_in_ohlcv_database)

                exchange_of_pair = get_exchange_of_trading_pair(
                    trading_pair=trading_pair_with_exchange_table_name_in_ohlcv_database)
                print("exchange_of_pair")
                print(exchange_of_pair)

                row_number_in_ohlcv_table_on_other_exchanges = \
                    get_row_number_when_timestamp_is_not_index(table_with_0000_ohlcv_data_df_on_other_exchanges,
                                                               last_atl_timestamp)
                print("row_number_in_ohlcv_table_on_other_exchanges")
                print(row_number_in_ohlcv_table_on_other_exchanges)
                table_with_0000_ohlcv_data_df_on_other_exchanges = table_with_0000_ohlcv_data_df_on_other_exchanges[
                    ["Timestamp", "open", "high", "low", "close", "volume"]]
                table_with_ohlcv_data_df_on_other_exchanges_numpy_array = table_with_0000_ohlcv_data_df_on_other_exchanges.to_numpy()
                low_on_another_exchange = find_low_for_timestamp(last_atl_timestamp,
                                                                 table_with_ohlcv_data_df_on_other_exchanges_numpy_array)
                number_of_days_where_atl_was_not_broken = 2 * 366
                atl_is_not_broken_for_a_long_time = check_atl_breakout(
                    table_with_ohlcv_data_df_on_other_exchanges_numpy_array,
                    number_of_days_where_atl_was_not_broken,
                    low_on_another_exchange,
                    row_number_in_ohlcv_table_on_other_exchanges)
                print(f"atl for {base} is not broken = {atl_is_not_broken_for_a_long_time}")

                string_of_all_exchanges_where_pair_is_traded = string_of_all_exchanges_where_pair_is_traded + "_" + exchange_of_pair
                string_of_all_exchanges_where_pair_is_traded = remove_first_underscore(
                    string_of_all_exchanges_where_pair_is_traded)
                if atl_is_not_broken_for_a_long_time == False:
                    counter_of_number_of_exchanges_where_level_had_been_broken = \
                        counter_of_number_of_exchanges_where_level_had_been_broken + 1
                    string_of_exchanges_where_level_was_broken = string_of_exchanges_where_level_was_broken + "_" + exchange_of_pair
                    string_of_exchanges_where_level_was_broken = remove_first_underscore(
                        string_of_exchanges_where_level_was_broken)
                else:
                    string_of_exchanges_where_level_was_not_broken = string_of_exchanges_where_level_was_not_broken + "_" + exchange_of_pair
                    string_of_exchanges_where_level_was_not_broken = remove_first_underscore(
                        string_of_exchanges_where_level_was_not_broken)

                # check if pair with the same base is traded on huobi and other 1600 exchanges
                if base in df_with_table_names_rows_as_base_of_crypto_and_table_number_as_column_names_1600.index:
                    print(f"base = {base} is on huobi")
                    tables_which_start_with_base_in_1600_ohlcv_db = [table for table in list_of_tables_in_ohlcv_db_1600
                                                                     if table.startswith(f'{base}_')]
                    for table_which_start_with_base_in_1600_ohlcv_db in tables_which_start_with_base_in_1600_ohlcv_db:
                        print("table_which_start_with_base_in_1600_ohlcv_db")
                        print(table_which_start_with_base_in_1600_ohlcv_db)
                        table_with_1600_ohlcv_data_df_on_other_exchanges = \
                            pd.read_sql_query(
                                f'''select * from "{table_which_start_with_base_in_1600_ohlcv_db}"''',
                                engine_for_ohlcv_data_for_stocks_1600)
                        table_with_1600_ohlcv_data_df_on_other_exchanges = \
                        table_with_1600_ohlcv_data_df_on_other_exchanges[
                            ["Timestamp", "open", "high", "low", "close", "volume"]]
                        print("table_with_1600_ohlcv_data_df_on_other_exchanges")
                        print(table_with_1600_ohlcv_data_df_on_other_exchanges)
                        closest_timestamp, low_corresponding_to_closest_timestamp, closest_timestamp_plus_one_day, low_plus_one_day = \
                            find_closest_timestamp_low_low_plus_one_day_using_index(
                                table_with_1600_ohlcv_data_df_on_other_exchanges, last_atl_timestamp)
                        min_low_on_1600_exchange = min(low_corresponding_to_closest_timestamp, low_plus_one_day)
                        print("low_corresponding_to_closest_timestamp")
                        print(low_corresponding_to_closest_timestamp)
                        print("low_plus_one_day")
                        print(low_plus_one_day)

                        timestamp_of_possible_atl_on_1600_exchange = np.nan
                        if min_low_on_1600_exchange == low_corresponding_to_closest_timestamp:
                            timestamp_of_possible_atl_on_1600_exchange = closest_timestamp
                        else:
                            timestamp_of_possible_atl_on_1600_exchange = closest_timestamp_plus_one_day
                        print("min_low_on_1600_exchange")
                        print(min_low_on_1600_exchange)
                        row_number_of_possible_atl_on_1600_exchange = \
                            get_row_number_when_timestamp_is_not_index(table_with_1600_ohlcv_data_df_on_other_exchanges,
                                                                       timestamp_of_possible_atl_on_1600_exchange)
                        table_with_ohlcv_data_df_on_other_exchanges_numpy_array_on_1600_exchange = \
                            table_with_1600_ohlcv_data_df_on_other_exchanges.to_numpy()
                        atl_is_not_broken_for_a_long_time_on_1600_exchange_ = check_atl_breakout(
                            table_with_ohlcv_data_df_on_other_exchanges_numpy_array_on_1600_exchange,
                            number_of_days_where_atl_was_not_broken,
                            min_low_on_1600_exchange,
                            row_number_of_possible_atl_on_1600_exchange)
                        exchange_of_pair_for_1600_exchange = get_exchange_of_trading_pair(
                            trading_pair=table_which_start_with_base_in_1600_ohlcv_db)
                        print("exchange_of_pair_for_1600_exchange")
                        print(exchange_of_pair_for_1600_exchange)
                        string_of_all_exchanges_where_pair_is_traded = string_of_all_exchanges_where_pair_is_traded + "_" + exchange_of_pair_for_1600_exchange
                        string_of_all_exchanges_where_pair_is_traded = remove_first_underscore(
                            string_of_all_exchanges_where_pair_is_traded)
                        if atl_is_not_broken_for_a_long_time_on_1600_exchange_ == False:
                            counter_of_number_of_exchanges_where_level_had_been_broken = \
                                counter_of_number_of_exchanges_where_level_had_been_broken + 1
                            string_of_exchanges_where_level_was_broken = string_of_exchanges_where_level_was_broken + "_" + exchange_of_pair_for_1600_exchange
                            string_of_exchanges_where_level_was_broken = remove_first_underscore(
                                string_of_exchanges_where_level_was_broken)
                        else:
                            string_of_exchanges_where_level_was_not_broken = string_of_exchanges_where_level_was_not_broken + "_" + exchange_of_pair_for_1600_exchange
                            string_of_exchanges_where_level_was_not_broken = remove_first_underscore(
                                string_of_exchanges_where_level_was_not_broken)

    try:
        string_of_exchanges_where_level_was_broken=\
            drop_duplicates_in_string_in_which_names_are_separated_by_underscores(string_of_exchanges_where_level_was_broken)
        string_of_exchanges_where_level_was_not_broken=\
            drop_duplicates_in_string_in_which_names_are_separated_by_underscores(string_of_exchanges_where_level_was_not_broken)
        string_of_all_exchanges_where_pair_is_traded=\
            drop_duplicates_in_string_in_which_names_are_separated_by_underscores(string_of_all_exchanges_where_pair_is_traded)
    except:
        traceback.print_exc()

    levels_formed_by_atl_df.at[
        row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "number_of_exchanges_where_level_had_been_broken"] = counter_of_number_of_exchanges_where_level_had_been_broken
    levels_formed_by_atl_df.at[
        row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_exchanges_where_level_was_broken"] = string_of_exchanges_where_level_was_broken
    levels_formed_by_atl_df.at[
        row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_exchanges_where_level_was_not_broken"] = string_of_exchanges_where_level_was_not_broken
    levels_formed_by_atl_df.at[
        row_index_where_to_put_string_it_can_be_counter_minus_one_or_zero, "string_of_all_exchanges_where_pair_is_traded"] = string_of_all_exchanges_where_pair_is_traded

    return levels_formed_by_atl_df


def get_row_number_when_timestamp_is_not_index(table_with_ohlcv_data_df_on_other_exchanges, atl_or_ath_timestamp):
    """
    Returns the row number of the row in which the column "Timestamp" equals to atl_timestamp.
    """
    print("inner_atl_of_ath_timestamp")
    print(atl_or_ath_timestamp)
    print("inner_table_with_ohlcv_data_df_on_other_exchanges")
    print(table_with_ohlcv_data_df_on_other_exchanges.tail(10).to_string())
    print("table_with_ohlcv_data_df_on_other_exchanges.index[table_with_ohlcv_data_df_on_other_exchanges['Timestamp'] == atl_or_ath_timestamp]")
    print(table_with_ohlcv_data_df_on_other_exchanges.index[
        table_with_ohlcv_data_df_on_other_exchanges['Timestamp'] == atl_or_ath_timestamp].tolist())
    # find the row number where "Timestamp" equals atl_timestamp
    row_number = table_with_ohlcv_data_df_on_other_exchanges.index[
        table_with_ohlcv_data_df_on_other_exchanges['Timestamp'] == atl_or_ath_timestamp].tolist()[0]

    return row_number


def get_row_number_when_timestamp_is_index(table_with_ohlcv_data_df_on_other_exchanges, atl_or_ath_timestamp):
    """
    Returns the row number of the row in which the index "Timestamp" equals to atl_or_ath_timestamp.
    """
    # find the row number where the index equals atl_or_ath_timestamp
    row_number = table_with_ohlcv_data_df_on_other_exchanges.index.get_loc(atl_or_ath_timestamp)

    return row_number
def get_last_atl_timestamp_and_row_number(table_with_ohlcv_data_df_slice_numpy_array, ATL):
    # Find the rows where the low equals the ATL
    atl_rows = np.where(table_with_ohlcv_data_df_slice_numpy_array[:, 3] == ATL)[0]
    print("np.where(table_with_ohlcv_data_df_slice_numpy_array[:, 3] == ATL)")
    print(np.where(table_with_ohlcv_data_df_slice_numpy_array[:, 3] == ATL))

    if len(atl_rows) > 0:
        # Get the timestamp of the last row where the low equals the ATL
        last_atl_timestamp = table_with_ohlcv_data_df_slice_numpy_array[atl_rows[-1], 0]

        # Get the row number of the last ATL row
        last_atl_row_number = atl_rows[-1]

        return last_atl_timestamp, last_atl_row_number
    else:
        return None

def find_high_for_timestamp(timestamp_of_ath, table_with_ohlcv_data_df_numpy_array):
    timestamp_column = table_with_ohlcv_data_df_numpy_array[:, 0]
    high_column = table_with_ohlcv_data_df_numpy_array[:, 2]
    index = np.where(timestamp_column == timestamp_of_ath)[0]
    if len(index) > 0:
        high_that_might_be_ath = high_column[index[0]]
        return high_that_might_be_ath
    else:
        return None

def find_low_for_timestamp(timestamp_of_atl, table_with_ohlcv_data_df_numpy_array):
    timestamp_column = table_with_ohlcv_data_df_numpy_array[:, 0]
    low_column = table_with_ohlcv_data_df_numpy_array[:, 3]
    index = np.where(timestamp_column == timestamp_of_atl)[0]
    if len(index) > 0:
        low_that_might_be_atl = low_column[index[0]]
        return low_that_might_be_atl
    else:
        return None


def get_last_ath_timestamp_and_row_number(table_with_ohlcv_data_df_slice_numpy_array, ATH):
    # Find the rows where the high equals the ATH
    ath_rows = np.where(table_with_ohlcv_data_df_slice_numpy_array[:, 2] == ATH)[0]

    if len(ath_rows) > 0:
        # Get the timestamp of the last row where the high equals the ATH
        last_ath_timestamp = table_with_ohlcv_data_df_slice_numpy_array[ath_rows[-1], 0]

        # Get the row number of the last ATH row
        last_ath_row_number = ath_rows[-1]

        return last_ath_timestamp, last_ath_row_number
    else:
        return None


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

def get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks):
    '''get list of all tables in db which is given as parameter'''
    inspector=inspect(engine_for_ohlcv_data_for_stocks)
    list_of_tables_in_db=inspector.get_table_names()

    return list_of_tables_in_db
def check_ath_breakout(table_with_ohlcv_data_df_slice_numpy_array,
                       number_of_days_where_ath_was_not_broken,
                       ath,
                       row_of_last_ath):
    # Calculate the row index to start selecting data from
    start_row_index = max(0, row_of_last_ath - number_of_days_where_ath_was_not_broken)
    # print("start_row_index")
    # print(start_row_index)

    # Select the relevant rows from the numpy array
    selected_rows = table_with_ohlcv_data_df_slice_numpy_array[start_row_index:row_of_last_ath + 1]
    # print("selected_rows")
    # print(selected_rows)

    # Determine if the high was broken during the selected period
    ath_is_not_broken_for_a_long_time = True
    max_high_over_given_perion = np.max(selected_rows[:, 2])
    # print("max_high_over_given_perion_when_true")
    # print(max_high_over_given_perion)
    if max_high_over_given_perion > ath:
        # print("max_high_over_given_perion_when_false")
        # print(max_high_over_given_perion)
        ath_is_not_broken_for_a_long_time = False

    return ath_is_not_broken_for_a_long_time


def find_closest_timestamp_high_low_closest_timestamp_high_low_plus_one_day(df, last_atl_timestamp):
    # # Convert the last_atl_timestamp to a pandas Timestamp object
    # last_atl_timestamp = pd.Timestamp(last_atl_timestamp)

    # Find the Timestamp in the DataFrame that is closest to last_atl_timestamp
    closest_timestamp = df['Timestamp'].iloc[(df['Timestamp'] - last_atl_timestamp).abs().argsort()[0]]

    # Find the corresponding low and high values
    closest_row = df.loc[df['Timestamp'] == closest_timestamp]
    low = closest_row['low'].values[0]
    high = closest_row['high'].values[0]

    # Find the next timestamp in the DataFrame
    closest_timestamp_plus_one_day = df['Timestamp'].iloc[
        (df['Timestamp'] - closest_timestamp - pd.Timedelta(days=1)).abs().argsort()[0]]

    # Find the corresponding low and high values for the next timestamp
    closest_row_plus_one_day = df.loc[df['Timestamp'] == closest_timestamp_plus_one_day]
    low_plus_one_day = closest_row_plus_one_day['low'].values[0]
    high_plus_one_day = closest_row_plus_one_day['high'].values[0]

    return closest_timestamp, low, high, closest_timestamp_plus_one_day, low_plus_one_day, high_plus_one_day


def find_closest_timestamp_high_closest_timestamp_plus_one_day_high_plus_one_day(df, last_ath_timestamp):
    # # Convert the last_ath_timestamp to a pandas Timestamp object
    # last_ath_timestamp = pd.Timestamp(last_ath_timestamp)

    # Find the Timestamp in the DataFrame that is closest to last_ath_timestamp
    closest_timestamp = df['Timestamp'].iloc[(df['Timestamp'] - last_ath_timestamp).abs().argsort()[0]]

    # Find the corresponding high value
    closest_row = df.loc[df['Timestamp'] == closest_timestamp]
    high = closest_row['high'].values[0]

    # Find the next timestamp in the DataFrame
    closest_timestamp_plus_one_day = df['Timestamp'].iloc[
        (df['Timestamp'] - closest_timestamp - pd.Timedelta(days=1)).abs().argsort()[0]]

    # Find the corresponding high value for the next timestamp
    closest_row_plus_one_day = df.loc[df['Timestamp'] == closest_timestamp_plus_one_day]
    high_plus_one_day = closest_row_plus_one_day['high'].values[0]

    return closest_timestamp, high, closest_timestamp_plus_one_day, high_plus_one_day


def find_closest_timestamp_low_closest_timestamp_plus_one_day_low_plus_one_day(df, last_atl_timestamp):
    # # Convert the last_atl_timestamp to a pandas Timestamp object
    # last_atl_timestamp = pd.Timestamp(last_atl_timestamp)

    # Find the Timestamp in the DataFrame that is closest to last_atl_timestamp
    closest_timestamp = df['Timestamp'].iloc[(df['Timestamp'] - last_atl_timestamp).abs().argsort()[0]]

    # Find the corresponding low value
    closest_row = df.loc[df['Timestamp'] == closest_timestamp]
    low = closest_row['low'].values[0]

    # Find the next timestamp in the DataFrame
    closest_timestamp_plus_one_day = df['Timestamp'].iloc[
        (df['Timestamp'] - closest_timestamp - pd.Timedelta(days=1)).abs().argsort()[0]]

    # Find the corresponding low value for the next timestamp
    closest_row_plus_one_day = df.loc[df['Timestamp'] == closest_timestamp_plus_one_day]
    low_plus_one_day = closest_row_plus_one_day['low'].values[0]

    return closest_timestamp, low, closest_timestamp_plus_one_day, low_plus_one_day


def find_closest_timestamp_high_high_plus_one_day_using_index(df, last_ath_timestamp):
    # # Convert the last_ath_timestamp to a pandas Timestamp object
    # last_ath_timestamp = pd.Timestamp(last_ath_timestamp)

    # Find the Timestamp in the DataFrame that is closest to last_ath_timestamp
    closest_timestamp = df['Timestamp'].iloc[(df['Timestamp'] - last_ath_timestamp).abs().argsort()[0]]

    # Find the index of the closest Timestamp in the DataFrame
    closest_index = df.index[df['Timestamp'] == closest_timestamp][0]

    # Find the corresponding high value
    high = df.loc[closest_index, 'high']

    # Find the Timestamp and high value for the next row in the DataFrame
    closest_timestamp_plus_one_day=np.nan
    high_plus_one_day=np.nan
    try:
        closest_timestamp_plus_one_day = df.loc[closest_index + 1, 'Timestamp']
    except:
        traceback.print_exc()
    try:
        high_plus_one_day = df.loc[closest_index + 1, 'high']
    except:
        traceback.print_exc()

    return closest_timestamp, high, closest_timestamp_plus_one_day, high_plus_one_day


def find_closest_timestamp_low_low_plus_one_day_using_index(df, last_atl_timestamp):
    # # Convert the last_atl_timestamp to a pandas Timestamp object
    # last_atl_timestamp = pd.Timestamp(last_atl_timestamp)

    # Find the Timestamp in the DataFrame that is closest to last_atl_timestamp
    closest_timestamp = df['Timestamp'].iloc[(df['Timestamp'] - last_atl_timestamp).abs().argsort()[0]]

    # Find the index of the closest Timestamp in the DataFrame
    closest_index = df.index[df['Timestamp'] == closest_timestamp][0]

    # Find the corresponding low value
    low = df.loc[closest_index, 'low']

    # Find the Timestamp and low value for the next row in the DataFrame
    closest_timestamp_plus_one_day=np.nan
    low_plus_one_day=np.nan
    try:
        closest_timestamp_plus_one_day = df.loc[closest_index + 1, 'Timestamp']
    except:
        traceback.print_exc()
    try:
        print("len(df)")
        print(len(df))
        low_plus_one_day = df.loc[closest_index + 1, 'low']
    except:
        traceback.print_exc()

    return closest_timestamp, low, closest_timestamp_plus_one_day, low_plus_one_day


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

def return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(db_where_ohlcv_data_for_stocks_is_stored):

    engine_for_ohlcv_data_for_stocks, \
        connection_to_ohlcv_data_for_stocks = \
        connect_to_postgres_db_without_deleting_it_first(db_where_ohlcv_data_for_stocks_is_stored)
    list_of_tables_in_ohlcv_db = get_list_of_tables_in_db(engine_for_ohlcv_data_for_stocks)
    # print("list_of_tables_in_ohlcv_db")
    # print(list_of_tables_in_ohlcv_db)

    # iterate over the list of table names
    base_list = []
    for table_name in list_of_tables_in_ohlcv_db:

        exchange = table_name.split("_on_")[1]
        trading_pair = table_name.split("_on_")[0]
        base = trading_pair.split("_")[0]
        quote = trading_pair.split("_")[1]
        base_list.append(base)

    # count the occurrences of each value in the list
    counted_values = Counter(base_list)
    # get the maximum count of any value in the list
    max_count = max(counted_values.values())

    #drop duplicates in base_list
    base_list=list(set(base_list))


    # create a dictionary of column names and empty lists
    columns = [f'{i}_table_name' for i in range(1, max_count + 1)]
    data_frame_with_columns_as_base = pd.DataFrame(index=base_list, columns=columns)

    for counter,base in enumerate(base_list):
        # print(f"counter = {counter}")

        new_list = [value for value in list_of_tables_in_ohlcv_db if value.startswith(base + "_")]
        list_without_nans=new_list.copy()
        new_list.extend([None] * (len(data_frame_with_columns_as_base.columns) - len(new_list)))

        data_frame_with_columns_as_base.loc[base] = new_list
        data_frame_with_columns_as_base.loc[base,"number_of_tables"] = len(list_without_nans)
        # data_frame_with_columns_as_base['number_of_tables'] = data_frame_with_columns_as_base['number_of_tables'].astype(int)
        # print("new_list")
        # print(new_list)

    # print("data_frame_with_columns_as_base")
    # print(data_frame_with_columns_as_base.to_string())
    # print("len(data_frame_with_columns_as_base)")
    # print(len(data_frame_with_columns_as_base))
    return data_frame_with_columns_as_base

def get_base_of_trading_pair(trading_pair):
    exchange = trading_pair.split("_on_")[1]
    trading_pair = trading_pair.split("_on_")[0]
    base = trading_pair.split("_")[0]
    quote = trading_pair.split("_")[1]
    return base

def get_exchange_of_trading_pair(trading_pair):
    exchange = trading_pair.split("_on_")[1]
    trading_pair = trading_pair.split("_on_")[0]
    base = trading_pair.split("_")[0]
    quote = trading_pair.split("_")[1]
    return exchange

def get_quote_of_trading_pair(trading_pair):
    exchange = trading_pair.split("_on_")[1]
    trading_pair = trading_pair.split("_on_")[0]
    base = trading_pair.split("_")[0]
    quote = trading_pair.split("_")[1]
    return quote

def remove_first_underscore(string):
    if string.startswith("_"):
        return string[1:]
    else:
        return string

if __name__=="__main__":
    db_where_ohlcv_data_for_stocks_is_stored = "ohlcv_1d_data_for_usdt_pairs_0000"
    db_where_ohlcv_data_for_stocks_is_stored=\
        return_dataframe_with_table_names_it_has_base_as_rows_number_as_columns(
            db_where_ohlcv_data_for_stocks_is_stored)



