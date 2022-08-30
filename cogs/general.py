from datetime import datetime
import json
import os
import discord
from discord.ext import commands
from discord import app_commands
import time
from cogs.utlits.database import Database
from .utlits.views import MsbahaView, SupportButtons, ZkaatView
from .utlits import times
import platform
import aiohttp

with open("json/msbaha.json", "r", encoding="utf-8") as f:
    msbaha_types = json.load(f)

class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="سرعة اتصال البوت 🏓")
    async def ping_command(self, interaction: discord.Interaction):
        before = time.monotonic()
        await interaction.response.send_message("```\nping\n```")
        ping = (time.monotonic() - before) * 1000
        await interaction.edit_original_response(content="```python\nTime: %s ms\nLatency: %s ms```" % (
            int(ping), round(self.bot.latency * 1000)
        ))

    @app_commands.command(name="support", description="سيرفر الدعم الفني 💡")
    async def support_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="**شكراً على أختيارك بوت فاذكروني 🌹**",
            color=0xffd430
        )
        embed.set_footer(text="بوت فاذكروني لإحياء سنة ذِكر الله", icon_url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed, view=SupportButtons())

    @app_commands.command(name="server", description="معلومات عن السيرفر 📊")
    async def server_command(self, interaction: discord.Interaction):
        db = Database()
        data = db.find_guild(interaction.guild.id)
        if not data:
            db.insert_guild(interaction.guild.id)
            data = db.find_guild(interaction.guild.id)
        embed = discord.Embed(
            description="إعدادات الخادم: %s" % interaction.guild.name,
            color=0xffd430
        )
        embed.add_field(name="قناة الأذكار:", value="<#%s>" % data.channel_id if data.channel_id else "لم يتم تحديد قناة")
        embed.add_field(name="وقت أرسال الأذكار:", value=times.get(data.time))
        embed.add_field(name="وضع الأمبد:", value="مفعل" if data.embed else "معطل")
        embed.add_field(name="رتبة القرآن الكريم:", value="<@&%s>" % data.role_id if data.role_id else "لم يتم تحديد رتبة")
        embed.add_field(name="أخر ذِكر تم أرساله:", value="<t:%d:R>" % int(data.next_zker.timestamp() - data.time))
        embed.add_field(name="اوقات الصلاة:", value="مفعل")
        embed.add_field(name="الادعية:", value="مفعل")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="azan", description="معرفة وقت الأذان في المنطقة الخاصه بك 🕌")
    async def azan_command(self, interaction: discord.Interaction, address: str):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://api.aladhan.com/v1/timingsByAddress?address=%s&method=5" % (
                address
            )) as resp:
                res = (await resp.json())
                if res["code"] != 200:
                    return await interaction.response.send_message("لم يتم العثور على العنوان المدخل", ephemeral=True)
        data = res["data"]
        embed = discord.Embed(
            title="أوقات الصلاة في %s" % address + " ليوم %s" % datetime.fromtimestamp(int(data["date"]["timestamp"])).strftime("%d/%m/%Y"),
            color=0xffd430,
            timestamp=datetime.fromtimestamp(int(data["date"]["timestamp"]))
        )
        embed.add_field(name="صلاة الفجْر:", value=data["timings"]["Fajr"])
        embed.add_field(name="الشروق:", value=data["timings"]["Sunrise"])
        embed.add_field(name="صلاة الظُّهْر:", value=data["timings"]["Dhuhr"])
        embed.add_field(name="صلاة العَصر:", value=data["timings"]["Asr"])
        embed.add_field(name="صلاة المَغرب:", value=data["timings"]["Maghrib"])
        embed.add_field(name="صلاة العِشاء:", value=data["timings"]["Isha"])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="معلومات عن البوت 🤖")
    async def info_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            color=0xffd430,
            description="بوت فاذكروني لإحياء سنة ذِكر الله",
            url=f"<https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands>"
        )
        embed.add_field(name="خوادم البوت:", value=len(self.bot.guilds).__str__())
        embed.add_field(name="سرعة الأتصال:", value=f"{round(self.bot.latency * 1000)}ms")
        embed.add_field(name="أصدار البوت:", value="v4.0.0")
        embed.add_field(name="الشاردات:", value=str(self.bot.shard_count))
        embed.add_field(name="أصدار المكتبة:", value=discord.__version__)
        embed.add_field(name="أصدار البايثون:", value=platform.python_version())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite", description="إنقر للدعوة 🔗")
    async def invite_command(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"<https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands>", 
            ephemeral=True
        )
    
    @app_commands.command(name="pray", description="أرسال ذِكر عشوائي 🎲")
    async def pray_command(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{os.environ['CDN_URL']}/pray/random") as resp:
                data = (await resp.json())
        embed = discord.Embed(
            title="ذِكر عشوائي - %d" % data["id"],
            description=data["text"],
            color=0xffd430
        )
        embed.set_footer(text="بوت فاذكروني لإحياء سنة ذِكر الله", icon_url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="zkaat", description="حساب زكاة الأموال 💰")
    @app_commands.describe(
        amount="أدخل كمية الأموال المراد حساب زكاتها",
        currency="أدخل عملة الأموال المراد حساب زكاتها",
        hide="جعل الرسالة بينك و بين البوت فقط, True(أخفاء الرسالة)/False(أضهار الرسالة)"
    )
    async def zkaat_command(self, interaction: discord.Interaction, amount: int, currency: str, hide: bool = False):
        zkaat = amount * 0.025
        embed = discord.Embed(
            title="حساب زكاة الأموال",
            color=0xffd430
        )
        embed.add_field(name="المبلغ المراد حسابها:", value=amount.__str__() + " " + currency)
        embed.add_field(name="الزكاة المطلوبة:", value=int(zkaat).__str__() + " " + currency)
        embed.add_field(name="المبلغ بعد الزكاة:", value=int(amount - zkaat).__str__() + " " + currency)
        embed.set_footer(
            text="ملاحظة هامة: الزكاة تكون على المال الذي مر عليه عام هجري،"
            " فمثلاً اليوم رصيدك 100 الف "
            "والعام الماضي في مثل هذا اليوم كان رصيدك 70 الف فان الزكاة واجبة على المبلغ 70 الف.")
        await interaction.response.send_message(embed=embed, view=ZkaatView(), ephemeral=hide)

    @app_commands.command(name="msbaha", description="حساب زكاة الأموال 💰")
    @app_commands.describe(
        type="حدد نوع المسبحة المراد",
        hide="جعل الرسالة بينك و بين البوت فقط, True(أخفاء الرسالة)/False(أضهار الرسالة)"
    )
    @app_commands.choices(type=[app_commands.Choice(name=i["title"], value=i["value"][:100] if i["value"] else "...") for i in msbaha_types])
    async def msbaha_command(self, interaction: discord.Interaction, type: str, hide: bool = False):
        msbaha = [i for i in msbaha_types if i["value"] and i["value"].startswith(type)][0]
        embed = discord.Embed(
            title=msbaha["title"],
            description=msbaha["value"] if msbaha["value"] else None,
            color=0xffd430
        )
        await interaction.response.send_message(embed=embed, view=MsbahaView(msbaha), ephemeral=hide)

    @app_commands.command(name="help", description="أرسل هذا الرسالة للحصول على جميع الأوامر 📖")
    async def help_command(self, interaction: discord.Interaction, is_hidden: bool = False):
        embed = discord.Embed(
            title="أوامر البوت",
            description="أرسل هذا الرسالة للحصول على جميع الأوامر 📖",
            color=0xffd430
        )
        embed.add_field(name="الأوامر العامة:", value="`pray`, `azan`, `info`, `invite`, `help`")
        embed.add_field(name="الأوامر الخاصة:", value="`pray`, `azan`, `info`, `invite`, `help`")
        await interaction.response.send_message(embed=embed, ephemeral=is_hidden)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))