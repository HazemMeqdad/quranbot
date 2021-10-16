
# BASE = "https://timesprayer.com/ajax.php"


# """
# do=search&
# language=ar&
# lat=40.7642323&
# lng=-73.9722201&
# long_name=New%2520York&
# short_name=New%2520York&
# formatted_address=5%2520E%252059th%2520St%2C%2520New%2520York%2C%2520NY%252010022%2C%2520USA&
# country_long_name=United%2520States&
# country_short_name=US&
# full_result=%255B%257B%2522long_name%2522%3A%25225%2522%2C%2522short_name%2522%3A%25225%2522%2C%2522types%2522%3A%255B%2522street_number%2522%255D%257D%2C%257B%2522long_name%2522%3A%2522East%252059th%2520Street%2522%2C%2522short_name%2522%3A%2522E%252059th%2520St%2522%2C%2522types%2522%3A%255B%2522route%2522%255D%257D%2C%257B%2522long_name%2522%3A%2522Manhattan%2522%2C%2522short_name%2522%3A%2522Manhattan%2522%2C%2522types%2522%3A%255B%2522political%2522%2C%2522sublocality%2522%2C%2522sublocality_level_1%2522%255D%257D%2C%257B%2522long_name%2522%3A%2522New%2520York%2522%2C%2522short_name%2522%3A%2522New%2520York%2522%2C%2522types%2522%3A%255B%2522locality%2522%2C%2522political%2522%255D%257D%2C%257B%2522long_name%2522%3A%2522New%2520York%2520County%2522%2C%2522short_name%2522%3A%2522New%2520York%2520County%2522%2C%2522types%2522%3A%255B%2522administrative_area_level_2%2522%2C%2522political%2522%255D%257D%2C%257B%2522long_name%2522%3A%2522New%2520York%2522%2C%2522short_name%2522%3A%2522NY%2522%2C%2522types%2522%3A%255B%2522administrative_area_level_1%2522%2C%2522political%2522%255D%257D%2C%257B%2522long_name%2522%3A%2522United%2520States%2522%2C%2522short_name%2522%3A%2522US%2522%2C%2522types%2522%3A%255B%2522country%2522%2C%2522political%2522%255D%257D%2C%257B%2522long_name%2522%3A%252210022%2522%2C%2522short_name%2522%3A%252210022%2522%2C%2522types%2522%3A%255B%2522postal_code%2522%255D%257D%255D
# """


from requests import request
from bs4 import BeautifulSoup
from itertools import zip_longest

BASE = "https://timesprayer.com"


class PrayerManger(object):
    def __init__(self, data: dict):
        self.data = data
        super().__init__()

    @property
    def description(self):
        return self.data.get("description")
    
    @property
    def url(self):
        return self.data.get("url")
    
    @property
    def fjer(self):
        return self.data.get("fjer")
    
    @property
    def sunrise(self):
        return self.data.get("sunrise")
    
    @property
    def noon(self):
        return self.data.get("noon")
    
    @property
    def pressing(self):
        return self.data.get("pressing")
    
    @property
    def moroccan(self):
        return self.data.get("moroccan")
    
    @property
    def isha(self):
        return self.data.get("isha")

class Prayer(object):
    def __init__(self, country):
        self._country = country

    def __repr__(self):
        return "DwcTeam"

    def country(self) -> PrayerManger:
        r = ["fjer", "sunrise", "noon", "pressing", "moroccan", "isha"]

        re = request("GET", f"{BASE}/prayer-times-cities-{self._country}.html")
        if re.text == "Not found":
            return {"msg": "Not found"}

        soup = BeautifulSoup(re.content, "lxml")
        div = soup.find("div", {"class": "col6 prayertable mobile"})
        data = {
            "description": div.find("h3").text,
            "url": f"{BASE}/prayer-times-cities-{self._country}.html"
        }
        n = []
        for i in div.find_all("tr"):
            l = [z.text for z in i.find_all("td")]
            if l == []:
                continue
            n.append(l[1])

        new = zip_longest(r, n)

        data.update(new)
        return PrayerManger(data)

    def city(self) -> PrayerManger:
        r = ["fjer", "sunrise", "noon", "pressing", "moroccan", "isha"]
        re = request("GET", f"{BASE}/prayer-times-in-{self._country}.html")
        if re.text == "Not found":
            return {"msg": "Not found"}
        soup = BeautifulSoup(re.content, "lxml")
        div = soup.find("div", {"class": "info prayertable mobile"})
        _json = {
            "description": div.find("h2").text,
            "url": f"{BASE}/prayer-times-in-{self._country}.html"
        }
        n = []
        for i in div.find_all("ul"):
            l = [z.text for z in i.find_all("li")]
            if l == []:
                continue
            for g in l:
                n.append(g.split(" ", 2)[2])
        new = zip_longest(r, n)
        _json.update(new)
        return _json

