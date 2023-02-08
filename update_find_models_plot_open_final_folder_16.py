import subprocess
import sys
def update_find_models_plot_open_final_folder_16():
    # Get the path to the Python interpreter executable
    interpreter = sys.executable
    files = ['update_historical_USDT_pairs_for_1D_next_bar_print_utc_time_16.py',
             'file2.py', 'file3.py']

    for file in files:
        subprocess.run([interpreter, file])