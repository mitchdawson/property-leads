from requests import Session
from bs4 import BeautifulSoup
import json
import time
import csv
from geopy.geocoders import Nominatim
import googlemaps
from pprint import pprint
from datetime import datetime

RADIUS = 1.0
BASE_URL = "https://rightmove.co.uk"
SEARCH_STRING = f"/property-for-sale/find.html?locationIdentifier=REGION%5E307&radius={RADIUS}&propertyTypes=detached%2Csemi-detached%2Cterraced&primaryDisplayPropertyType=houses&includeSSTC=true&mustHave=&dontShow=&furnishTypes=&keywords="
# Define the Google Maps Api Key
google_geocode_api_Key = "AIzaSyDl7HjkgWVXQy8JgjyUro-F-4v3xrr4dlE"

# Create the Google Maps Client.
gmaps = googlemaps.Client(key=google_geocode_api_Key)

# Requests Session Headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


class RightMoveCrawler:

    def __init__(self, base_url, search_string):
        self.base_url = base_url
        self.search_string = search_string
        # This is the total number of properties found by the search.
        self.result_count = 0
        self.properties_parsed = 0
        self.properties_list = list()
        self.session = Session()
        self.session.headers = headers
    
    def get_url(self):
        # Check if the result_count variable is zero indicating that no requests have been made, in which case the main url is unaltered.
        # Otherwise we need to add the index parameter. i.e. index=48 (increments of 24).
        if self.result_count == 0:
            return self.base_url + self.search_string
        else:
            return self.base_url + self.search_string + f"&index={self.properties_parsed}"

    def fetch(self):
        # Make and return the Web request.
        return self.session.get(self.get_url())


    def parse_main_page(self, page):
        """
        This method parses a page which contains many properties. The aim is to extract and store certain information
        to be able to confirm the status of the property as SOLD or SOLD STC.
        """

        # Break out the json data from the page and load into a python dict.
        try:
            js = json.loads(page.split("</div><script>window.jsonModel = ")[1].split("</script><script>")[0])
        
        except Exception as e:
            print(str(e))
            print(page)
            return

        # Break out the result count on the first request only. This is the number of results returned for
        # the given url search.
        if self.result_count == 0:
            self.result_count = int(str(js["resultCount"]).replace(",", "").strip())
            print(f"Number of Potential Properties Found = {self.result_count}")

        # Break out the properties.
        properties = js["properties"]
        
        # Check that we have some valid properties returned to us in the json. If there are not properties then return.
        if len(properties) == 0:
            return
        
        # Iterate through the returned properties.
        for p in properties:
            # Check for properties with a display_status of either Sold or Sold STC.
            if not "Sold" in p.get("displayStatus"):
                continue
            
            # Create a property dictionary object.
            prop = {
                "id": p["id"],
                "description": p["propertyTypeFullDescription"],
                "property_type": p["propertySubType"],
                "bedrooms": p["bedrooms"],
                "bathrooms": p["bathrooms"],
                "commercial": p["commercial"],
                "display_address": p["displayAddress"],
                "display_status": p["displayStatus"],
                "latitude": p["location"]["latitude"],
                "longitude": p["location"]["longitude"],
                "price": p["price"]["amount"],
                "first_visible_date": p["firstVisibleDate"],
                "url": p["propertyUrl"]
            }

            # Add the property object to the properties_list.
            self.properties_list.append(prop)
        
        # Update the number of properties that have been Parsed.
        self.properties_parsed += len(properties) - 1
    
    def process_individual_property(self):
        """
        This method takes a property and loads the individual property page in order to obtain additional 
        information such as the Energy Performance Certificate (EPC) details, and the full postcode. 
        """
        print("Getting individual Property Page")
        # Iterate through the properties list
        for index in range(len(self.properties_list)):
            print(f"Getting Property {index}/{len(self.properties_list)}")
            # Get the property from the list.
            p = self.properties_list[index]
            # Get the property page.
            page = self.get_individual_propery_page(p)
            # Parse the individual property Page
            self.parse_individual_property_page(page.text, p)

    def get_individual_propery_page(self, property_dict):
        return self.session.get(self.base_url + property_dict["url"])
    
    def parse_individual_property_page(self, page, property):
        # Break out the json data from the page and load into a python dict.
        try:
            # print(page.split("window.PAGE_MODEL = ")[1].split("</script>")[0])
            js = json.loads(page.split("window.PAGE_MODEL = ")[1].split("</script>")[0])
            #["propertyData"]
        except Exception as e:
            print(str(e))
            # print(page)
            return
        print("*" * 150, "\n")
        # pprint(js)

        # Obtain the postcode element from the json.
        property["postcode"] = js["analyticsInfo"]["analyticsProperty"]["postcode"]
        
        # Check if the value of ["address"]["deliveryPointId"] value is an integer.
        if (
            # Check for an Interger Value.
            type(js["propertyData"]["address"]["deliveryPointId"]) == int and \
            # Length should be 8 digits long.
            len(str(js["propertyData"]["address"]["deliveryPointId"])) == 8
        ):
            # Add the "deliveryPointId" key to the property Dictionary.
            property["deliveryPointId"] = js["propertyData"]["address"]["deliveryPointId"]
        else:
            # Add a value of None
            property["deliveryPointId"] = None
        
        # Set a default value of None on property["epcGraphs"] = None.
        property["epcGraphs"] = None
        # Get the value contained within the "epcGraphs" list value if it is not empty.
        if js["propertyData"]["epcGraphs"]:
            # We want to filter out PDF files with the url values
            # Example - [{'url': 'https://media.rightmove.co.uk/15k/14258/93474227/14258_TheRidings_EPC_00_0000.pdf', 'caption': 'EPC 1'}]
            for epc in js["propertyData"]["epcGraphs"]:
                if ".pdf" in epc["url"]:
                    property["epcGraphs"] = epc["url"]
                    # Break out of the loop if we have found a value as we only want one.
                    break
                else:
                    # Continue the loop
                    continue
        return

    def get_address_from_nominatim(self):
        print("Nominatim Client Starting...")
        # Create the Instance of the Nominatim class.
        geolocator = Nominatim(user_agent="test-user-agent")
        # Iterate through the properties list
        for index in range(len(self.properties_list)):
            print(f"Getting Address {index}/{len(self.properties_list)}")
            p = self.properties_list[index]
            # Create a Nomanitim Reverse Geocode Query
            location = geolocator.reverse(f'{p.get("latitude")}, {p.get("longitude")}')
            # Add a new key to the propert Dictionary
            p["geocode Address"] = location.address
        print("Nominatim Client Finished...")

    def get_address_from_google_maps(self):
        print("Google Maps Client Starting...")
        # Create the Google Maps Client.
        gmaps = googlemaps.Client(key=google_geocode_api_Key)
        # Iterate through the properties list
        for index in range(len(self.properties_list)):
            print(f"Getting Address {index}/{len(self.properties_list)}")
            p = self.properties_list[index]
            # # Look up an address with reverse geocoding.
            location = gmaps.reverse_geocode((p.get("latitude"), p.get("longitude")))[0]
            # Add a new key to the propert Dictionary
            p["googlemaps Address"] = location["formatted_address"]

    def to_csv(self):
        print("Writing Results To CSV...")
        # Create a datetime stamp.
        date = datetime.now().strftime("%Y_%m_%d_%I_%M_%S_%p")
        # Open up the output file object
        with open(f"results_{date}.csv", "w", newline='', encoding='utf-8') as results_file:
            writer = csv.DictWriter(results_file, fieldnames=self.properties_list[0].keys())
            # Write the header rows.
            writer.writeheader()
            writer.writerows(self.properties_list)
        
        print("Results Written...")

    def run(self):

        while True:

            # Get the Web Page
            page = self.fetch()

            # Parse the returned Page
            self.parse_main_page(page.text)

            # Print the Number of Properties Parsed.
            print(f"Number of Properties Parsed = {self.properties_parsed}")

            # Print the number of Sold / Sold STC Properties Found
            print(f"Number of Sold / Sold STC Properties = {len(self.properties_list)}")

            # Check if we have parsed all available properties.
            if self.properties_parsed > 200:
                # Break out of the while loop.
                break

            # sleep for 0.5 seconds
            time.sleep(0.5)
            
        # Carry out post fetch processing.

        # Get the Addresses from the Geocode Nominatim Client
        self.get_address_from_nominatim()

        # Get the Address from Google Maps
        self.get_address_from_google_maps()

        # Process Individual Property Info
        self.process_individual_property()



        # Write results to CSV.
        self.to_csv()





        # # Get the Initial Page
        # response = self.fetch()
        # # print(response.text)
        # # with open("res.html", "w") as html_file:
        # #     html_file.write(response.text)
        # # html = open("res.html", "r").read()
        # # print(html)

        # self.parse(response.text)


def main():
    
    rmc = RightMoveCrawler(BASE_URL, SEARCH_STRING)

    rmc.run()


if __name__ == "__main__":
    main()