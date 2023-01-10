from datetime import datetime
import json
import discord
from discord.ext import commands
from discord import app_commands
import time
from utlits.db import AzanDatabase, Database
from utlits.views import HelpView, MsbahaView, SupportButtons, ZkaatView
from utlits import times, HELP_DATA, format_time_str, AZAN_DATA, get_next_azan_time
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
    @app_commands.guild_only()
    async def server_command(self, interaction: discord.Interaction):
        db, azan_db = Database(), AzanDatabase()
        data = db.find_guild(interaction.guild.id)
        azan_data = azan_db.find_guild(interaction.guild.id)
        if not data:
            db.insert_guild(interaction.guild.id)
            data = db.find_guild(interaction.guild.id)
        embed = discord.Embed(
            description="إعدادات الخادم: %s" % interaction.guild.name,
            color=0xffd430
        )
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text="بوت فاذكروني لإحياء سنة ذِكر الله", icon_url=self.bot.user.avatar.url)
        embed.add_field(name="قناة الأذكار و الأدعية:", value="<#%s>" % data.channel_id if data.channel_id else "لم يتم تحديد قناة")
        embed.add_field(name="وقت أرسال الأذكار و الأدعية:", value=times.get(data.time))
        embed.add_field(name="وضع الأمبد:", value="مفعل" if data.embed else "معطل")
        embed.add_field(name="رتبة القرآن الكريم:", value="<@&%s>" % data.role_id if data.role_id else "لم يتم تحديد رتبة")
        if data.channel_id:
            embed.add_field(name="أخر ذِكر تم أرساله:", value="<t:%d:R>" % int(data.next_zker.timestamp() - data.time))
        embed.add_field(
            name="اوقات الصلاة:", 
            value=f"مفعل في <#{azan_data.channel_id}> حسب توقيت **{azan_data.address}**" if azan_data is not None else "معطل",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="azan", description="معرفة وقت الأذان في المنطقة الخاصه بك 🕌")
    @app_commands.describe(address="المنطقة التي تريد معرفة وقت الأذان فيها")
    async def azan_command(self, interaction: discord.Interaction, address: str):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://api.aladhan.com/v1/timingsByAddress?address=%s&method=5" % (
                address
            )) as resp:
                res = (await resp.json())
                if res["code"] != 200:
                    return await interaction.response.send_message("لم يتم العثور على العنوان المدخل", ephemeral=True)
        data = res["data"]
        next_azan = get_next_azan_time(data["timings"], data["meta"]["timezone"])
        embed = discord.Embed(
            title="أوقات الصلاة في %s" % address + " ليوم %s" % datetime.fromtimestamp(int(data["date"]["timestamp"])).strftime("%d/%m/%Y"),
            color=0xffd430,
            timestamp=datetime.fromtimestamp(int(data["date"]["timestamp"]))
        )
        embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/451230075875504128/ZRTmO08X.jpeg")
        embed.add_field(name="صلاة الفجْر:", value=format_time_str(data["timings"]["Fajr"]))
        embed.add_field(name="الشروق:", value=format_time_str(data["timings"]["Sunrise"]))
        embed.add_field(name="صلاة الظُّهْر:", value=format_time_str(data["timings"]["Dhuhr"]))
        embed.add_field(name="صلاة العَصر:", value=format_time_str(data["timings"]["Asr"]))
        embed.add_field(name="صلاة المَغرب:", value=format_time_str(data["timings"]["Maghrib"]))
        embed.add_field(name="صلاة العِشاء:", value=format_time_str(data["timings"]["Isha"]))
        if next_azan != (None, None):
            embed.add_field(name=f"تبقى على وقت صلاة {AZAN_DATA[next_azan[0]]['name']}:", value=discord.utils.format_dt(next_azan[1], "R"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="معلومات عن البوت 🤖")
    async def info_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            color=0xffd430,
            description="\n".join(HELP_DATA["main"]["description"].split("\n\n")[:1]),
            url=f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"
        )
        embed.add_field(name="خوادم البوت:", value=len(self.bot.guilds).__str__())
        embed.add_field(name="سرعة الأتصال:", value=f"{round(self.bot.latency * 1000)}ms")
        embed.add_field(name="أصدار البوت:", value="v4.0.0")
        embed.add_field(name="الشاردات:", value=str(self.bot.shard_count))
        embed.add_field(name="أصدار المكتبة:", value=discord.__version__)
        embed.add_field(name="أصدار البايثون:", value=platform.python_version())
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="بوت فاذكروني لإحياء سنة ذِكر الله", icon_url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed, view=SupportButtons())

    @app_commands.command(name="invite", description="إنقر للدعوة 🔗")
    async def invite_command(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"<https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands>", 
            ephemeral=True
        )

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

    @app_commands.command(name="msbaha", description="فتح مسحبة عداد المسبحة للحسنات و الحسنه بعشر أمثالها")
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
        view = MsbahaView(msbaha)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=hide)
        view.message = await interaction.original_response()

    @app_commands.command(name="help", description="أرسل هذا الرسالة للحصول على جميع الأوامر 📖")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=HELP_DATA["main"]["title"],
            description=HELP_DATA["main"]["description"],
            color=0xffd430
        )
        embed.set_author(name="لوحة أوامر بوت فاذكروني", icon_url=self.bot.user.avatar.url)
        view = HelpView(self.bot, interaction.user.id)
        await interaction.response.send_message(
            embed=embed, 
            view=view,
        )
        view.message = await interaction.original_response()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
