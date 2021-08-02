import googlemaps
from datetime import datetime
from pprint import pprint

lat = 51.724316
lon = 0.429032

google_geocode_api_Key = "AIzaSyDl7HjkgWVXQy8JgjyUro-F-4v3xrr4dlE"
gmaps = googlemaps.Client(key=google_geocode_api_Key)

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((lat, lon))
pprint(reverse_geocode_result[0]["formatted_address"])

# Geopy Nominatim example
# from geopy.geocoders import Nominatim
# geolocator = Nominatim(user_agent="test-user-agent")
# location = geolocator.reverse(f"{lat}, {lon}")
# print(location)