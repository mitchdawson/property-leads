import csv
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import InvalidInputError, RateLimitExceededError, UnknownError

api_key = "2f5caae0240c4d2fa3cba125454024ab"
geocoder = OpenCageGeocode(api_key)

with open("results_file.csv", "r", newline="") as input:
    reader = [row for row in csv.DictReader(input)]

for p in reader:
    try:
        location = geocoder.reverse_geocode(p.get("latitude"), p.get("longitude"))
    except Exception as e:
        print(str(e))
    else:
        if location and len(location):
            print("Got Address")
            p["opencage address"] = location[0]["formatted"]

with open("new_results.csv", "w", newline="", encoding="utf-8") as output:
    writer = csv.DictWriter(output, fieldnames=reader[0].keys())
    # Write the header rows.
    writer.writeheader()
    writer.writerows(reader)