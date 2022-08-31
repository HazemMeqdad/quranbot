import discord 
from discord.ext import commands
from discord import app_commands
import aiohttp
import typing as t
from cogs.utlits.database import SavesDatabase
from cogs.utlits.views import TafsirView
from .utlits import convert_number_to_000

surahs_cache = []


class Tafsir(commands.GroupCog, name="tafsir"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
    
    @app_commands.command(name="word", description="الحصول على التفسير للكلمة المدخلة")
    @app_commands.describe(
        word="ادخل الكلمة المراد التفسير عنها"
    )
    async def tafsir(self, interaction: discord.Interaction, word: str):
        await interaction.response.send_message("التفسير للكلمة %s: %s" % (word, self.bot.tafsir.tafsir(word)))
    
    async def surah_autocomplete(self, interaction: discord.Interaction, current: t.Optional[str] = None) -> t.List[app_commands.Choice]:
        global surahs_cache
        if not surahs_cache:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://cdn.fdrbot.com/reciters/surah.json") as resp:
                    surahs_cache = await resp.json()
        if not current:
            return [app_commands.Choice(name=i["titleAr"], value=c+1) for c, i in enumerate(surahs_cache)][:25]
        return [app_commands.Choice(name=i["titleAr"], value=c+1) for c, i in enumerate(surahs_cache) if current in i["titleAr"]][:25]


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
        await interaction.response.send_message(embed=embed, view=TafsirView(int(surah), interaction.user.id))

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
        await interaction.response.send_message(embed=embed, view=TafsirView(postion, interaction.user.id))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tafsir(bot))
