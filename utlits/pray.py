import typing as t
from datetime import datetime
import pytz
from .utlit import between_two_numbers
import json
import random


class Pray:
    AZAN_DATA = {
        "Fajr": {
            "name": "الفجر",
            "rakats": 2,
            "sunna_after": 0,
            "sunna_before": 2,
            "info": {
                "count_rakats": "ركعتان تؤدّيان بالفاتحة و السورة جهرا	",
                "tims": "من طلوع الفجر الى ما قبل بزوغ الشمس"
            }
        },
        "Dhuhr": {
            "name": "الظهر",
            "rakats": 4,
            "sunna_after": 2,
            "sunna_before": 4,
            "info": {
                "count_rakats": "4 ركعات : الركعتان الأولى و الثانية تؤدّيان بالفاتحة و السّورة سرّا\n"
                                "الركعتان الباقيتان بالفاتحة سرّا",
                "tims": "اثر زوال الشّمس مباشرة إلى أن يصير ظلّ كلّ شيء مثله"
            }
        },
        "Asr": {
            "name": "العصر",
            "rakats": 4,
            "sunna_after": 0,
            "sunna_before": 0,
            "info": {
                "count_rakats": "4 ركعات : الركعتان الأولى و الثانية تؤدّيان بالفاتحة و السّورة سرّا\n"
                                "الركعتان الباقيتان بالفاتحة سرّا",
                "tims": "من زيادة الظلّ عن مثله و يستمرّ الى غروب الشّمس"
            }
        },
        "Maghrib": {
            "name": "المغرب",
            "rakats": 3,
            "sunna_after": 2,
            "sunna_before": 0,
            "info": {
                "count_rakats": "3 ركعات الركعتان الأولى و الثانية بالفاتحة و السّورة جهرا\n"
                                "الركعة الأخيرة بالفاتحة فقط",
                "tims": "من مغيب جميع قرص الشمس الى مغيب الشّفق الأحمر."
            }
        },
        "Isha": {
            "name": "العشاء",
            "rakats": 4,
            "sunna_after": 2,
            "sunna_before": 0,
            "info": {
                "count_rakats": "4 ركعات: الرّكعتان الأولى و الثانية بالفاتحة و السّورة جهرا\n"
                                "الركعتان الباقيتان بالفاتحة فقط سرّا.",
                "tims": "من مغيب الشّفق الأحمر إلى طلوع الفجر."
            }
        }
    }

    @staticmethod
    def get_next_azan(azan: str) -> str:
        azan_list = list(Pray.AZAN_DATA.keys())
        azan_index = azan_list.index(azan)
        next_azan = azan_list[azan_index + 1] if azan_index + 1 < len(azan_list) else azan_list[0]
        return next_azan

    @staticmethod
    def format_time_str(time: str):
        h, m = int(time.split(":")[0]), int(time.split(":")[1])
        if h>12:
            h -= 12
            return "%02d:%02d PM" % (h, m)
        return "%02d:%02d AM" % (h, m)

    @staticmethod
    def get_colser_azan(timings: dict, now: datetime) -> t.Tuple[str, datetime]:
        for key, value in timings.items():
            if key not in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
                continue
            h = int(value.split(":")[0])
            m = int(value.split(":")[1])
            if h == now.hour and between_two_numbers(m, now.minute-2, now.minute+2):
                return key, value
        return None

    @staticmethod
    def get_next_azan_time(timings: t.Dict[str, str], timezone: str) -> t.Tuple[t.Optional[str], t.Optional[datetime]]:
        close_azan = None
        date = datetime.now(pytz.timezone(timezone))
        for azan in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            if timings[azan] > datetime(date.year, date.month, date.day, date.hour, date.minute+2).strftime("%H:%M"):
                close_azan = azan
                break
        if close_azan is None:
            return None, None
        h, m = int(timings[close_azan].split(":")[0]), int(timings[close_azan].split(":")[1])
        return close_azan, datetime.fromtimestamp(datetime(date.year, date.month, date.day).timestamp() + (h * 3600) + (m * 60))

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
