import requests

d = {
    "locationIdentifier": "REGION^307",
    "minPrice": 500000,
    "maxPrice": 800000,
    "radius": 10.0,
    "propertyTypes": "detached",
    "primaryDisplayPropertyType": "detached",
    "includeSSTC": "true",
    "dontShow": "sharedOwnership,retirement,newHome"
}

url = "https://rightmove.co.uk/property-for-sale/find.html"

r = requests.get(url, params=d)
print(r.url)
print(r.status_code)