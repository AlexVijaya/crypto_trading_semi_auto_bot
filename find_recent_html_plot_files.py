from PIL import Image
import pdfkit
import os
from PyPDF2 import PdfMerger
import datetime


def jpeg_to_pdf_merge(jpeg_files):
    # Initialize the PDF merger
    merger = PdfMerger()

    # Convert each JPEG file to a PDF and add it to the merger
    for file in jpeg_files:
        pdf_file = file.replace(".jpeg", ".pdf").replace(".jpg", ".pdf")
        image = Image.open(file)
        print(f"I am working with {file}")
        image.save(pdf_file, "PDF", resolution=100.0)
        merger.append(pdf_file)

    # Get the current date and time
    now = datetime.datetime.now()
    date_and_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Define the path to the merged PDF file
    merged_pdf_path = os.path.join(os.getcwd(), "datasets",
                                   "plots",
                                   "merged_pdfs","with_half_atr_approach",
                                   f"crypto_plot_{date_and_time}.pdf")

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(merged_pdf_path), exist_ok=True)

    # Save the merged PDF to the specified file
    merger.write(merged_pdf_path)



    # Delete the individual PDF files
    for file in jpeg_files:
        pdf_file = file.replace(".jpeg", ".pdf").replace(".jpg", ".pdf")
        os.remove(pdf_file)

    return merged_pdf_path


def jpeg_to_pdf_merge_no_half_atr_approach(jpeg_files):
    # Initialize the PDF merger
    merger = PdfMerger()



    # Convert each JPEG file to a PDF and add it to the merger
    for file in jpeg_files:
        # if "asset_approaches_its_ath_closer_than_50percent_atr" in file:
        #     continue
        #
        # if "asset_approaches_its_atl_closer_than_50percent_atr" in file:
        #     continue


        pdf_file = file.replace(".jpeg", ".pdf").replace(".jpg", ".pdf")
        image = Image.open(file)
        print(f"I am working with {file}")
        image.save(pdf_file, "PDF", resolution=100.0)
        merger.append(pdf_file)

    # Get the current date and time
    now = datetime.datetime.now()
    date_and_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Define the path to the merged PDF file
    merged_pdf_path = os.path.join(os.getcwd(), "datasets",
                                   "plots",
                                   "merged_pdfs","no_half_atr_approach",
                                   f"crypto_plot_no_half_atr_approach_{date_and_time}.pdf")

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(merged_pdf_path), exist_ok=True)

    # Save the merged PDF to the specified file
    merger.write(merged_pdf_path)



    # Delete the individual PDF files
    for file in jpeg_files:
        pdf_file = file.replace(".jpeg", ".pdf").replace(".jpg", ".pdf")
        os.remove(pdf_file)

    return merged_pdf_path

def remove_half_atr_from_list(list_of_needed_jpg_files):
    # list_with_removed_half_atr=[]
    # for file_path in list_of_needed_jpg_files:
    #     print("file_path")
    #     print(file_path)
    #     if "asset_approaches_its_ath_closer_than_50percent_atr" not in file_path:
    #         list_with_removed_half_atr.append(file_path)
    #
    #     if "asset_approaches_its_atl_closer_than_50percent_atr" not in file_path:
    #         list_with_removed_half_atr.append(file_path)
    list_with_removed_half_atr=[elem for elem in list_of_needed_jpg_files if
            'asset_approaches_its_ath_closer_than_50percent_atr' not in elem and 'asset_approaches_its_atl_closer_than_50percent_atr' not in elem]
    #
    print("list_with_removed_half_atr")
    print(list_with_removed_half_atr)
    return list_with_removed_half_atr

    # print("list_with_removed_half_atr")
    # print(list_with_removed_half_atr)
    # print("**"*80)
    # return list_with_removed_half_atr

def html_to_pdf_merge(html_files):
    # Initialize the PDF merger
    merger = PdfMerger()

    # Convert each HTML file to a PDF and add it to the merger
    for file in html_files:
        pdf_file = file.replace(".html", ".pdf")
        pdfkit.from_file(file, pdf_file)
        merger.append(pdf_file)

    # Define the path to the merged PDF file
    merged_pdf_path = os.path.join(os.getcwd(), "datasets", "plots", "merged_pdfs", "merged.pdf")

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(merged_pdf_path), exist_ok=True)

    # Save the merged PDF to the specified file
    merger.write(merged_pdf_path)

    # Delete the individual PDF files
    for file in html_files:
        pdf_file = file.replace(".html", ".pdf")
        os.remove(pdf_file)

    return merged_pdf_path
def find_html_files(folder):

    from datetime import datetime, timedelta
    html_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time > datetime.now() - timedelta(hours=1):
                    html_files.append(file_path)
    return html_files

def find_jpg_files(folder):

    from datetime import datetime, timedelta
    jpg_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".jpg"):
                file_path = os.path.join(root, file)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time > datetime.now() - timedelta(hours=3):
                    jpg_files.append(file_path)
    return jpg_files


if __name__=="__main__":
    # list_of_needed_html_files=find_html_files(os.path.join(os.getcwd(),"datasets","plots"))
    # print('os.path.join(os.curdir,"/datasets","/plots")')
    # print(os.path.join(os.getcwd(), "datasets", "plots"))
    # print('list_of_needed_html_files')
    # print(list_of_needed_html_files)

    list_of_needed_jpg_files = find_jpg_files(os.path.join(os.getcwd(), "datasets", "plots"))
    print('list_of_needed_jpg_files')
    print(list_of_needed_jpg_files)
    # print('os.path.join(os.curdir,"/datasets","/plots")')
    # print(os.path.join(os.getcwd(), "datasets", "plots"))
    # print('list_of_needed_jpg_files')
    # print(list_of_needed_jpg_files)

    path_to_merged_pdf=jpeg_to_pdf_merge(list_of_needed_jpg_files)

    list_of_needed_jpg_files_no_half_atr=remove_half_atr_from_list(list_of_needed_jpg_files)
    path_to_merged_pdf_no_half_atr_approach =\
        jpeg_to_pdf_merge_no_half_atr_approach(list_of_needed_jpg_files_no_half_atr)
    #
    # print('path_to_merged_pdf')
    # print(path_to_merged_pdf)

    # print(find_html_files("/home/alex/PycharmProjects/crypto_trading_semi_auto_bot/datasets/plots"))