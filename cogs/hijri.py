import discord 
from discord.ext import commands
from discord import app_commands
from hijri_converter import Gregorian
from datetime import datetime

class HijriCog(commands.GroupCog, name="hijri"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="date", description="الحصول على التاريخ الهجري للوقت الحالي")
    async def date_hijri(self, interaction: discord.Interaction):
        now = datetime.now()
        try:
            hijri = Gregorian(now.year, now.month, now.day).to_hijri()
        except OverflowError:
            return await interaction.response.send_message("يرجى التاكد من التاريخ المدخل", ephemeral=True)
        embed = discord.Embed(
            title="تحويل التاريخ الحالي إلى التاريخ الهجري",
            description="التاريخ الهجري للوقت الحالي: **%d %s (الشهر %d) %d هـ**" % (hijri.day, hijri.month_name("ar"), hijri.month, hijri.year),
            color=0xffd430,
            timestamp=now
        )
        embed.set_footer(text="عدد أيام الشهر %d يوم" % hijri.month_length())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="convert", description="التوحيل من التاريخ الميلادي الى الهجري")
    @app_commands.describe(
        day="ادخل اليوم",
        month="ادخل الشهر",
        year="ادخل السنة",
    )
    async def convert_hijri(self, interaction: discord.Interaction, day: int, month: int, year: int):
        try:
            hijri = Gregorian(year, month, day).to_hijri()
        except OverflowError:
            return await interaction.response.send_message("يرجى التاكد من التاريخ المدخل", ephemeral=True)
        embed = discord.Embed(
            title="تحويل %d/%d/%d إلى التاريخ الهجري" % (day, month, year),
            description="التاريخ الهجري: **%d %s (الشهر %d) %d هـ**" % (hijri.day, hijri.month_name("ar"), hijri.month, hijri.year),
            color=0xffd430
        )
        embed.set_footer(text="عدد أيام الشهر %d يوم" % hijri.month_length())
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(HijriCog(bot))
