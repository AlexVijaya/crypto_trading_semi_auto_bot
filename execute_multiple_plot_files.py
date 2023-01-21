import subprocess
import sys
import time
import os
import shutil
import datetime
import pprint
def delete_files_in_current_rebound_breakout_and_false_breakout():
  # Get current directory
  current_dir = os.getcwd()

  # Construct path to subfolder
  subfolder_path = os.path.join(current_dir, 'current_rebound_breakout_and_false_breakout')

  file_path_to_delete=\
      get_file_name_for_deletion(subdirectory_name='current_rebound_breakout_and_false_breakout')


  # Check if subfolder exists
  if not os.path.exists(subfolder_path):
    print("subfolder doesn't exist")
    return

  # Delete all files in subfolder
  for filename in os.listdir(subfolder_path):

    file_path = os.path.join(subfolder_path, filename)
    if file_path!=file_path_to_delete:
        continue
    try:
      if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)
      elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
    except Exception as e:
      print('Failed to delete %s. Reason: %s' % (file_path, e))

def get_file_name_for_deletion(subdirectory_name='current_rebound_breakout_and_false_breakout'):

    # Declare the path to the current directory
    current_directory = os.getcwd()

    # Create the subdirectory in the current directory if it does not exist
    subdirectory_path = os.path.join(current_directory, subdirectory_name)
    os.makedirs(subdirectory_path, exist_ok=True)

    # Get the current date
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # Create the file path by combining the subdirectory and the file name (today's date)
    file_path = os.path.join(subdirectory_path, "crypto_" + today + '.txt')
    return file_path



def run_multiple_search_current_rebound_breakout_false_breakout_situations():
    # Run the Python script and capture its output

    # delete_files_in_current_rebound_breakout_and_false_breakout()

    # Get the path to the Python interpreter executable
    interpreter = sys.executable


    print(interpreter)
    files = ["plot_stock_charts_of_assets_which_is_closer_to_ath_than_50%_atr.py",
                 "plot_stock_charts_of_assets_which_is_closer_to_atl_than_50%_atr.py",
                 "plot_stock_charts_of_assets_with_breakout_of_ath_situations_entry_point_next_day.py",
                 "plot_stock_charts_of_assets_with_breakout_of_ath_situations_entry_point_next_day.py",
                 "plot_stock_charts_of_assets_with_breakout_of_atl_situations_entry_point_next_day.py",
                 "plot_stock_charts_of_assets_with_breakout_of_atl_situations_entry_point_on_day_two.py",
                 "plot_stock_charts_of_assets_with_false_breakout_of_ath_by_two_bars_situations_entry_point_next_day.py",
                 "plot_stock_charts_of_assets_with_false_breakout_of_ath_by_two_bars_situations_entry_point_next_day.py",
                 "plot_stock_charts_of_assets_with_false_breakout_of_atl_by_two_bars_situations_entry_point_next_day.py",
                 "plot_stock_charts_of_assets_with_false_breakout_of_atl_by_two_bars_situations_entry_point_next_day.py",
                 "plot_stock_charts_of_assets_with_fast_breakout_situations_off_the_ath_in_history.py",
                 "plot_stock_charts_of_assets_with_fast_breakout_situations_off_the_atl_in_history.py",
                 "plot_stock_charts_of_assets_with_rebound_situations_off_the_ath_in_history.py",
                 "plot_stock_charts_of_assets_with_rebound_situations_off_the_atl_in_history.py"]

    # Run each Python file in the list in parallel
    processes = []
    for file in files:
        process = subprocess.Popen([f'{interpreter}', file])
        processes.append(process)

    # Wait for the processes to complete and get their output
    # outputs = []
    for process in processes:
        output, _ = process.communicate()
        # outputs.append(output.decode())

    # # Print the output of the processes
    # for output in outputs:
    #     print(output)
    #     # pprint.print(output)
if __name__=="__main__":
    start_time = time.time()
    run_multiple_search_current_rebound_breakout_false_breakout_situations()
    end_time = time.time()
    overall_time = end_time - start_time
    print('overall time in minutes=', overall_time / 60.0)
    print('overall time in hours=', overall_time / 60.0 / 60.0)