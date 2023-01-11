import typing as t
from datetime import datetime
import pytz
import discord
import lavalink
import json
import random
from .buttons import SupportButtons, BaseView

times = {1800: "30m", 3600: "1h", 7200: "2h",
             21600: "6h", 43200: "12h", 86400: "24h"}

def convert_number_to_000(number: int) -> str:
    if number < 10:
        return "00" + str(number)
    elif number < 100:
        return "0" + str(number)
    else:
        return str(number)

def between_two_numbers(num: int, a: int, b: int):
    """
    True if the number is between the two numbers, False if not
    """
    if a < num and num < b: 
        return True
    else: 
        return False


HELP_DATA = {
    "main": {
        "title": "الصفحة الرئيسية",
        "description": ("**بسم الله الرحمن الرحيم**\n"
                    "بوت فاذكروني اول بوت عربي اسلامي للأذكار, البوت "
                    "يمكنه تشغيل القرآن الكريم بالقنوات الصوتيه و أرسال الأذكار"
                    "و الأدعية بشكل دوري, البوت غير ربحي و اهدافه خالصه لله عز و جل."
                    "\n\nيمكنك من الأسفل أختيار الأوامر"
                    ),
        "cog": None
    },
    "general": {
        "title": "الأوامر العامة",
        "description": "يمكن للعامة أستخدامها و متاحة للجميع",
        "cog": "general"
    },
    "moshaf": {
        "title": "أوامر المصحف الشريف", 
        "description": "يمكن ل أوامر المصحف الشريف فتح القرآن الكريم بالصور و أيضاً تثبيت رساله للمصحف",
        "cog": "moshaf"
    },
    "hijri": {
        "title": "أوامر التاريخ الهجري",
        "description": "يمكن ل أوامر التاريخ الهجري تحويل التاريخ الهجري إلى التاريخ الميلادي و عكسه",
        "cog": "hijri"
    },
    "quran_voice": {
        "title": "أوامر القرآن الكريم الصوتية",
        "description": "يمكن ل أوامر القرآن الكريم الصوتية تشغيل القرآن الكريم بالصوت بأكثر من 150 قارئ مختلف و تشغيل أكثر من 150 أذاعة مخصصة للقرآن الكريم",
        "cog": "quran"
    },
    "admin": {
        "title": "أوامر مشرفي السيرفر",
        "description": "يمكن ل أوامر مشرفي السيرفر تحديد قناة أرسال الأدعية و الأذان و العديد من الأمور **(للمشرفين فقط)**",
        "cog": "set"
    },
    "hadith": {
        "title": "أوامر الحديث النبوي الشريف",
        "description": "يمكن ل أوامر الحديث النبوي الشريف البحث عن الحديث و التحقق منه و الحصول على حديث بشكل عشوائي",
        "cog": "hadith"
    },
    "tafsir": {
        "title": "أوامر تفسير المصحف الشريف",
        "description": "يمكن ل أوامر تفسير المصحف الشريف فتح بطاقات تفسير سور القرآن الكريم و أيضاً البحث عن تفسير كلمة محددة",
        "cog": "tafsir"
    },
    "premium": {
        "title": "أوامر البريميوم",
        "description": "أوامر البريمبوم التي يقدمها بوت  فاذكروني",
        "cog": "premium"
    },
    "pray": {
        "title": "أوامر الأذكار",
        "description": "يمكن ل أوامر الأذكار فتح صفحات أذكار الصباح و المساء و غيرها من الأمور",
        "cog": "pray"
    }
}

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


def get_next_azan(azan: str) -> str:
    azan_list = list(AZAN_DATA.keys())
    azan_index = azan_list.index(azan)
    next_azan = azan_list[azan_index + 1] if azan_index + 1 < len(azan_list) else azan_list[0]
    return next_azan

def format_time_str(time: str):
    h, m = int(time.split(":")[0]), int(time.split(":")[1])
    if h>12:
        h -= 12
        return "%02d:%02d PM" % (h, m)
    return "%02d:%02d AM" % (h, m)

def get_colser_azan(timings: dict, now: datetime) -> t.Tuple[str, datetime]:
    for key, value in timings.items():
        if key not in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            continue
        h = int(value.split(":")[0])
        m = int(value.split(":")[1])
        if h == now.hour and between_two_numbers(m, now.minute-2, now.minute+2):
            return key, value
    return None

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


def get_quran_embed(player: lavalink.DefaultPlayer, audio_track: t.Optional[lavalink.AudioTrack] = None, *, reader: t.Optional[str] = None, user_id: int) -> discord.Embed:
    track = player.current or audio_track
    embed = discord.Embed(
        title="القرآن الكريم",
        color=0xffd430
    )
    embed.add_field(name="القارئ:", value=reader or track.author)
    if not track.title.lower().startswith("http"):
        embed.add_field(name="السورة:", value=track.title)
    embed.add_field(name="المستوى:", value=player.volume)
    embed.add_field(name="الحالة:", value="متوقف" if player.paused else "مشغل")
    if len(player.queue) > 1:
        embed.add_field(name="القادم:", value=f"{player.queue[1].title}")
        embed.add_field(name="عدد السور المتبقية بالقراءة:", value=f"{len(player.queue)}")
    if track:
        embed.add_field(name="مشغل من:", value="اذاعة القرآن الكريم" if track.uri.lower().startswith("https://qurango.net/radio") else "القرآن الكريم")
    embed.add_field(name="المستخدم:", value=f"<@{user_id}>")
    loop = ["غير مفعل", "السورة فقط", "القرآن الكريم كامل"]
    embed.add_field(name="حالة التكرار", value=loop[player.loop])
    return embed

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

def prosses_pray_embed(pray: t.Dict[str, t.Any], user_avatar: str) -> discord.Embed:
    embed = discord.Embed(
        title=pray["category"],
        description=pray["zekr"],
        color=0xffd430,
    )
    embed.set_thumbnail(url=user_avatar)
    embed.set_footer(text="بوت فاذكروني لإحياء سنة ذِكر الله", icon_url=user_avatar)
    if pray.get("description") and pray.get("description").get("arabic"):
        embed.add_field(name="وصف", value=pray["description"]["arabic"], inline=False)
    if pray.get("reference") != False:
        embed.add_field(name="المرجعي", value=pray["reference"])
    if pray.get("number") != False:
        embed.add_field(name="تكرار", value=pray["number"])
    return embed