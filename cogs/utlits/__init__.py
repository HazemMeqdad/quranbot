
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
