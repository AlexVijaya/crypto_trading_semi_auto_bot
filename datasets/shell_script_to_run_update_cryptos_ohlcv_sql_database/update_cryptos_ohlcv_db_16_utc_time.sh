set -e

# Set the path to the Python script
SCRIPT_PATH="/home/alex/PycharmProjects/crypto_trading_semi_auto_bot/update_historical_USDT_pairs_for_1D_next_bar_print_utc_time_16.py"


# Set the output file path
OUTPUT_FILE="/home/alex/PycharmProjects/crypto_trading_semi_auto_bot/output_of_update_historical_USDT_pairs_for_1D_next_bar_print_utc_time_16.txt"


# Run the Python script and save the output to the output file
dirpath=$(dirname "$SCRIPT_PATH")
cd $dirpath
echo $dirpath
/home/alex/.local/share/virtualenvs/crypto_trading_semi_auto_bot-VajgW3Re/bin/python  $SCRIPT_PATH > $OUTPUT_FILE


echo "Done!"
