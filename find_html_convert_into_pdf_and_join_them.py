import os
import subprocess

path = os.path.join(os.getcwd(), "/datasets", "/plots")
pdf_files = []

try:
    html_files = [f for f in os.listdir(path) if f.endswith('.html')]
except FileNotFoundError:
    print("The specified directory does not exist.")
    exit(1)

for html_file in html_files:
    pdf_file = html_file.replace(".html", ".pdf")
    pdf_files.append(pdf_file)
    try:
        subprocess.run(['wkhtmltopdf', os.path.join(path, html_file), os.path.join(path, pdf_file)])
    except subprocess.CalledProcessError as error:
        print(f"An error occurred while converting {html_file} to {pdf_file}: {error}")

try:
    final_pdf = os.path.join(path, "combined.pdf")
    subprocess.run(['pdfunite'] + pdf_files + [final_pdf])
except subprocess.CalledProcessError as error:
    print(f"An error occurred while combining PDF files: {error}")
