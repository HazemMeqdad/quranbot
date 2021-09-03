from requests import request
from bs4 import BeautifulSoup
from itertools import zip_longest

BASE = "https://timesprayer.com"


class Prayer(object):
    def __init__(self, country):
        self._country = country

    def __repr__(self):
        return "DwcTeam"

    def country(self) -> dict:
        r = ["fjer", "sunrise", "noon", "pressing", "moroccan", "supper"]
        re = request("GET", f"{BASE}/prayer-times-cities-{self._country}.html")
        if re.text == "Not found":
            return {"msg": "Not found"}
        soup = BeautifulSoup(re.content, "lxml")
        div = soup.find("div", {"class": "col6 prayertable mobile"})
        _json = {
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
        _json.update(new)
        return _json

    def city(self) -> dict:
        r = ["fjer", "sunrise", "noon", "pressing", "moroccan", "supper"]
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
