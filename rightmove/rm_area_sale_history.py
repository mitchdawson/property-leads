import logging
logger = logging.getLogger(__name__)
import json
import time
from threading import Thread


class RightMoveAreaSaleHistory(Thread):
    """
    This class is used to extract previous sale results for a given postcode. This data 
    can be used to match the individual property sale info, providing the address.
    """

    def __init__(self, web_client, db, running, sleep_time):
        super().__init__()
        # Web Client Session
        self.web_client = web_client
        # Datebase Connection
        self.db = db
        # Define the exit event placeholder
        self.running = running
        # Define a sleep time placeholder
        self.sleep_time = sleep_time

    def get_area_sale_history_page(self, postcode_url, page_number=None):
        """
        Method gets a page of the previous house sales for a given postcodes, indiviual properties
        contain the full address.
        """
        if page_number:
            postcode_url = postcode_url + f"?page={page_number}"
        
        logger.info("getting area sale history page")
        # Get the property page.
        page = self.web_client.get_page_for_url(postcode_url)
        # Check for a value of None or a non 200 status code.
        if not page or page.status_code != 200:
            # Continue for the next url
            return
        logger.info("got area sale history page")
        return page
    
    def get_area_sale_history_properties(self, json):
        """
        Method returns a list of properties and their previous sale dates and prices.
        Example: "properties":[{"address":"14, Hillwood Grove, Hutton, Brentwood, Essex CM13 2PD","propertyType":"Detached","bedrooms":5,"images":{"imageUrl":"https://media.rightmove.co.uk/dir/147k/146846/48181536/146846_6187143_IMG_00_0000_max_135x100.jpg","count":23},"hasFloorPlan":true,"transactions":[{"displayPrice":"£1,800,000","dateSold":"12 Mar 2020","tenure":"Freehold","newBuild":false}],"location":{"lat":51.62568,"lng":0.33711},"detailUrl":"https://www.rightmove.co.uk/house-prices/detailMatching.html?prop=48181536&sale=11345743&country=england"}]
        """
        try:
            properties = json["properties"]
        except Exception as e:
            logger.exception(str(e))
            return
        else:
            # Return the results.
            logger.info("extracted properties successfully")
            return properties
    
    def get_area_sale_history_result_count(self, json):
        """
        Method extracts the result count value from the json input parameter.
        """
        try:
            result_count = int(json["resultCount"])
        except Exception as e:
            logger.exception(str(e))
            return
        else:
            logger.info(f"got {result_count} sales results")
            # Return the results.
            return result_count

    def get_area_sale_history_json(self, page):
        """
        Method extracts the sales history json from the given page.
        """
        # Break out the json data from the page and load into a python dict.
        try:
            # Get the page text value from the requests object
            page_text = page.text
            js = json.loads(page_text.split("</script><script>window.__PRELOADED_STATE__ = ")[1].split("</script>")[0])
        except Exception as e:
            logger.exception(str(e))
            return
        else:
            logger.info("extracted sale history json successfully")
            # Return the results.
            return js["results"]
    
    def get_sale_history_for_postcode(self, postcode_url):
        """
        This method handles the process of extracting all area sales history for a given postcode.
        A page will yield a maximum of 25 results, therefore it maybe necessary to request additional pages,
        depending on the number of results.
        """
        # Create an area sale history placeholder.
        area_sale_history = list()

        # Get the first page for a given postcode.
        first_page = self.get_area_sale_history_page(postcode_url)
        if not first_page:
            return area_sale_history
        
        # Extract the Json from the page.
        json = self.get_area_sale_history_json(first_page)
        # Get the Number of results found.
        result_count = self.get_area_sale_history_result_count(json)
        logger.info("extracted result count successfully")
        # Get the sales history from the first page.
        sales_history = self.get_area_sale_history_properties(json)
        # Add the sales history to the area_sale_history list.
        area_sale_history.extend(sales_history)

        # Check if the length of the area_sale_history list is equal to the result count.
        while len(area_sale_history) < result_count:
            page_number = 2
            next_page = self.get_area_sale_history_page(postcode_url, page_number=page_number)
            if not next_page:
                continue
            
            # Extract the Json from the page.
            json = self.get_area_sale_history_json(next_page)
            # Get the sales history from the first page.
            sales_history = self.get_area_sale_history_properties(json)
            # Add the sales history to the area_sale_history list.
            area_sale_history.extend(sales_history)
            # Increment the page counter
            page_number += 1

        # Return the area_sale_history list
        return area_sale_history
    
    def get_address_for_property(self, property_sale_history, area_sales_history):
        # Set a place holder for address.
        address = None
        # Iterate through the sales history dates and prices for the property.
        for i in range(len(property_sale_history)):
            if address:
                break
            try:
                # Break out a sale_date and sale_price object.
                psh = property_sale_history[i]
                # Break out the sale date.
                psh_date = psh["sale_date"]
                # Break out the sale price.
                psh_price = str(psh["sale_price"]).replace("£", "").replace(",", "") # "£530,000" becomes "530000"
                logger.info(f"property sale date {psh_date}, sale price {psh_price}")
                # Iterate through the area sale history object.
                for j in range(len(area_sales_history)):
                    # Break out the transactions.
                    transactions = area_sales_history[j]["transactions"]
                    # Iterate through the transactions.
                    for t in transactions:
                        ash_price = str(t["displayPrice"]).replace("£", "").replace(",", "") # "£530,000" becomes "530000"
                        ash_date = str(t["dateSold"]).split()[-1] # "8 Nov 2019" becomes 2019
                        # logger.info(f"area sale date {ash_date}, sale price {ash_price}")
                        # Compare the date and price values.
                        if (psh_date == ash_date and psh_price == ash_price):
                            # Extract the Address value and update
                            address = area_sales_history[j]["address"]
                            logger.info(f"Located address - {address}")
                            # Break out of the loop.
                            break
                    # Check if we have a value other than None for address.
                    if address:
                        break
            
            except Exception as e:
                logger.exception(str(e))
                continue
        # Return the Value of address.
        return address
    
    def process_property_area_sale_histories(self, properties):
        # Check if we have some valid properties in the list or return.
        if not properties:
            return
        
        # Create a list to hold the property Id and real address value.
        property_real_address_data = list()

        # Iterate through the properties.
        for property in properties:

            try:

                # Get the sale history for the given property id from the database.
                property_sale_history = self.db.get_sale_history_for_property_id(property["id"])

                # Check for a None value.
                if not property_sale_history:
                    continue

                # Get the area sale history for the given sold nearby url which shows all logged sales for 
                # the same postcode.
                area_sales_history = self.get_sale_history_for_postcode(property["rm_sold_nearby_url"])

                # Try and get an address for the property
                address = self.get_address_for_property(property_sale_history, area_sales_history)

                # Check for a None value.
                if not address:
                    # We need to update the database to set "rm_real_address_attempted" to true so that we dont attempt this
                    # property search again.
                    self.db.update_real_address_attempted([(True, property["id"])])
                    continue
                
                # Create a tuple of the real address value and the rm_real_address_attempted (True) and property id, and add to the
                # property_real_address_data list
                property_real_address_data.append((address, True, property["id"]))

            except Exception as e:
                logger.exception(str(e))
        
        # Check that we have some entries to update.
        if property_real_address_data:

            # Update the datebase with the real address for the given property id.
            properties_updated = self.db.update_real_address_value(property_real_address_data)

            # Print the number of rows updated.
            logger.info(f"Properties real address updated {str(properties_updated)}")
        

    
    def run(self):
        
        # Forever Loop
        while not self.running.is_set():
            try:
                # Get properties from the database. This returns a list of property 
                # id, rm_id, rm_postcode, rm_sold_nearby_url values for properties which have some sale history.
                properties = self.db.get_properties_with_no_real_address_and_sale_history_attempted()

                # Process Properties and area sale histories
                self.process_property_area_sale_histories(properties)

            except Exception as e:
                logger.exception(str(e))
            
            finally:
                logger.info("Sleeping")
                time.sleep(self.sleep_time)

        logger.info("Exited while loop gracefully")

