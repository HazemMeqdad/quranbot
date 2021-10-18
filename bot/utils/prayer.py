
from __future__ import annotations
from requests import request
from bs4 import BeautifulSoup
from itertools import zip_longest

BASE = "https://timesprayer.com"


class PrayerManger(object):
    def __init__(self, data: dict):
        self.data = data

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

    def country(self) -> PrayerManger | dict:
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

    def city(self) -> PrayerManger | dict:
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

