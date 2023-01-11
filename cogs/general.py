from datetime import datetime
import json
import discord
from discord.ext import commands
from discord import app_commands
import time
from database import Database, DataNotFound
from database.objects import DbGuild
from utlits.buttons import SupportButtons
from utlits import BaseView
from utlits import times, HELP_DATA, format_time_str, AZAN_DATA, get_next_azan_time
import platform
import aiohttp
import typing as t

class ZkaatView(BaseView):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="نصاب زكاة المال", style=discord.ButtonStyle.grey, custom_id="zakat:money")
    async def zakat_money(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_message(
            content="ليس كل مال عليه زكاة، بل يجب أن يمضي على المال بحوزتك"
                    "مدة عام كامل وأن تكون قيمته قد بلغت قيمة نصاب الزكاة،"
                    "ونصاب زكاة المال يختلف من دولة إلى اخرى ومن عام إلى آخر،"
                    "فمن اختصاص وزارة الأوقاف والشؤون الدينية في الدولة تحديد نصاب"
                    "زكاة المال للمواطنين واصدار نشرة بهذا النصاب من وقت إلى آخر،"
                    "وفي حال كنت لا تعرف نصاب زكاة المال في بلدك فعليك الإتصال"
                    "بوزارة الأوقاف والشؤون الدينية لسؤالهم عن نصاب الزكاة،"
                    "فقد تكون قيمة المال المدخرة بحوزتك وبلغ عليها عام"
                    "كامل لم تصل نصاب الزكاة في بلدك وبذلك فانت معفى من تزكية هذا المال.",
            ephemeral=True
        )

    @discord.ui.button(label="لمن تعطي الزكاة", style=discord.ButtonStyle.grey, custom_id="zakat:forwho")
    async def zakat_forwho(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.send_message(
            content="> **1-** الفقراء: من لا يجدون كفايتهم لمدة نصف عام.\n"
                    "> **2-** المساكين: اشخاص مالهم قليل لكنهم افضل حالاً من الفقراء.\n"
                    "> **3-** الغارمين: اشخاص عليهم ديون وتعذر عليهم سدادها.\n"
                    "> **4-** ابن السبيل: شخص مسافر نفذت منه امواله، يعطى حتى يبلغ مقصده او يستطيع العودة إلى بلده، حتى لو كان غني في بلده.\n"
                    "> **5-** في سبيل الله: للاشخاص الذين خرجوا لقتال العدو من أجل اعلاء كلمة لا اله إلا الله.\n"
                    "> **6-** العاملون عليها: الاشخاص الذين قد يوليهم الحاكم على جمع اموال الزكاة وتوزيعها.\n"
                    "\n\n"
                    "> كانت تعطى ايضاً الزكاة للرقاب، اي لتحرير العبيد وايضاً للمؤلفة قلوبهم وهؤلاء غير موجدون في ايامنا هذه.",
            ephemeral=True
        )

class MsbahaView(BaseView):
    def __init__(self, msbaha, user_id: int, message: t.Optional[discord.Message] = None):
        super().__init__(timeout=60 * 5)
        self.msbaha = msbaha
        self.count = 0
        self.message = message
        self.user_id = user_id
    
    @discord.ui.button(label="0", emoji="👆", style=discord.ButtonStyle.grey, custom_id="msbaha:click")
    async def msbaha_button(self, interaction: discord.Interaction, button: discord.Button):
        if self.user_id != interaction.author.id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه المسبحة", ephemeral=True)
        self.count += 1
        button.label = f"{self.count}"
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label="تصفير", style=discord.ButtonStyle.red, custom_id="msbaha:reset")
    async def msbaha_reset(self, interaction: discord.Interaction, button: discord.Button):
        if self.user_id != interaction.author.id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه المسبحة", ephemeral=True)
        self.count = 0
        self.children[0].label = "0"
        await interaction.response.edit_message(view=self)


class HelpView(SupportButtons, BaseView):
    def __init__(self, bot: commands.Bot, user_id: t.Optional[int] = None, message: t.Optional[discord.Message] = None):
        super().__init__(timeout=60 * 5)
        self.bot = bot
        self.user_id = user_id
        self.message = message

    @discord.ui.select(
        placeholder="أختر فئة الأوامر التي تريد الحصول على معلوماتها", 
        custom_id="help:menu", 
        options=[
            discord.SelectOption(label="الصفحة الرئيسية", value="main"),
            discord.SelectOption(label="أوامر العامة", value="general"),
            discord.SelectOption(label="أوامر المصحف الشريف", value="moshaf"),
            discord.SelectOption(label="أوامر التاريخ الهجري", value="hijri"),
            discord.SelectOption(label="أوامر القرآن الكريم الصوتية", value="quran_voice"),
            discord.SelectOption(label="أوامر مشرفي السيرفر", value="admin"),
            discord.SelectOption(label="أوامر الحديث النبوي الشريف", value="hadith"),
            discord.SelectOption(label="أوامر تفسير المصحف الشريف", value="tafsir"),
            discord.SelectOption(label="أوامر البريميوم", value="premium"),
            discord.SelectOption(label="أوامر الأذكار", value="pray"),
        ]
    )
    async def help_menu(self, interaction: discord.Interaction, select: discord.ui.Select):
        if not self.user_id or interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        values = interaction.data["values"]
        if not values:
            return await interaction.response.edit_message()
        value = values[0]
        data = HELP_DATA[value]
        embed = discord.Embed(
            title=data["title"],
            description=data["description"] + "\n\n",
            color=0xffd430
        )
        if data["cog"]:
            cogs = {k.lower(): v for k, v in self.bot.cogs.items()}
            cog = cogs.get(data["cog"].lower())
            if not cog:
                ...
            else:
                cog_commands = cog.walk_app_commands()
                normal_commands = [i.name for i in cog.get_app_commands()]
                app_commands: t.List[discord.app_commands.AppCommand] = self.bot.app_commands
                for command in cog_commands:
                    if command.name in normal_commands:
                        command_id = discord.utils.get(app_commands, name=command.name).id
                        embed.description += f"</{command.name}:{command_id}> -  {command.description}\n"
                    else:
                        command_id = discord.utils.get(app_commands, name=command.parent.name).id
                        embed.description += f"</{command.parent.name} {command.name}:{command_id}> -  {command.description}\n"

        await interaction.response.edit_message(embed=embed)

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
        try:
            data = await Database.find_one("guilds", {"_id": interaction.guild.id})
        except DataNotFound:
            data = DbGuild(interaction.guild_id)
            await Database.insert(data)
        azan_data = await Database.find_one("azan", {"_id": interaction.guild.id}, raise_not_found=False)
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
