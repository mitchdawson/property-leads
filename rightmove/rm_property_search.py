# from enum import unique
import logging
logger = logging.getLogger(__name__)
#from requests import Session
import json
import time
from datetime import datetime
from collections import OrderedDict
from threading import Thread
from datetime import datetime
import random


class RightMovePropertySearch(Thread):

    """
    Rightmove class purpose is to retrieve property data from the rightmove website for a given search criteria.
    Typically there will be a search url which will yield a number of results in the webpage, data can be gleaned from this
    page however there maybe a requirement to interogate the individual property page as well.
    """

    def __init__(self, web_client, rm_maximum_results, rm_sleep_time, db, running, sleep_time):
        super().__init__()
        # Web Client Session
        self.web_client = web_client
        # Rightmove maximum yielded results
        self.rm_maximum_results = rm_maximum_results
        # Sleep Time between runs in seconds
        self.rm_sleep_time = rm_sleep_time
        # Datebase Connection
        self.db = db
        # Define the exit event placeholder
        self.running = running
        # Define a sleep time placeholder
        self.sleep_time = sleep_time

    
    def get_search_urls(self):
        # Get the urls from the database, this will contain the id of the url.
        urls_from_db = self.db.get_property_search_url_params()

        # Check if we have some urls or return.
        if not urls_from_db:
            logger.info(f"no urls returned")
            return

        # Get the id of the urls and hold in a seperate list.
        url_ids = [url["id"] for url in urls_from_db]
        logger.info(f"number of urls returned = {len(urls_from_db)}")
        
        # Filter any url parameters with values of None or keys such as "id".
        url_params_filtered = [{k: v for k, v in ups.items() if v is not None and k != "id"} for ups in urls_from_db]
            
        # Build the full urls
        urls = [self.web_client.create_url_for_parameters(url_param) for url_param in url_params_filtered]

        # Zip the url id's and the full url values into a dictionary
        ids_urls_dict = dict(zip(url_ids, urls))
        # logger.info(f"{ids_urls_dict}")

        # return the urls
        return ids_urls_dict

    def get_result_count_from_page(self, page):
        """
        Method returns the number of results that a given search has yielded.
        """
        # Break out the json data from the page and load into a python OrderedDict.
        try:

            js = json.loads(page.split("<script>window.jsonModel = ")[1].split("</script><script>")[0])
            # Get the result Count Value
            result_count = int(str(js["resultCount"]).replace(",", "").strip())
            # print(result_count)
            logger.info(f"result count from page = {result_count}")
            return result_count

        except Exception as e:
            logger.exception(str(e))
            return
    
    def scrape_all_properties_for_search_url(self, url):
        """
        This method obtains all of the properties for a given search, and is called
        after an initial call has been made to the search url to obtain the number
        of results that can be yielded.
        """
        # Unedited search url
        base_search_url = url
        
        # Create a place holder for the properties that have been parsed.
        parsed_properties = list()

        # Properties Processed counter
        parsed_properties_index = 0

        # Create the Result count counter
        result_count = 0

        # Process Variable
        process = True

        while process:
            try:
                time.sleep(random.randint(1, 10))
                logger.info(f"result_count = {result_count}")
                
                # Get the request object for the given url
                page = self.web_client.get_page_for_url(url)
                if not page or page.status_code != 200:
                    break

                # If the result count is zero, we need to extract the count from the search page.
                if not result_count:
                    logger.info("getting search results count")
                    # Get the number of search results available.
                    search_results = self.get_result_count_from_page(page.text)

                    # If we have a search result value and it is less than the maximum results that can be
                    # obtained from a search then update the result count value with the search results value.
                    if search_results and search_results < self.rm_maximum_results:
                        result_count = search_results
                    
                    # If we have a search result value and it is more than the maximum results that can be
                    # gained from a search then update the result count value with the maximum results value.
                    elif search_results and search_results >= self.rm_maximum_results:
                        result_count = self.rm_maximum_results

                    # Break if we cant get an accurate search result count value.
                    elif not search_results:
                        logger.info("breaking as no search result count could be obtained.")
                        # Break out if we were unable to obtain the number of properties available.
                        break
                
                # Extract the properties from the page of results.
                properties = self.extract_properties_from_page(page.text)
                # Check if we didnt return any results, then break out of the loop.
                if not properties:
                    break
                
                # If we have results then add these to the properties list.
                parsed_properties.extend(properties)
                logger.info(f"number of parsed properties in list = {len(parsed_properties)}")
                
                # Take the number of properties found (but not necessarily parsed) away from the result count.
                if len(properties) >= 24:
                    # Update the parsed properties index.
                    parsed_properties_index += 24
                    # Update the url with the index attribute.
                    url = base_search_url + f"&index={parsed_properties_index}"
                
                # Check if the number of results found is greater or equal to our desired result count, 
                # indicates completion.
                if len(parsed_properties) >= result_count:
                    break
            
            except Exception as e:
                logger.exception(str(e))

        return parsed_properties


    def extract_properties_from_page(self, page):
        """
        This method retrieves a page of property data and links and returns a result count and
        a list of property date in a list. The result count is used to determine how many pages of results there maybe.
        Rightmove will only ever yield 1000 results via web pages even though more may be present.
        Each page will contain 24 normal results and a featured property value which isnt included in the result count. 
        """
        # Break out the json data from the page and load into a python OrderedDict.
        try:
            js = json.loads(page.split("<script>window.jsonModel = ")[1].split("</script><script>")[0])
            # Return the "properties" element from the json.
            properties = js["properties"]
            logger.info(f"properties extracted = {len(properties)}")
            return properties
        except Exception as e:
            logger.exception(str(e))
            return

    def generate_property_objects(self, properties):
        """
        Method iterates through the returned rightmove properties list and creates
        new python OrderedDictionaries which mimic the database field names. We basically convert
        the rightmove data formatting to our own standard here.
        """
        # Create a place holder list
        properties_object_list = list()
        
        # Iterate through the returned properties.
        for p in properties:
            # Check for properties with a display_status of either Sold or Sold STC.
            # if not "Sold" in p.get("displayStatus"):
            #     continue

            # Check for Commercial Properties and skip them.
            if p["commercial"]:
                continue
            try:
                # Create an Ordered OrderedDictionary to hold our values.
                property = OrderedDict()

                # Create a property OrderedDictionary object.
                # Get the RightMove Property ID Value
                property["rm_property_id"] = p["id"]
                # Get the RightMove Property Description
                property["rm_description"] = p["propertyTypeFullDescription"]
                # Get the RightMove Property Type
                property["rm_property_type"] = p["propertySubType"]
                # Get the number of bedrooms listed
                property["rm_bedrooms"] = p["bedrooms"]
                # Get the number of bathrooms listed
                property["rm_bathrooms"] = p["bathrooms"]
                # Get the value of whether this is a commercial property
                property["rm_commercial"] = p["commercial"]
                # Get the website displayed address
                property["rm_display_address"] = p["displayAddress"]
                # Get the website displayed status (Sold STC)
                property["rm_display_status"] = p["displayStatus"]
                # Get the Latitude Coordinates
                property["rm_latitude"] = p["location"]["latitude"]
                # Get the Longitude Coordinates
                property["rm_longitude"] = p["location"]["longitude"]
                # Get the websites displayed listig price
                property["rm_listing_price"] = p["price"]["amount"]
                # Get the date that it was first uploaded / visible
                property["rm_first_visible_date"] = p["firstVisibleDate"]
                # Get the unique property refference url
                property["rm_property_url"] = p["propertyUrl"]

                # Add the propery object to the
                properties_object_list.append(property)
            except Exception as e:
                logger.exception(str(e))
                continue
        
        # Return the property object list.
        logger.info(f"property objects created = {len(properties_object_list)}")
        return properties_object_list
    
        
    def get_changed_status_values_list(self, changed_display_status):
        # Create a list of tuples containing the property OrderedDictionary values.
        changed_display_status_values_list = list()
        # Iterate through the objects and format the values into the correct positions
        for i in range(len(changed_display_status)):
            cds = changed_display_status[i]
            # Create a tuple to hold the values.
            t = (
                # rm_display_status
                cds["rm_display_status"],
                True,
                cds["rm_property_id"]
            )
            # Add to the list.
            changed_display_status_values_list.append(t)
        # Return changed_display_status_values_list
        return changed_display_status_values_list
    
    
    def get_new_properties_values_list(self, new_properties):
        # Create a list of tuples containing the property OrderedDictionary values.
        new_property_values_list = list() #[np.values() for np in new_properties]
        for np in new_properties:
            vals = tuple(np.values())
            new_property_values_list.append(vals)
        return new_property_values_list


    def filter_out_new_properties(self, scraped_property_objects, existing_property_objects):
        """
        This method takes the full list of scraped property objects and returns
        a new list of property objects of properties that are not already in the database.
        """
        # Create a list of existing rm_property_id's.
        rm_property_ids = [p["rm_property_id"] for p in existing_property_objects]
        # Create a placeholder for new properties.
        new_properties = list()
        # Iterate through the list of scraped property objects
        for i in range(len(scraped_property_objects)):
            try:
                # Get the object at position i.
                p = scraped_property_objects[i]
                # Check if the rm_property_id value is NOT already present in the database.
                if p["rm_property_id"] not in rm_property_ids:
                    # Add the property to the new_properties list.
                    new_properties.append(p)
            except Exception as e:
                print(str(e))
                continue
        # Return the new property object list.
        return new_properties
    
    def filter_out_sold_stc(self, sorted_scraped_properties_objects, existing_properties_from_db):
        """
        This method takes the list of scraped property objects and returns
        a new list of property objects of properties that have a display status which differs
        from the value held in the database.
        """
        # Define a placeholder for objects with changed display status values.
        sold_stc = list()
        # Iterate through the scaped_property_objects list.
        for i in range(len(sorted_scraped_properties_objects)):
            try:
                # Get a scraped property (sp) from the list at position i.
                sp = sorted_scraped_properties_objects[i]
                # Check for a display Status of "Sold STC"
                if sp["rm_display_status"] != "Sold STC":
                    continue
                # Iterate through the existing_properties_from_db objects.
                for j in range(len(existing_properties_from_db)):
                    # Get an existing property (ep) from the list at position j.
                    ep = existing_properties_from_db[j]
                    # Compare the rm_property_id's of the objects and the display status

                    if (
                        sp["rm_property_id"] == ep["rm_property_id"] and
                        sp["rm_display_status"] != ep["rm_display_status"]
                    ):
                        
                        # Add the scraped property object to the changed_display_status list.
                        sold_stc.append(sp)
            
            except Exception as e:
                print(str(e))
                continue
        logger.info(f"number of properties with a changed display status = {len(sold_stc)}")
        # Return the list of objects with changed display status values.
        return sold_stc
    
    def filter_duplicate_property_objects(self, property_objects):
        """
        Method removes duplicates dictionaries in a list. Returns a list of Orderedicts.
        """
        logger.info(f"number of scaped properties = {len(property_objects)}")
        
        # Create a list of unique property objects.
        unique_property_objects = [OrderedDict(t) for t in {tuple(d.items()) for d in property_objects}]
        logger.info(f"number of unique scaped properties = {len(unique_property_objects)}")

        # Return the unique_property_objects
        return unique_property_objects
    
    def process_new_properties(self, unique_scraped_property_objects, existing_property_objects):
        """
        This method takes the full list of scraped property objects and filters out new
        properties for insertion into the database, aswell as identifying existing properties that have attributes
        which have changed and now need to be reflected in the database.
        """
        logger.info(f"Number of existing properties = {len(existing_property_objects)}")
        if not unique_scraped_property_objects:
            return

        # If we have existing properties in the database.
        if existing_property_objects:
            # Get a list of new properties that can be inserted into the database. This method will also filter
            # properties removing new properties from the scraped objet list.
            new_properties = self.filter_out_new_properties(unique_scraped_property_objects, existing_property_objects)
        else:
            # If there are no pre existing properties in the database then all properties are new.
            new_properties = unique_scraped_property_objects

        # Get a list of new property values.
        new_properties_values_list = self.get_new_properties_values_list(new_properties)
        logger.info(f"new properties values = {len(new_properties_values_list)}")
        
        # Insert new properties to the DB. returns an integer of the rows inserted.
        insert_new_properties = self.db.insert_new_properties(new_properties_values_list)
        logger.info(f"new properties inserted into the database = {insert_new_properties}")

    
    def process_sold_stc_updates(self, unique_scraped_property_objects, existing_property_objects):
        """
        This method takes the full list of scraped property objects and filters out new
        properties for insertion into the database, as well as identifying existing properties that have attributes
        which have changed and now need to be reflected in the database.
        """
        if not unique_scraped_property_objects:
            return
        # Get a list of properties with a display status which has changed.
        sold_stc = self.filter_out_sold_stc(
            unique_scraped_property_objects, existing_property_objects
        )
        logger.info(f"properties with a display status change = {len(sold_stc)}")

        # If there are no updates then return.
        if not sold_stc:
            return
        
        # Get a list changed status values
        sold_stc_status_values = self.get_changed_status_values_list(sold_stc)
        logger.info("got property display status values list")
        logger.info(sold_stc_status_values)
        
        # Update the datebase with the required changes.
        sold_stc_updates = self.db.update_property_sold_stc(sold_stc_status_values)
        logger.info(f"number of property display status updates = {sold_stc_updates}")


    def process_search_urls(self, ids_urls_dict):
        """
        This method takes a list of search urls and performs the steps necessary to 
        extract all available properties, convert those values to python objects of our own
        format, insert into the database and perform updates to existing objects in the database as
        required.
        """
        # Return if no urls were passed in.
        if not ids_urls_dict:
            return
        
        # Create a placeholder for all scraped properties.
        scraped_properties = list()

        # Placeholder for urls that were successfull accessed.
        accessed_url_ids = list()
        
        # Iterate through the urls;
        for id, url in ids_urls_dict.items():
            try:
                # Extend the scraped_properties list to include the returned properties for the url.
                scraped_properties.extend(self.scrape_all_properties_for_search_url(url))
                # Update the last accessed value for the url
                # self.db.update_url_accessed([(id,)])
                accessed_url_ids.append((id, str(datetime.now())))
                # Insert a random pause between each url.
                time.sleep(random.randint(1, 10))
            except Exception as e:
                logger.exception(str(e))
                continue             
        
        # Check we have some values, if not return.
        if not scraped_properties:
            return
        
        # Convert to our own property object format.
        scraped_property_objects = self.generate_property_objects(scraped_properties)

        # Sort the scraped objects by filtering our duplicates
        unique_scraped_property_objects = self.filter_duplicate_property_objects(scraped_property_objects)

        # Get the existing properties from the database.
        existing_property_objects = self.db.get_id_rm_property_id_display_status()
        
        # Process new propeties and update existing ones.
        self.process_new_properties(unique_scraped_property_objects, existing_property_objects)

        # Process display status changes
        self.process_sold_stc_updates(unique_scraped_property_objects, existing_property_objects)

        # Update the urls "accessed" attribute to reflect successful access.
        self.db.update_url_accessed(accessed_url_ids)


    def run(self):

        # Forever Loop
        while not self.running.is_set():
            try:
                # Get the search urls
                ids_urls_dict = self.get_search_urls()
                
                # Process the retrieved urls.
                self.process_search_urls(ids_urls_dict)

            except Exception as e:
                logger.exception(str(e))
            finally:
                logger.info("Sleeping")
                time.sleep(self.sleep_time)
        logger.info("Exited while loop gracefully")