from requests import request
from bs4 import BeautifulSoup
from requests.models import Response


BASE = "https://sunnah.one"


class Sunnah(object):
    def __init__(self, query: str):
        self.query = query
        self.data = self._request().json()

    def _request(self) -> Response:
        re = request("GET", f"{BASE}/get.php?q={self.query}")
        self.data = re.json()
        return re

    def result(self) -> str:
        mytext = ""
        for item in self.data["data"]:
            for text in item:
                if isinstance(text, list):
                    continue
                content = str(text).split("<span class=\"search-keys\">")
                content = [i.replace("<span class=\"search-keys\">", "**") + "**" for i in content]
                suop = BeautifulSoup(" ".join(content).encode(), "lxml")
                mytext += suop.text + "\n"
            mytext += "\n"
        return mytext

    @property
    def url(self) -> str:
        return f"{BASE}/?s={self.query}"

    @property
    def count(self) -> int:
        return self.data["count"]

    def __repr__(self) -> str:
        return self.result()

