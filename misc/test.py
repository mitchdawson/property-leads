import json
from pprint import pprint
import googlemaps
from geopy.geocoders import Nominatim

# # Define the Google Maps Api Key
google_geocode_api_Key = "AIzaSyDl7HjkgWVXQy8JgjyUro-F-4v3xrr4dlE"

# # Create the Google Maps Client.
gmaps = googlemaps.Client(key=google_geocode_api_Key)

# # Look up an address with reverse geocoding.
# reverse_geocode_result = gmaps.reverse_geocode((51.724316, 0.429032))

# print(reverse_geocode_result)

# Geopy Nominatim Example
geolocator = Nominatim(user_agent="test-user-agent")

# Open and Read the 1st page of the Results
html = open("res.html", "r").read()

# Break out the json data from within the page.
js = html.split("</div><script>window.jsonModel = ")[1].split("</script><script>")[0]

# Load the json string into a python dict.
my_json = json.loads(js)

# Break out the properties
properties = my_json["properties"]

# Break out the result count
result_count = my_json["resultCount"]
# print(result_count)

for p in properties:
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
    if prop.get("display_status") == "Sold STC":
        print("*" * 100)

        print(f'Latitude = {p["location"]["latitude"]}, Longitude = {p["location"]["longitude"]}')

        # Print Right Move Address
        print(f'RightMove = {prop["display_address"]}')

        # Create a Google Maps Reverse Geocode Query
        # gr = gmaps.reverse_geocode((prop["latitude"], prop["longitude"]))[0]["formatted_address"]

        # Create a Nomanitim Reverse Geocode Query
        location = geolocator.reverse(f'{prop["latitude"]}, {prop["longitude"]}', exactly_one=False)

        # print(prop["description"], prop["display_address"], prop["display_status"], prop["latitude"], prop["longitude"])
        # Create the Geocoder Instance
        #print(f'Google Result = {gr[0]["long_name"]}, {gr[1]["long_name"]}, {gr[2]["long_name"]}, {gr[3]["long_name"]}, {gr[4]["long_name"]}, {gr[6]["long_name"]}')
        # print(f'Google = {gr}')
        for l in location:
            print(f'Nomanitim = {l.raw}')

    # id = p["id"]
    # description = p["propertyTypeFullDescription"]
    # property_type = p["propertySubType"]
    # bedrooms = p["bedrooms"]
    # bathrooms = p["bathrooms"]
    # commercial = p["commercial"]
    # display_address = p["displayAddress"]
    # display_status = p["displayStatus"]
    # latitude = p["location"]["latitude"]
    # longitude = p["location"]["longitude"]
    # price = p["price"]["amount"]
    # first_visible_date = p["firstVisibleDate"]
