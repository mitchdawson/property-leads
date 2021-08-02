from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
import time
from collections import OrderedDict
from operator import itemgetter
import logging
from threading import Thread
logger = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARNING)

class RightMovePropertySaleHistory(Thread):
    """
    This class is used to extract date from an individual property page using Selenium. RM keep data relating to
    previous sales of the relevent property that can only be loaded from clicking a button on the page. 
    Selenium has the ability to do this and then return the relevent sale price and date, which in turn can be used
    to obtain the address by looking for corresponding data in RM's sales nearby pages.
    """
    def __init__(
        self, 
        rm_base_url, 
        rm_sales_history_cookies_rpath,
        rm_sales_history_element_rpath,
        rm_sales_history_table_rpath,
        db,
        running,
        program_sleep_time
        ):
        super().__init__()
        # Rightmove base url
        self.rm_base_url = rm_base_url
        # RightMove Sales History Cookies Path
        self.rm_sales_history_cookies_rpath = rm_sales_history_cookies_rpath
        # RightMove Sales History Element Path
        self.rm_sales_history_element_rpath = rm_sales_history_element_rpath
        # Rightmove Sale History Table Path
        self.rm_sales_history_table_rpath = rm_sales_history_table_rpath
        # Datebase Connection
        self.db = db
        # Sleep Time Value
        self.sleep_time = 5
        # Define the exit event placeholder
        self.running = running
        # Define a sleep time placeholder
        self.program_sleep_time = program_sleep_time

    def create_browser_object(self):
        # Create Some Options for the browser object.
        options = Options()
        # Run in headless mode.
        options.headless = True
        # Create a Firefox Browser Instance
        browser = webdriver.Firefox(service_log_path='logs\my-app.log', options=options)
        # Maximise the Window
        browser.maximize_window()
        # Return the browser object.
        return browser
    
    def accept_cookies(self, browser):
        cookies_accepted = False
        try:
            logger.info(f"sleeping {self.sleep_time} before accepting cookies")
            # Wait for the page to load.
            time.sleep(self.sleep_time)
            cookies = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, self.rm_sales_history_cookies_rpath)))
            logger.info(f"clicking cookies")
            cookies.click()
            logger.info("Cookies Accepted")
            # Update cookies accepted value.
            cookies_accepted = True
        except Exception as e:
            logger.exception(str(e))
        finally:
            return cookies_accepted
    
    def open_sales_history_element(self, browser):
        sales_history_clicked = False
        try:
            address_history = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, self.rm_sales_history_element_rpath)))
            logger.info(f"sleeping {self.sleep_time} before clicking address history")
            time.sleep(self.sleep_time)
            logger.info(f"clicking address history")
            address_history.click()
            # Update the sales_history_clicked element
            sales_history_clicked = True
            logger.info("Sales history element clicked, sleeping before returning.")
            time.sleep(1)
        except TimeoutException as t:
            # If we get a timeout with the address history then it indicates that the property has likely
            # been withdrawn from the site. We therefore opt to delete the property from the database.
            logger.exception(f"caught TimeoutException for url '{browser.current_url}', deleting.")
            # Get the rm_property_id value from the url.
            id = int(str(browser.current_url.split("/")[-1]))
            # Delete the property based on the rm_property_id.
            self.db.delete_property_for_rm_property_id((id,))
        except Exception as e:
            logger.exception(str(e))
        finally:
            return sales_history_clicked
    
    def extract_data_table(self, browser):
        """
        Method locates the tbody elements that hold the years and prices of
        previous sales.
        """
        # Get a list of the elements or an empty list of not found.
        table = browser.find_elements_by_xpath(self.rm_sales_history_table_rpath)
        # Check that table is not empty.
        if not table:
            return
        # Create a dictionary
        data = dict()
        # Iterate through the table data elements.
        for t in table:
            # Extract the year value.
            year = t.find_element_by_tag_name('td')
            # Extract the price value.
            price = t.find_element_by_tag_name('span')
            # Create a Key using the year and the price as a value.
            data[str(year.text)] = str(price.text)
            # print(year.text, price.text)
        # Return the data dictionary.
        return data

    def extract_sale_history(self, browser):
        # Get the year and price date in a dictionary from the tbody table.
        sale_hist_data = self.extract_data_table(browser)
        # Return the Data
        return sale_hist_data
    
    def open_property_url(self, url, browser):
        logger.info(f"getting property at url {url}")
        # Get the url with the browser object.
        browser.get(url)

    def get_sale_history_for_property(self, property, browser):
        # Structure is {2010: 500000, 2000: 350000}
        sale_history_data = self.extract_sale_history(browser)
        # Update the rm_sale_history_attempted value to True
        property["rm_sale_history_attempted"] = True
        # Check we have a dictionary and not None
        if not sale_history_data:
            return
        # If we have multiple sales returned for a property, filter them to the most recent.
        # if len(sale_history_data.keys()) > 1:
            # logger.info(f"sales history {sorted(sale_history_data.items(), reverse=True)[0]}")
        # We want the most recent sale history entry rather than all of them.
        sale_history_data = dict({sorted(sale_history_data.items(), reverse=True)[0]})
        # Add the property_id value i.e. property["id"] to the dictionary if not None.
        sale_history_data["id"] = property["id"]
        logger.info(f"sale history data {sale_history_data}")
        # Return the sale history data
        return sale_history_data

    def process_properties_sale_history(self, properties):
        # Check if we have a valid list of properties.
        if not properties:
            return
        
        # Create the browser object
        browser = self.create_browser_object()

        # Create a placeholder for our sale history data for all properties.
        sales_history_data_all_properties = list()

        # Cookies Accepted Placeholder
        cookies_accepted = False
        
        # Iterate through the properties
        for index in range(len(properties)):
            try:
                logger.info(f"getting property {index}/{len(properties)}")
                # Get the property object
                property = properties[index]

                # Build The URl
                url = self.rm_base_url + property["rm_property_url"]

                # Open the property url.
                self.open_property_url(url, browser)

                if not cookies_accepted:
                    cookies_accepted = self.accept_cookies(browser)
                    # Check the value again and continue if the cookies still werent accepted.
                    if not cookies_accepted:
                        continue
                
                # We need to Click on the button to open the sale history.
                # Open the sales history element on the page.
                if not self.open_sales_history_element(browser):
                    continue
                
                # Get the Sale History Data.
                sale_history_data = self.get_sale_history_for_property(property, browser)
                # Check for a value returned
                if not sale_history_data:
                    continue

                # Add the individual property sale history to sales_history_data_all_properties
                sales_history_data_all_properties.append(sale_history_data)

            except Exception as e:
                logger.exception(str(e))
        # Close the browser object
        browser.close()

        # Return the sales_history_data_all_properties list
        return sales_history_data_all_properties
    
    def get_properties_sale_history_values(self, properties_sale_history):
        """
        This method takes the property sale history list of dictionaries and
        returns a list of tuples containing the relevent data required for insertion
        into the database.
        """
        if not properties_sale_history:
            return

        # Create a list of sale_date, sale_price, property_id values.
        sales_history_values = list()
        
        # Iterate through the properties_sale_history list.
        # Structure is [{2010: 500000, 2000: 350000, property_id: 1}]
        for property in properties_sale_history:
            # Get and remove the property_id value and remove the key.
            id = property["id"]
            # Delete the property_id key
            del property["id"]
            # Iterate through the keys and values
            for k, v in property.items():
                # Append to the sales_history_values list.
                sales_history_values.append((k, v, id))
        
        # Return the sales_history_values list
        return sales_history_values

    def process_properties(self, properties):
        # Check if we have some valid properties in the list or return.
        if not properties:
            return
        
        # Get the sale history for the properties.
        properties_sale_history = self.process_properties_sale_history(properties)
        
        # Create a list of property id's of properties that we have attempted to get the
        # sale history for.
        property_ids = [(p["id"], True) for p in properties if p["rm_sale_history_attempted"] == True]
    
        # Update the Sale History Attempted Value
        rows_updated = self.db.update_sales_history_attempted(property_ids)

        # Check we have a value other than an integer.
        if not isinstance(rows_updated, int):
            logger.info(f"error updating property sale history attempted {property_ids}")
        
        # Check we have some sale history results.
        if not properties_sale_history:
            return

        # Get the values of the properties_sale_history dictionaries
        property_sale_history_values = self.get_properties_sale_history_values(properties_sale_history)
        
        # Insert the sale history data into the database.
        sale_historys_inserted = self.db.insert_sale_history_data(property_sale_history_values)
        
        # Check we have a value other than an integer.
        if not isinstance(sale_historys_inserted, int):
            logger.info(f"error inserting sale history data {sale_historys_inserted}")
            return

        
        
        



    def run(self):

        # Forever Loop
        while not self.running.is_set():
            try:

                # Get properties from db with no sale history data.
                properties = self.db.get_properties_with_no_sale_history()

                self.process_properties(properties)
                
            
            except Exception as e:
                logger.exception(str(e))
            
            finally:
                logger.info("Sleeping")
                time.sleep(self.program_sleep_time)

        logger.info("Exited while loop gracefully")