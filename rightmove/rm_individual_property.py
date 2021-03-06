import json
import time
import logging
logger = logging.getLogger(__name__)
from threading import Thread
import random

class RightMoveIndividualProperty(Thread):

    """
    The RightMoveIndividualProperty class is used to retrieve an individual properties details. 
    We use this to obtain values such as the:
    - sold nearby url so that we can locate the prices of previous sales including the addresses.
    - property postcode so that this can be used to cross refference with the prvious sale information.
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
    
    def parse_property_page(self, page):
        """
        Takes an individual property html page and extracts the json data contained within.
        """
        # Break out the json data from the page and load into a python dict.
        try:
            # Load the Json from the page.
            js = json.loads(page.split("window.PAGE_MODEL = ")[1].split("</script>")[0])
            logger.info(f"property json extracted successfully")
        except Exception as e:
            logger.exception(str(e))
            return
        else:
            return js

    def get_sold_stc_status(self, json):
        # Set a default value of None for the soldSTC status.
        sold_stc = None
        # Extract the sold stc status.
        try:
            sold_stc = json["analyticsInfo"]["analyticsProperty"]["soldSTC"]
        except KeyError:
            return
        else:
            return sold_stc

    def get_and_set_property_sold_nearby_url(self, json, property):
        # Extract the url for properties sold nearby.
        try:
            property["rm_sold_nearby_url"] = json["propertyData"]["propertyUrls"]["nearbySoldPropertiesUrl"]
            logger.info(f"rm_sold_nearby_url extracted successfully")
        except Exception as e:
            logger.exception(str(e))
            return

    def get_and_set_property_postcode(self, json, property):
        # Extract the postcode value from the json.
        try:
            property["rm_postcode"] = json["analyticsInfo"]["analyticsProperty"]["postcode"]
            logger.info(f"rm_postcode extracted successfully")
        except Exception as e:
            logger.exception(str(e))
            return
    
    # def get_and_set_property_delivery_point_id(self, json, property):
    #     # Populate the "rm_delivery_point_id" key with a default integer value of 0.
    #     property["rm_delivery_point_id"] = 0
    #     try:
    #         # Check for an Interger Value.
    #         if type(json["propertyData"]["address"]["deliveryPointId"]) == int:
    #             # Set the Property Delivery Point Id value.
    #             property["rm_delivery_point_id"] = json["propertyData"]["address"]["deliveryPointId"]      
    #     except KeyError:
    #         return

    def get_property_epc_certificate_data(self, json, property):
        # Set a default value of None on property["epcGraphs"] = None.
        property["rm_epc_cert_url"] = None
        # Set the "rm_epc_cert" value to 1
        property["rm_epc_cert"] = False
        # Get the value contained within the "epcGraphs" list value if it is not empty.
        try:
            if json["propertyData"]["epcGraphs"]:
                # We want to filter out PDF files with the url values
                # Example - [{'url': 'https://media.rightmove.co.uk/15k/14258/93474227/14258_TheRidings_EPC_00_0000.pdf', 'caption': 'EPC 1'}]
                for epc in json["propertyData"]["epcGraphs"]:
                    if ".pdf" in epc["url"]:
                        property["rm_epc_cert_url"] = epc["url"]
                        # Break out of the loop if we have found a value as we only want one.
                        break
                    else:
                        # Continue the loop
                        continue
            else:
                return
        except Exception as e:
            logger.exception(str(e))
        
    def get_and_validate_page_for_url(self, property):
        # Get the property page.
        page = self.web_client.get_page_for_url(property["rm_property_url"])

        # Delete properties with a status of 410 or 404 which indicates that they have been removed
        # or no longer listed.
        if page.status_code == 404 or page.status_code == 410:
            # Clear out any sales history for a given property
            # Delete the property from the database.
            self.db.delete_sale_history_and_property((property["id"],))
            # return
            return

        # Check for a value of None or a non 200 status code.
        elif not page or page.status_code != 200:
            # Log the url and the status
            logger.info(f"No page or non successful status code url = {page.url}, status = {page.status_code}")
            # return
            return
        else:
            # Return a valid page.
            return page

    
    def process_properties_no_postcode_and_no_sold_nearby_url(self, properties):
        # Create a new property list placeholder.
        updated_properties = list()
        # Iterate through the properties list
        for index in range(len(properties)):
            try:
                logger.info(f"Getting Property {index + 1}/{len(properties)}")
                # Get the property from the list.
                property = properties[index]
                logger.info(property)

                # Get the property page.
                page = self.get_and_validate_page_for_url(property)
                # Check for am invalid page
                if not page:
                    # Continue to the next object
                    continue

                # Parse the individual property Page
                json = self.parse_property_page(page.text)
                # Check we have a valid json object or try the next property in the list.
                if not json:
                    continue

                # Process property sold nearby value extraction.
                self.get_and_set_property_sold_nearby_url(json, property)
                # Process Postcode Value Extraction
                self.get_and_set_property_postcode(json, property)
                # Process property Energy Performance Certificate extraction.
                self.get_property_epc_certificate_data(json, property)
                # Add the property object to our updated list.
                updated_properties.append(property)
            
            except Exception as e:
                logger.exception(str(e))
                continue
            
            finally:
                time.sleep(random.randint(0, 2))
        
        # Return the updated properties list.
        return updated_properties
    
    def process_properties_sold_stc_updates(self, properties):
        # Create a property sold stc change list placeholder.
        updated_sold_stc_properties = list()
        # Create an last accessed list
        last_accessed_properties = list()
        # Iterate through the properties list
        for index in range(len(properties)):
            try:
                logger.info(f"Getting Property {index + 1}/{len(properties)}")
                # Get the property from the list.
                property = properties[index]
                logger.info(property)
                
                # Get the property page.
                page = self.get_and_validate_page_for_url(property)
                # Check for am invalid page
                if not page:
                    # Continue to the next object
                    continue

                # Parse the individual property Page
                json = self.parse_property_page(page.text)
                # Check we have a valid json object or try the next property in the list.
                if not json:
                    continue
                
                # Get the soldSTC value
                sold_stc = self.get_sold_stc_status(json)

                # Add the property id to the last_accessed_properties list
                last_accessed_properties.append((property["id"],))

                # Compare for a None value and against the existing value.
                if sold_stc and sold_stc != property["rm_sold_stc"]:
                    logger.info(f'current Sold stc value = {sold_stc}, existing = {property["rm_sold_stc"]}')
                    # Update the property value
                    property["rm_sold_stc"] = sold_stc
                    # Update the updated_sold_stc_properties list.
                    updated_sold_stc_properties.append((property["id"], property["rm_sold_stc"]))
            
            except Exception as e:
                logger.exception(str(e))
                continue
            
            finally:
                time.sleep(random.randint(0, 2))
        
        # Return the updated properties list.
        return updated_sold_stc_properties, last_accessed_properties
        
    def get_postcode_sold_nearby_values_list(self, properties):
        # Create a list of tuples containing the property OrderedDictionary values.
        property_values_list = list()
        for index in range(len(properties)):
            p = properties[index]
            vals = p["id"], p["rm_postcode"], p["rm_sold_nearby_url"], p["rm_epc_cert_url"]
            # print(vals)
            property_values_list.append(vals)
        return property_values_list
    
    def process_properties_with_no_postcode_and_no_sold_nearby_url(self, properties):
        # Check that we have a valid list of properties, if not return.
        if not properties:
           return
        
        # Populate Postcode and sold nearby url data.
        properties = self.process_properties_no_postcode_and_no_sold_nearby_url(properties)
        
        # Get a value list of updates
        property_values = self.get_postcode_sold_nearby_values_list(properties)
        if not property_values:
            return
        
        logger.info(f"Number of properties for postcode and sold nearby value update = {len(property_values)}")
        
        # Update the properties in the database.
        self.db.update_property_postcode_sold_nearby_url_values(property_values)

    
    def process_properties_not_accessed_within_the_alotted_period(self, properties):
        # Check that we have a valid list of properties, if not return.
        if not properties:
           return
        
        # Process sold STC Updates
        properties_stc_update, last_accessed_properties = self.process_properties_sold_stc_updates(properties)
        
        if properties_stc_update:
            # Update the Database with updated sold stc values
            self.db.update_property_sold_stc_status(properties_stc_update)

        if last_accessed_properties: 
            # Process properties that we have successfully accessed and update the last_accessed_timestamp
            self.db.update_property_last_accessed(last_accessed_properties)


    def run(self):

        # Forever Loop
        while not self.running.is_set():
            try:
                # Get Properties sold stc with no postcode and no sold nearby url
                properties = self.db.get_properties_with_no_postcode()

                # Process Properties
                self.process_properties_with_no_postcode_and_no_sold_nearby_url(properties)

                # Get Properties that have not been accessed with the alotted period.
                properties = self.db.get_properties_not_accessed_within_alloted_time()

                # Process properties not accessed within the alotted period.
                self.process_properties_not_accessed_within_the_alotted_period(properties)

            except Exception as e:
                logger.exception(str(e))
            
            finally:
                logger.info("Sleeping")
                time.sleep(self.sleep_time)
        logger.info("Exited while loop gracefully")


        
    
