import requests
from bs4 import BeautifulSoup

class Epc:
    """
    This class provides an interface to the government Energy Performance Certificate Database
    via its web url. The class is to used to retrieve EPC data for a given postcode. The data available includes
    the Energy Rating, the date of certificate expiry and the property address.
    EPC certificates are valid for ten years, and properties older than this will need to have a new EPC
    prior to being marketed. It is common for properties to obtain a new EPC just prior to going onto the market,
    therefore the validity of the certificate can given an indication to a particular property having been added
    at a similar time (minus ten years). 
    """

    def __init__(self, epc_postcode_url, epc_validity):
        # Post Code Url
        self.epc_postcode_url = epc_postcode_url    
        # Epc Validty in Years
        self.epc_validity = epc_validity

    def get_epcs_for_postcode(self, postcode):
        """
        Method carries out the steps required to return a list of objects comprising (Address, Rating, Date).
        """
        try:
            # Make the web request
            page = self.make_web_request_for_epcs_for_postcode(postcode)

            # Check the Status Code
            if page.status_code != 200:
                return None
            
            # Parse the Web request
            results = self.parse_web_request_for_epcs_for_postcode(page)

            # Filter out expired EPC's and return.
            return self.remove_objects_with_expired_certificates(results)
        
        except Exception as e:
            print(str(e))
            return None     

    
    def make_web_request_for_epcs_for_postcode(self, postcode):
        """
        This method returns a requests object response containing the html for the page for a given postcode search.
        Parameters:
        name - type - example
        ---------------------------
        postcode - String - "CM14FF"
        """
        return requests.get(
            url=self.postcode_url.format(postcode)
        )
    
    def parse_web_request_for_epcs_for_postcode(self, page, items=2):
        """
        This method parses a web page using Beautiful soup HTML parser, returning a list of tuple
        objects comprising (Address, Rating, Date).
        Parameters:
        name - type - example
        ---------------------------
        page - requests object - Html bytes

        Return:
        list of tuples containing (address, rating and date objects).
        [
        ('54 TORQUAY ROAD, CHELMSFORD, CM1 7NX', ['C', '11 March 2031']),
        ('50, Torquay Road, CHELMSFORD, CM1 7NX', ['D', '12 March 2019 (expired)'])
        ]
        """
        try:
            soup = BeautifulSoup(page.content, "html.parser")
            # Break out the address components.
            address = [str(status.text).strip() for status in soup.find_all("a", {"class": "govuk-link"}) if "," in str(status.text).strip()]
            # The rating and the date are located within html tags with the same name.
            # Initial Dates and Ratings. 
            initial_dates_ratings = [str(date.text).strip() for date in soup.find_all("td", {"class": "govuk-table__cell"})]
            # Format to place the rating and the date into its own list.
            # ['C', '11 March 2031']
            formated_dates_ratings = [initial_dates_ratings[n:n + items] for n in range(0, len(initial_dates_ratings), items)]
        except Exception as e:
            print(str(e))
            # Return an empty List
            return list()
        else:
            # Join the address iterable and the dates and ratings.
            return list(zip(address, formated_dates_ratings))
    
    def remove_objects_with_expired_certificates(self, results):
        """
        Method returns a sanitised list of epc objects minus those whose EPC's have expired.
        Example:
        ('50, Torquay Road, CHELMSFORD, CM1 7NX', ['D', '12 March 2019 (expired)'])
        """
        return [result for result in results if "expired" not in result[1][1]]