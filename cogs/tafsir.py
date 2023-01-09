import json
import discord 
from discord.ext import commands
from discord import app_commands
import aiohttp
import typing as t
from cogs.utlits.db import SavesDatabase
from cogs.utlits.views import TafsirView, TafsirAyahView
from .utlits import convert_number_to_000


tafsir_cache = {}
surah_text_cache = {}

class Tafsir(commands.GroupCog, name="tafsir"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
    
    async def surah_autocomplete(self, interaction: discord.Interaction, current: t.Optional[str] = None) -> t.List[app_commands.Choice]:
        with open("json/surahs.json", "r", encoding="utf-8") as f:
            surahs = json.load(f)
        if not current:
            return [app_commands.Choice(name=i, value=c+1) for c, i in enumerate(surahs)][:25]
        return [app_commands.Choice(name=i, value=c+1) for c, i in enumerate(surahs) if current in i][:25]

    @app_commands.command(name="ayah", description="الحصول على نفسير الآية")
    @app_commands.describe(
        surah="ادخل السورة المراد التفسير عنها",
        ayah="ادخل رقم للآية المراد التفسير عنها",
    )
    @app_commands.autocomplete(surah=surah_autocomplete)
    async def tafsir(self, interaction: discord.Interaction, surah: int, ayah: int = 1):
        global tafsir_cache, surah_text_cache
        if surah > 114:
            return await interaction.response.send_message("السورة غير موجودة", ephemeral=True)
        query = f"{surah}:{ayah}"
        data = tafsir_cache.get(query)
        if not data:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://raw.githubusercontent.com/semarketir/quranjson/master/source/translation/ar/ar_translation_{surah}.json") as resp:
                    tafsir_cache[query] = json.loads(await resp.text())
                    data = tafsir_cache.get(query)
        surah_text = surah_text_cache.get(query)
        if not surah_text:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://raw.githubusercontent.com/semarketir/quranjson/master/source/surah/surah_{surah}.json") as resp:
                    surah_text_cache[query] = json.loads(await resp.text())
                    surah_text = surah_text_cache.get(query)

        if ayah > data["count"]:
            return await interaction.response.send_message("الآية المطلوبة غير موجودة", ephemeral=True)
        with open("json/surahs.json", "r", encoding="utf-8") as f:
            surahs = json.load(f)
        surah_name = surahs[data["index"]-1]["titleAr"]
        embed = discord.Embed(
            title=f"سورة {surah_name} الآية {ayah} حسب التفسير المیسر", 
            description=f"قال الله تعالى ({surah_text['verse'][f'verse_' + str(ayah)]})\n\n"
                        "-------------------------\n\n"
                        f"{data['verse'][f'verse_' + str(ayah)]}",
            color=0xffd430
        )
        embed.set_footer(text=f"{ayah}/{data['count']}")
        view = TafsirAyahView(data, surah_text, ayah, interaction.user.id)
        await interaction.response.send_message(
            embed=embed, 
            view=view
        )
        view.message = await interaction.original_response()

    @app_commands.command(name="surah", description="الحصول على التفسير للسورة المدخلة")
    @app_commands.describe(
        surah="ادخل رقم السورة المراد التفسير عنها"
    )
    @app_commands.autocomplete(surah=surah_autocomplete)
    @app_commands.describe(
        surah="ادخل اسم السورة المراد التفسير عنها",
        hide="جعل الرسالة بينك و بين البوت فقط, True(أخفاء الرسالة)/False(أضهار الرسالة)",
    )
    async def tafsir_surah(self, interaction: discord.Interaction, surah: int, hide: bool = False):
        postion = convert_number_to_000(int(surah))

        embed = discord.Embed(
            title="قائمة بطاقات القرآن الكريم",
            color=0xffd430
        )
        embed.set_image(url=f"https://raw.githubusercontent.com/rn0x/albitaqat_quran/main/images/{postion}.jpg")
        embed.set_footer(text=f"البطاقة الحالية: {surah}/114")
        view = TafsirView(int(surah), interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

    @app_commands.command(name="browser", description="فتح قائمة بطاقات القرآن الكريم")
    async def browser(self, interaction: discord.Interaction):
        db = SavesDatabase()
        user_data = db.find_one(f"tafsir_{interaction.user.id}")
        postion = 1
        if user_data:
           postion = user_data.data["postion"]
        embed = discord.Embed(
            title="قائمة بطاقات القرآن الكريم",
            color=0xffd430
        )
        embed.set_image(url=f"https://raw.githubusercontent.com/rn0x/albitaqat_quran/main/images/{convert_number_to_000(postion)}.jpg")
        embed.set_footer(text=f"البطاقة الحالية: {postion}/114")
        view = TafsirView(postion, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tafsir(bot))
