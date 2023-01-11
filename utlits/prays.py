import random 
from datetime import datetime
import json

times = {1800: "30m", 3600: "1h", 7200: "2h",
             21600: "6h", 43200: "12h", 86400: "24h"}

def get_pray():
    with open("json/prays.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    random_type = random.choice(list(data.keys()))
    prays = data[random_type]
    date = datetime.now()
    if random_type == "azkar":
        pray_list = prays
        if date.hour <= 10:
            pray_list = list(filter(lambda x: x["category"] == "أذكار الصباح", prays))
        if date.hour >= 18:
            pray_list =list (filter(lambda x: x["category"] == "أذكار المساء", prays))
        return random.choice(pray_list)
    return random.choice(data[random_type])
