import requests
import logging
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("pdfminer").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
from threading import Thread
import time
import re
import random
import pdfplumber
import os

class EPC(Thread):

    def __init__(self, sleep_time, db, running, epc_base_url):
        super().__init__()
        # Define the application sleep time
        self.sleep_time = sleep_time
        # Create the Database placeholder
        self.db = db
        # Define the exit event placeholder
        self.running = running
        # Certificate Regex
        self.epc_number_regex = r"(.*)(\d{4}-\d{4}-\d{4}-\d{4}-\d{4})(.*)"
        # Government Epc Checking url (address based on epc)
        self.epc_base_url = epc_base_url


    def make_web_request_for_url(self, url):
        count = 0
        result = None
        while count < 3:
            try:
                request = requests.get(url)
                message = f"Url = {request.url}, Status = {request.status_code}"
                logger.info(message)
            except Exception as e:
                logger.exception(str(e))
                count += 1
                time.sleep(10)
            else:
                result = request
                break
        return result
    
    def get_page_for_url(self, url):
        """
        This method returns a valid web page for the given url or None based on the
        requests status code.
        """
        page = self.make_web_request_for_url(url)
        # Check the status code
        if page.status_code != 200:
            return None
        logger.info(f"returning page")
        return page
    
    def save_epc_page_into_pdf(self, page, file_path):
        """
        This method gets takes the web page content and writes this to
        a pdf file based on the name of the property id.
        """
        # logger.info(f"opening file {file_path}")
        file = open(file_path, "wb")
        logger.info(f"writing content to {file_path}")
        file.write(page.content)
        # logger.info(f"closing file {file_path}")
        file.close()
    
    def open_pdf_file(self, file_path):
        # Create the pdf file placeholder
        pdf = None
        try:
            # Create instance of the pdfplumber class.
            pdf = pdfplumber.open(file_path)
            logger.info(f"successfully opened pdf {file_path}")
        except Exception as e:
            logger.info(f"caught exception when opening pdf {file_path}")
            logger.exception(str(e))
            # Flush the PDF Cache
            pdf.flush_cache()
            # Close the pdf
            pdf.close()
        finally:
            return pdf
    
    def extract_page_from_pdf(self, pdf, page_number=0):
        # Create the page placeholder
        page = None
        try:
            # Get the first page.
            page = pdf.pages[page_number]
            logger.info(f"sucessfully extracted page from pdf")
        except Exception as e:
            logger.info(f"caught exception extracting page from pdf")
            logger.exception(str(e))
        finally:
            return page

    def extract_text_from_page(self, page):
        # Create the page placeholder
        text = None
        try:
            # Extract The Text
            text = page.extract_text()
            if text:
                 logger.info(f"sucessfully extracted text from the page")
        except Exception as e:
            logger.info(f"exception extracting text from the page")
            logger.exception(str(e))
        finally:
            return text

    def get_epc_certificate_number(self, file_path):
        # Set the Epc Certificate Placeholder
        epc_number = None
        try:
            # Create instance of the pdfplumber class.
            pdf = self.open_pdf_file(file_path)
            if not pdf:
                # Flush the pdf page cache
                self.epc_flush_and_close_pdf(pdf)
                return epc_number
            
            # Get the first page.
            page = self.extract_page_from_pdf(pdf)
            if not page:
                # Flush the pdf page cache
                self.epc_flush_and_close_pdf(pdf)
                return epc_number
            
            # Extract The Text
            text = self.extract_text_from_page(page)
            # Check The value of text
            if not text:
                # Flush the pdf page cache
                self.epc_flush_and_close_pdf(pdf)
                return epc_number
            
            # Attempt a regex match
            epc_number = self.get_epc_regex_match(text)
            # Flush the pdf page cache
            self.epc_flush_and_close_pdf(pdf)
        
        except Exception as e:
            logger.exception(str(e))
        finally:
            logger.info(f"finally Epc number is {epc_number}")
            # Return the value of epc_number
            return epc_number
    
    def epc_flush_and_close_pdf(self, pdf):
        # Check for a NoneType object.
        if not pdf:
            return
        # Flush the PDF Cache
        pdf.flush_cache()
        # Close the pdf
        pdf.close()
    
    def get_epc_regex_match(self, text):
        # Attempt a regex match.
        match = re.search(self.epc_number_regex, text)
        # Check for a successful match
        if match:
            logger.info(f"Epc number is {match.group(2)}")
            return match.group(2)
    
    def extract_address_from_epc_page(self, page):
        """
        This method attempts to obtain the address for a given epc number 
        via the government epc checker website.
        """
        # Address Placeholder
        address = None
        try:
            address = str(page.text).split('<p class="epc-address govuk-body">')[1].split('</p>')[0]
            # Format Address Before Returning
            address = str(address).replace("<br />", ", ").strip()
        except Exception as e:
            logger.exception(str(e))
        finally:
            logger.info(f"Epc cert address is {address}")
            return address
    
    def cleanup_files_directory(self):
        # Create the file path
        dir_path = os.path.abspath(os.path.join(os.sep, os.getcwd(), 'epc', 'pdfs'))
        # logger.info(f"{dir_path}")
        # Create a list of files in the directory path.
        files = os.listdir(dir_path)
        # Iterate through the files.
        for file in files:
            # Create the file_path
            file_path = os.path.join(os.sep, dir_path, file)
            logger.info(f"{file_path}")
            # Remove the file
            os.remove(file_path)

    def process_properties(self, properties):
        # Check that we have a valid list of properties, if not return.
        if not properties:
           return

        # Create an address and property id placeholder list.
        address_and_property_id_list = list()
        
        # Iterate through the properties list
        for index in range(len(properties)):
            try:
                logger.info(f"Getting Property {index + 1}/{len(properties)}")
                # Get the property from the list.
                property = properties[index]
                logger.info(property)

                # Get the Epc Url Page.
                page = self.get_page_for_url(property["rm_epc_cert_url"])
                if not page:
                    # Update the DB Value to indicate that we have attempted to obtain the EPC,
                    # so that this isnt re attempted.
                    self.db.update_epc_cert_address_attempted([(True, property["id"])])
                    continue
                
                # Generate the file path to store and read the pdf.
                file_path = os.path.abspath(
                    os.path.join(os.sep, os.getcwd(), 'epc', 'files', f'{property["id"]}.pdf')
                )
                
                # Save the page content to a pdf file.
                self.save_epc_page_into_pdf(page, file_path)

                # Get the epc number
                epc_number = self.get_epc_certificate_number(file_path)
                # Delete the saved file here.
                # remove(file_path)
                if not epc_number:
                    # Update the DB Value to indicate that we have attempted to obtain the EPC,
                    # so that this isnt re attempted.
                    self.db.update_epc_cert_address_attempted([(True, property["id"])])
                    continue
                
                # Get the page for the certificate from the government epc checker
                page = self.get_page_for_url(f"{self.epc_base_url}{epc_number}")
                if not page:
                    # Update the DB Value to indicate that we have attempted to obtain the EPC,
                    # so that this isnt re attempted.
                    self.db.update_epc_cert_address_attempted([(True, property["id"])])
                    continue
                
                # Get the Address from the page.
                address = self.extract_address_from_epc_page(page)
                if not address:
                    # Update the DB Value to indicate that we have attempted to obtain the EPC,
                    # so that this isnt re attempted.
                    self.db.update_epc_cert_address_attempted([(True, property["id"])])
                    continue

                # Add the Address and the property id to the list.
                address_and_property_id_list.append((address, property["id"]))          
            
            except Exception as e:
                logger.exception(str(e))
            
            finally:
                time.sleep(random.randint(1, 5))
        
        # Cleanup files in the files diretory.
        self.cleanup_files_directory()
        
        # Return the Address and property id value list.
        return address_and_property_id_list
    
    def update_properties_epc_address_values(self, address_and_property_id_list):
        # Check if we have any values, return if not.
        if not address_and_property_id_list:
            return
        
        # Update properties and the epc_cert_address values.
        self.db.update_epc_cert_address(address_and_property_id_list)


    def run(self):
        # Forever Loop
        while not self.running.is_set():
            try:
                # Get the properties with an EPC Url in the database.
                properties = self.db.get_properties_with_epc_url_and_no_real_address()

                # Get the property address and property id value list.
                address_and_property_id_list = self.process_properties(properties)

                # Update the datebase with the values.
                self.update_properties_epc_address_values(address_and_property_id_list)

            except Exception as e:
                logger.exception(str(e))
            
            finally:
                logger.info("Sleeping")
                time.sleep(self.sleep_time)