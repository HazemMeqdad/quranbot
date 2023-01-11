from .azan import (AZAN_DATA, get_next_azan, get_colser_azan, get_next_azan_time, format_time_str)
from .buttons import (DownloadSurahView, SupportButtons, BaseView)
from .embed import get_quran_embed, prosses_pray_embed
from .modals import MoveModule
from .msohaf_data import moshaf_types, moshafs
from .prays import get_pray, times
from .utlit import between_two_numbers, convert_number_to_000
from .views import OpenMoshafView
from voice_client import LavalinkVoiceClient



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


