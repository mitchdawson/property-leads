import PyPDF2
import pdfplumber
import re
import requests

file_name = "epc.pdf"
cert_regex = r"^\d{4}-\d{4}-\d{4}-\d{4}-\d{4}$"
# url = 'https://media.rightmove.co.uk/9k/8250/82363769/8250_ejs190166_EPC_00_0000.pdf'
# url = 'https://media.rightmove.co.uk/152k/151070/103685408/151070_1122248-1_EPC_00_0001.pdf'
# url = 'https://media.rightmove.co.uk/15k/14962/104446175/14962_SHJSWMCH01321_EPC_00_0000.pdf'
# url = 'https://media.rightmove.co.uk/203k/202979/104971478/202979_1145571-1_EPC_00_0001.pdf'
url = 'https://media.rightmove.co.uk/18k/17328/99902717/17328_BirchHouse_EPC_00_0002.pdf'

def funcpdftotext():
    pass


def pdf_plumber_func():
    with pdfplumber.open(file_name) as temp:
        first_page = temp.pages[0]
        for line in str(first_page.extract_text()).splitlines():
            match = re.match(cert_regex, line)
            if match:
                print(line)
        # print(first_page.extract_text())

# pdf_plumber_func()

def new_pdfplumber_func():
    r = requests.get(url)
    print(r.status_code)
    file = open("test1.pdf", "wb")
    file.write(r.content)
    file.close()
    pdf = pdfplumber.open("test1.pdf")
    for index in range(len(pdf.pages)):
        page = pdf.pages[index]
        print(page.extract_text())
        page.flush_cache()
    pdf.close()

# new_pdfplumber_func()


def pypdf2_func():
    # creating a pdf file object 
    pdfFileObj = open('test1.pdf', 'rb') 
    
    # creating a pdf reader object 
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False) 
    
    # printing number of pages in pdf file 
    print(pdfReader.numPages)

    for index in range(pdfReader.numPages):
        page  = pdfReader.getPage(index)
        print(page.extractText())
    
    # # creating a page object 
    # pageObj = pdfReader.getPage(0) 
    
    # # extracting text from page 
    # print(pageObj.extractText()) 
    
    # closing the pdf file object 
    pdfFileObj.close()

pypdf2_func()

def pdfminerfunc():
    # from pdfminer.high_level import extract_pages
    # from pdfminer.layout import LTTextContainer
    # for page_layout in extract_pages("test.pdf"):   
    #     for element in page_layout:
    #         if isinstance(element, LTTextContainer):
    #             print(element.get_text())
    from pdfminer.high_level import extract_text
 
    text = extract_text("test.pdf")
 
    print(text)
# pdfminerfunc()