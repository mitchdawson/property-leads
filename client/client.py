import logging
logger = logging.getLogger(__name__)
from requests import Session
from urllib.parse import urlencode, urljoin
# import requests
import time
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class WebClient:
    """
    Client is used to create to persistent web connection to the RightMove website. 
    The associated methods carry out specific tasks required for obtaining certain elements
    of data.
    """

    def __init__(self, rm_base_url, request_headers):
        # Rightmove base url
        self.rm_base_url = rm_base_url
        # Create the Requests Session.
        self.rightmove_session = Session()
        # Apply the custom headers.
        self.rightmove_session.headers = request_headers
    
    def get_page_for_url(self, url):
        """
        Method will join the url passed in to the base_url value on the class, before
        retrieving the given web page and returning the result.
        """
        count = 0
        result = None
        while count < 3:
            try:
                request = self.rightmove_session.get(self.rm_base_url + url, timeout=(3.5, 5))
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

    def create_url_for_parameters(self, parameters):
        path = f"/property-for-sale/find.html"
        query = "?" + urlencode(parameters)
        return urljoin(path, query)