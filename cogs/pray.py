import discord
from discord.ext import commands
from discord import app_commands
import json
import typing as t
from .utlits import prosses_pray_embed, get_pray
from .utlits.views import PrayView


class Pray(commands.GroupCog, name="pray"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_prays(self, type: t.Literal["أذكار الصباح", "أذكار المساء"]) -> t.List[t.Dict[str, t.Any]]:
        with open("json/prays.json", "r", encoding="utf-8") as f:
            data = json.load(f)["azkar"]
        prays = list(filter(lambda x: x["category"] == type, data))
        return prays

    @app_commands.command(name="random", description="الحصول على ذِكر عشوائي")
    async def pray(self, interaction: discord.Interaction):
        pray = get_pray()
        embed = prosses_pray_embed(pray, self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="sabah", description="فتح قائمة أذكار الصباح")
    @app_commands.describe(
        hide="جعل الرسالة بينك و بين البوت فقط, True(أخفاء الرسالة)/False(أضهار الرسالة)"
    )
    async def pray_sabah(self, interaction: discord.Interaction, hide: t.Optional[bool] = False):
        prays = self.get_prays("أذكار الصباح")
        embed = prosses_pray_embed(prays[0], self.bot.user.avatar.url)
        embed.set_footer(text=f"1/{len(prays)}")
        view = PrayView(interaction.user.id, prays, self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=hide)
        view.message = await interaction.original_response()

    @app_commands.command(name="masaa", description="فتح قائمة أذكار المساء")
    @app_commands.describe(
        hide="جعل الرسالة بينك و بين البوت فقط, True(أخفاء الرسالة)/False(أضهار الرسالة)"
    )
    async def pray_masaa(self, interaction: discord.Interaction, hide: t.Optional[bool] = False):
        prays = self.get_prays("أذكار المساء")
        embed = prosses_pray_embed(prays[0], self.bot.user.avatar.url)
        embed.set_footer(text=f"1/{len(prays)}")
        view = PrayView(interaction.user.id, prays, self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=hide)
        view.message = await interaction.original_response()


async def setup(bot: commands.Bot):
    await bot.add_cog(Pray(bot))
