import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random

all_chapters = []

class Hadith(commands.GroupCog, name="hadith"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def hadith_search_autocompete(self, interaction: discord.Interaction, current: str) -> str:
        current = current if current != "" else "اللة"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://ahadith-api.herokuapp.com/api/search/ahadith/{current}/ar-notashkeel") as resp:
                data = await resp.json()
                return [app_commands.Choice(name=i["Ar_Text_Without_Tashkeel"][:100], value="%d_%d_%d" % (i["Book_ID"], i["Chapter_ID"], i["Hadith_ID"])) for i in data["Chapter"]][:25]

    @app_commands.command(name="search", description="البحث عن حديث 🔎")
    @app_commands.autocomplete(hadith=hadith_search_autocompete)
    @app_commands.describe(hadith="ادخل الحديث الذي تريد البحث عنه")
    async def hadith_search_command(self, interaction: discord.Interaction, *, hadith: str) -> None:
        bookid, chapterid, hadith_id = hadith.split("_")[0], hadith.split("_")[1], hadith.split("_")[2]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://ahadith-api.herokuapp.com/api/ahadith/{bookid}/{chapterid}/ar-notashkeel") as resp:
                data = await resp.json()
        hadith_text = [i for i in data["Chapter"] if i["Hadith_ID"] == int(hadith_id)][0]["Ar_Text_Without_Tashkeel"]
        embed = discord.Embed(
            title=f"{bookid}:{chapterid}:{hadith_id}", 
            description=hadith_text,
            color=0xffd430
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="random", description="البحث عن حديث بشكل عشوائي 🔎")
    async def random_hadith_command(self, interaction: discord.Interaction) -> None:
        global all_chapters

        if len(all_chapters) == 0:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://ahadith-api.herokuapp.com/api/ahadith/all/ar-notashkeel") as resp:
                    all_chapters = await resp.json()

        data = all_chapters
        
        hadith = random.choice(data["AllChapters"])
        embed = discord.Embed(
            title=f"{hadith['Book_ID']}:{hadith['Chapter_ID']}:{hadith['Hadith_ID']}", 
            description=hadith["Ar_Text_Without_Tashkeel"],
            color=0xffd430
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Hadith(bot))
