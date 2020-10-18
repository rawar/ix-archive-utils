from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
import io
import os

filename = '/Users/rwartala/Google Drive/data/ix-archive/daten/19/01/ix1901.pdf'
years_dict = {
    '88':'1988',
    '89':'1989',
    '90':'1990',
    '91':'1991',
    '92':'1992',
    '93':'1993',
    '94':'1994',
    '95':'1995',
    '96':'1996',
    '97':'1997',
    '98':'1998',
    '99':'1999',
    '00':'2000',
    '01':'2001',
    '02':'2002',
    '03':'2003',
    '04':'2004',
    '05':'2005',
    '06':'2006',
    '07':'2007',
    '08':'2008',
    '09':'2009',
    '10':'2010',
    '11':'2011',
    '12':'2012',
    '13':'2013',
    '14':'2014',
    '15':'2015',
    '16':'2016',
    '17':'2017',
    '18':'2018',
    '19':'2019'
}

def pdf_to_page_file(pdf_filename, txt_filename):
    fp = open(filename, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    print(type(retstr))
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    page_no = 0
    for pageNumber, page in enumerate(PDFPage.get_pages(fp)):
        interpreter.process_page(page)
        data = retstr.getvalue()
        with open(f"{txt_filename}_{page_no}.txt", 'wb') as file:
            file.write(data.encode('utf-8'))
        data = ''
        retstr.truncate(0)
        retstr.seek(0)
        page_no += 1

def get_files_by_pattern(start_dir, pattern):
    filenames = []
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith(pattern):
                filenames.append(os.path.join(root, file))

    return filenames

def flatten_output_filenames(start_dir, filenames, years_dict):
    output_filenames = {}
    for f_name in filenames:
        if f_name.endswith('.pdf'):
            d_name = os.path.dirname(f_name)
            path, edition = os.path.split(d_name)
            path, year =  os.path.split(path)
            full_year = years_dict[year]
            output_filename = f"ix_{full_year}-{edition}"
            output_filenames[f_name] = os.path.join(start_dir, output_filename)

    return output_filenames

def convert_pdf_to_page_files(filenames_dict):
    for source_file, target_file in filenames_dict.items():
        pdf_to_page_file(source_file, target_file) 


input_start_dir = '/Users/rwartala/Google Drive/data/ix-archive/daten'
output_start_dir = '/Users/rwartala/Google Drive/data/ix-archive/texts'
pdf_files = get_files_by_pattern(input_start_dir, '.pdf')
html_files = get_files_by_pattern(input_start_dir, '.htm')

pdf2txt_dict = flatten_output_filenames(output_start_dir, pdf_files, years_dict)
convert_pdf_to_page_files(pdf2txt_dict)


# ix_[year]_[volume]_[page].txt

#text = convert_pdf_to_string(filename)
#print(text)
#pdfpage_to_file(filename)
# /Volumes/iX USB

# daten/Jahrgang[00-99]/Ausgabe[01-13/Seite[000-1XX]
# Jahrgänge:
# 88 => 1988 (HTML)
# ...
# 99 => 1999 (HTML)
# 00 => 2000 (HTML)
# 01 => 2001 (HTML)
# 02 => 2002 (HTML)
# 03 => 2003 (HTML)
# ...
# 07 => 2007 (HTML)
# 08 => 2008 (PDF)
# ...
# 19 => 2019 (PDF)
