from bs4 import BeautifulSoup
import requests
import itertools
from datetime import datetime, timedelta


def main():
    url = "https://find-energy-certificate.digital.communities.gov.uk/find-a-certificate/search-by-postcode?postcode=CM17NX"

    r = requests.get(url)

    soup = BeautifulSoup(r.content, "html.parser")

    address = [str(status.text).strip() for status in soup.find_all("a", {"class": "govuk-link"}) if "," in str(status.text).strip()]
    valid_dates = [str(date.text).strip() for date in soup.find_all("td", {"class": "govuk-table__cell"})]

    # chks = list(itertools.grouper(valid_dates, 2))
    N = 2
    new_dates = [valid_dates[n:n + N] for n in range(0, len(valid_dates), N)]
    # print(address)
    # print(valid_dates, "\n")
    # print(new_dates)

    # tes = [list(itertools.chain(*i)) for i in zip(address, new_dates)]
    # print(tes)
    tes = list(zip(address, new_dates))
    print(tes)
    # for t in tes:
    #     print(t[0], t[1][0], t[1][1])

    # Example Right Move first seen timetamp
    first_seen_ts = "2020-05-05T14:46:47Z".split("T")[0]
    first_seen_dtf = "%Y-%m-%d"

    # Example ECP Date Stamp
    epc_ts = "11 March 2031"
    epc_tsf = "%d %B %Y"

    first_seen_dt = datetime.strptime(first_seen_ts, first_seen_dtf)
    epc_dt = datetime.strptime(epc_ts, epc_tsf)

    # Epc Time Delta (datetime minus 10 years for certificate validity)
    # epc_td = epc_dt - timedelta(days=3650)
    epc_td = epc_dt.replace(year=epc_dt.year - 10) # Removes ten from the years rathern than in days.

    # Time Delta
    delta = epc_td - first_seen_dt
    print(delta.days)

if __name__ == "__main__":
    main()