from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from dehyphen import FlairScorer
from dehyphen.format import text_to_format, format_to_paragraph
from bs4 import BeautifulSoup
import io
import os
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

filename = '/Users/rwartala/Google Drive/data/ix-archive/daten/19/01/ix1901.pdf'
years_dict = {
    '88': '1988',
    '89': '1989',
    '90': '1990',
    '91': '1991',
    '92': '1992',
    '93': '1993',
    '94': '1994',
    '95': '1995',
    '96': '1996',
    '97': '1997',
    '98': '1998',
    '99': '1999',
    '00': '2000',
    '01': '2001',
    '02': '2002',
    '03': '2003',
    '04': '2004',
    '05': '2005',
    '06': '2006',
    '07': '2007',
    '08': '2008',
    '09': '2009',
    '10': '2010',
    '11': '2011',
    '12': '2012',
    '13': '2013',
    '14': '2014',
    '15': '2015',
    '16': '2016',
    '17': '2017',
    '18': '2018',
    '19': '2019'
}

def html_to_page_file(html_filename, txt_filename):
    """
    Convert a html file to a text file
    :param html_filename: Name of the HTML file
    :param txt_filename: Name of the text file
    :return: None
    """
    fp = open(html_filename, 'rb')
    html_content = fp.read()
    soup = BeautifulSoup(html_content, features="html.parser")
    txt_fname = f"{txt_filename}.txt"
    logging.info(f"convert {html_filename} => {txt_fname}")
    with open(txt_fname + ".txt", 'wb') as file:
        file.write(soup.get_text().encode('utf-8'))


def pdf_to_page_file(pdf_filename, txt_filename):
    fp = open(pdf_filename, 'rb')
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    # codec = 'utf-8'
    codec = 'iso-8859-1'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    page_no = 0
    for pageNumber, page in enumerate(PDFPage.get_pages(fp)):
        interpreter.process_page(page)
        data = retstr.getvalue()
        txt_fname = f"{txt_filename}_{page_no}.txt"
        logging.info(f"convert {pdf_filename} => {txt_fname}")
        with open(txt_fname, 'wb') as file:
            file.write(data.encode('utf-8'))
            # file.write(data.encode('iso-8859-1'))
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


def pdf_flatten_output_filenames(start_dir, filenames, years_dict):
    pdf_output_filenames = {}
    for f_name in filenames:
        if f_name.endswith('.pdf'):
            d_name = os.path.dirname(f_name)
            path, edition = os.path.split(d_name)
            path, year = os.path.split(path)
            full_year = years_dict[year]
            output_filename = f"ix_{full_year}-{edition}"
            pdf_output_filenames[f_name] = os.path.join(start_dir, output_filename)

    return pdf_output_filenames


def html_flatten_output_filenames(start_dir, filenames, years_dict):
    html_output_filenames = {}
    for f_name in filenames:
        if f_name.endswith('art.htm'):
            d_name = os.path.dirname(f_name)
            path, page = os.path.split(d_name)
            path, edition = os.path.split(path)
            path, year = os.path.split(path)
            full_year = years_dict[year]
            output_filename = f"ix_{full_year}-{edition}-{page}"
            html_output_filenames[f_name] = os.path.join(start_dir, output_filename)

    return html_output_filenames


def convert_input_to_page_files(filenames_dict):
    for source_file, target_file in filenames_dict.items():
        logger.info(f"convert {source_file}...")
        if source_file.endswith('.htm'):
            html_to_page_file(source_file, target_file)
        elif source_file.endswith('.pdf'):
            pdf_to_page_file(source_file, target_file)


def remove_small_files(text_files_directory: str, file_size_max_in_bytes: int) -> int:
    """
    Remove smaller files with no content.
    :param text_files_directory: Input directory with all text files
    :param file_size_max_in_bytes: Number of file size in bytes to remove
    :return: number of removed files
    """
    dirpath, dirs, files = next(os.walk(text_files_directory))
    file_idx = 0
    for file in files:
        if os.path.getsize(file) < file_size_max_in_bytes:
            file_idx += 1
            os.remove(file)

    return file_idx


def dehyphen_text_file(text_filename) -> str:
    """
    Return a dehyphed text string from a given text file by name.
    :param text_filename: Name of the text file
    :return: Text string with dehyphed text
    """
    logger.info(f"read text from '{text_filename}'")
    txt_file = open(text_filename, 'r', encoding='utf-8')
    lines = txt_file.readlines()
    text_lines = []
    for line in lines:
        # remove every line < 6 characters
        if len(line) > 5:
            # remove more then one space in each line
            line = re.sub("\s\s+", " ", line)
            #line = re.sub("ˇ%", "%")
            ln = [line.strip("\n")]
            text_lines.append(ln)

    logger.info(f"dehyphen {len(text_lines)} lines of text")
    scorer = FlairScorer(lang="de")
    fixed_hyphens = scorer.dehyphen_paragraph(text_lines)
    logger.info(f"fixed_hyphens='{fixed_hyphens}'")
    # glue the parts to one text line
    dehyphed_text = "".join(["".join(fh) + " " for fh in fixed_hyphens])
    logger.info(f"dehyphed_text='{dehyphed_text}'")
    return dehyphed_text


def create_csv_from_dir(csv_filename: str, text_files_directory:str):
    """
    Create a single column csv file from a text file directory.
    :param csv_filename: Name of the output csv file
    :param text_files_directory: Name of the text files directory
    :return: None
    """
    with open(csv_filename, 'w') as csv_file:
        dirpath, dirs, files = next(os.walk(text_files_directory))
        number_files = len(files)
        file_idx = 1
        logger.info(f"{number_files} file(s) found in {text_files_directory}")
        for filename in files:
            logger.info(f"process {file_idx}/{number_files}...")
            fname = os.path.join(dirpath, filename)
            if fname.endswith('.txt'):
                dehyphed_text = dehyphen_text_file(fname)
                # write one text each line
                csv_file.write(dehyphed_text + '\n')
                file_idx += 1


def main():
    # input directory for iX archive data
    input_start_dir = '/Users/rwartala/Google Drive/data/ix-archive/daten'

    # output directory for iX text files
    output_start_dir = '/Users/rwartala/Google Drive/data/ix-archive/new_texts'

    # text data file
    csv_filename = "ix_archive.csv"

    # all iX achive pdf files
    pdf_files = get_files_by_pattern(input_start_dir, '.pdf')
    pdf2txt_dict = pdf_flatten_output_filenames(output_start_dir, pdf_files, years_dict)
    convert_input_to_page_files(pdf2txt_dict)


    # all iX archive html files
    #html_files = get_files_by_pattern(input_start_dir, '.htm')
    #html2txt_dict = html_flatten_output_filenames(output_start_dir, html_files, years_dict)
    #convert_html_to_page_files(html2txt_dict)

    # number_removed_files = remove_small_files(output_start_dir, 1)
    # logger.info(f"remove {number_removed_files} files from {output_start_dir}")
    #logger.info(f"read text files from {output_start_dir}")
    #create_csv_from_dir(csv_filename, output_start_dir)

    #text = dehyphen_text_file("/Users/rwartala/Google Drive/data/ix-archive/texts/ix_1991-10_54.txt")
    #print(text)

if __name__ == "__main__":
    main()
