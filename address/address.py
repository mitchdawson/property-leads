import logging
from requests import Session
logger = logging.getLogger(__name__)
from requests import Session
import time

class AddressValidator:

    def __init__(self, nom_base_url, request_headers, db, running, sleep_time):
        # Rightmove base url
        self.nominatim_base_url = nom_base_url
        # Create the Requests Session.
        self.nominatim_session = Session()
        # Apply the custom headers.
        self.nominatim_session.headers = request_headers
        # Ignore Certificate Validation
        self.nominatim_session.verify = False
        # Datebase Connection
        self.db = db
        # Define the exit event placeholder
        self.running = running
        # Define a sleep time placeholder
        self.sleep_time = sleep_time

    def get_page_for_url(self, url):
        """
        Method will join the url passed in to the base_url value on the class, before
        retrieving the given web page and returning the result.
        """
        count = 0
        result = None
        while count < 3:
            try:
                request = self.nominatim_session.get(self.nominatim_base_url + url, timeout=(3.5, 5))
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
    
    def make_request_convert_response_json(self, url):
        """
        This method handles making and validate the web request and passing back
        None or a python dict of json back the the caller.
        """
        try:
        
            # Get the page for the given url.
            request = self.get_page_for_url(url)

            # Check the response for a None type or non 200 status code.
            if not request or request.status_code != 200:
                return
            
            # Convert the json to a python dict.
            js =  request.json()

        except Exception as e:
            logger.exception(str(e))
            return
        
        else:
            # Return the dict
            return js
        
    
    def get_address_for_postcode(self, postcode):
        """
        This method combines the get_lat_and_long_for_postcode & get_address_for_lat_and_long methods
        to obtain an address (up to the road) for a given postcode. The address response from Nominatim
        will contain elements such as the road, suburb, city, county etc.
        """
        # First obtain the lat and long coordinates, 
        # these are used to obtain the address object later.
        js = self.get_lat_and_long_for_postcode(postcode)

        # Check the response
        if not js:
            return
        
        # Extract the Lat and Lon values. These will be None if not present.
        lat = js.get('lat')
        lon = js.get('lat')

        # Check for None types
        if not (lat and lon):
            return
        
        # Pass the lat and lon values to the get_address_for_lat_and_long method.
        return self.get_address_for_lat_and_long(lat, lon)

    
    def get_lat_and_long_for_postcode(self, postcode):
        """
        This method requests longitude and latitude values for a given postcode from the nominatim api.

        Example Response:

        0	
        place_id	259716909
        licence	"Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright"
        boundingbox	
        0	"51.580735646009"
        1	"51.900735646009"
        2	"0.35254258050131"
        3	"0.67254258050131"
        lat	"51.740735646009405"
        lon	"0.5125425805013116"
        display_name	"Springfield, Chelmsford, Essex, East of England, England, CM2 6YZ, United Kingdom"
        class	"place"
        type	"postcode"
        importance	0.325
        """
        # Define the url search portion
        url = f"/search?&postalcode={postcode}&format=json"

        # Make the request to the api and return the result
        return self.make_request_convert_response_json(url)

    def get_address_for_lat_and_long(self, lat, lon):
        """
        This method requests an address object based on previously obtained longitude and latitude values.
        
        Example Response:

        place_id	110505694
        licence	"Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright"
        osm_type	"way"
        osm_id	93169586
        lat	"51.74081698566567"
        lon	"0.5125455415840944"
        display_name	"Silvester Way, Chancello…CM2 6YZ, United Kingdom"
        address	
        road	"Silvester Way"
        neighbourhood	"Chancellor Park"
        suburb	"Springfield"
        city	"Chelmsford"
        county	"Essex"
        state_district	"East of England"
        state	"England"
        postcode	"CM2 6YZ"
        country	"United Kingdom"
        country_code	"gb"
        boundingbox	
        0	"51.7402801"
        1	"51.7414385"
        2	"0.512291"
        3	"0.5133474"
        """
        # Define the url search portion
        url = f"/reverse?lat={lat}&lon={lon}&format=json"

        # Make the request to the api and return the result
        return self.make_request_convert_response_json(url)
    

    def run(self):
        # Forever Loop
        while not self.running.is_set():
            try:
                # Get properties with a real address or epc address
                pass


            except Exception as e:
                logger.exception(str(e))
            
            finally:
                logger.info("Sleeping")
                time.sleep(self.sleep_time)

        logger.info("Exited while loop gracefully")



