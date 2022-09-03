from discord import ButtonStyle
from discord.ui import View, Button
import discord
from .msohaf_data import moshaf_types, moshafs
from .db import Database, SavesDatabase
from . import convert_number_to_000, HELP_DATA, get_quran_embed
from discord.ext import commands
import typing as t
from discord.app_commands import AppCommand
import aiohttp
import lavalink

surahs_cache = []

class BaseView(View):
    async def on_timeout(self) -> None:
        if not hasattr(self, "message") or self.message is None:
            return
        for index, item in enumerate(self.children):
            if isinstance(item, discord.ui.TextInput) or (isinstance(item, discord.ui.Button) and item.style == ButtonStyle.link):
                continue
            self.children[index].disabled = True
        await self.message.edit(view=self)

class MoveModule(discord.ui.Modal, title="أنتقال إلى صفحة محددة"):
    position = discord.ui.TextInput(
        label="الصفحة", 
        style=discord.ui.text_input.TextStyle.short,
        placeholder="أدخل رقم الصفحة",
        required=True,
        min_length=1,
    )
    
    def __init__(self, view: BaseView, max_value: int) -> None:
        super().__init__()
        self.view = view
        self.position.max_value = max_value
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.view.set_position(int(self.position.value))
        await interaction.response.edit_message(embed=await self.view.get_page())

class SupportButtons(BaseView):
    def __init__(self, timeout: t.Optional[int] = None):
        super().__init__(timeout=timeout)
        self.add_item(Button(
            style=ButtonStyle.url,
            label="إضافة البوت",
            url=f"https://discord.com/oauth2/authorize?client_id=728782652454469662&permissions=8&scope=bot%20applications.commands"
        ))
        self.add_item(Button(
            style=ButtonStyle.url,
            label="الدعم الفني",
            url="https://discord.gg/VX5F54YNuy"
        ))
        self.add_item(Button(
            style=ButtonStyle.url,
            label="لوحة التحكم",
            url="https://fdrbot.com"
        ))


class MoshafView(BaseView):
    def __init__(self, moshaf_type: int, page_number: int, page_end: int, user_id: int, message: t.Optional[discord.Message] = None):
        super().__init__(timeout=60 * 5)
        self.moshaf_type = moshaf_type
        self.postion = page_number
        self.page_end = page_end
        self.user_id = user_id
        self.message = message

    def set_position(self, position: int) -> None:
        self.postion = position

    @discord.ui.button(label="⏮️", style=ButtonStyle.grey, custom_id="moshaf:first")
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.edit_message()
        self.postion = 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="◀️", style=ButtonStyle.grey, custom_id="moshaf:prev")
    async def previous_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.send_message(content="لا يمكنك الرجوع للصفحة السابقة", ephemeral=True)
        self.postion -= 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏹️", style=ButtonStyle.red, custom_id="moshaf:close")
    async def close(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        await interaction.response.edit_message(view=None)

    @discord.ui.button(label="▶️", style=ButtonStyle.grey, custom_id="moshaf:next")
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        if self.postion == self.page_end:
            return await interaction.response.send_message(content="لا يمكنك التقدم للصفحة التالية", ephemeral=True)
        self.postion += 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏭️", style=ButtonStyle.grey, custom_id="moshaf:last")
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        if self.postion == self.page_end:
            return await interaction.response.edit_message()
        self.postion = self.page_end
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="📌", style=ButtonStyle.green, custom_id="moshaf:save")
    async def save_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        db = SavesDatabase()
        data = db.find_one(f"moshaf_{self.user_id}")
        if not data:
            db.insert(f"moshaf_{self.user_id}", {"moshaf_type": self.moshaf_type, "page_number": self.postion})
        else:
            db.update(f"moshaf_{self.user_id}", data={"moshaf_type": self.moshaf_type, "page_number": self.postion})
        await interaction.response.send_message(content="تم حفظ الصفحة بنجاح", ephemeral=True)

    @discord.ui.button(label="🔢", style=ButtonStyle.grey, custom_id="moshaf:page")
    async def page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        await interaction.response.send_modal(MoveModule(self, self.page_end))

    async def get_page(self) -> discord.Embed:
        moshaf = [i for i in moshaf_types if int(i["value"]) == self.moshaf_type][0]

        embed = discord.Embed(title=moshaf["name"], color=0xffd430)
        embed.set_image(url=f"http://www.islamicbook.ws/{self.moshaf_type}/{self.postion}.{moshafs[str(self.moshaf_type)]['type']}")
        embed.set_footer(text=f"الصفحة {self.postion}/{moshafs[str(moshaf['value'])]['page_end']}")
        
        return embed

class OpenMoshafView(BaseView):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📖", style=ButtonStyle.grey, custom_id="moshaf:open")
    async def open_moshaf(self, interaction: discord.Interaction, button: discord.Button):
        db = SavesDatabase()
        db_data = db.find_one(f"moshaf_{interaction.user.id}")
        data = db_data.data if db_data else None
        guild_data = Database().find_guild(interaction.guild.id)
        moshaf_type = guild_data.moshaf_type if guild_data.moshaf_type else 1
        page_number = 1
        if data is not None and data["moshaf_type"] == moshaf_type:
            page_number = data["page_number"]

        moshaf = [i for i in moshaf_types if i["value"] == moshaf_type][0]

        embed = discord.Embed(title=moshaf["name"], color=0xffd430)
        embed.set_image(url=f"http://www.islamicbook.ws/{moshaf_type}/{page_number}.{moshafs[str(moshaf['value'])]['type']}")
        embed.set_footer(text=f"الصفحة {page_number}/{moshafs[str(moshaf['value'])]['page_end']}")
        await interaction.response.send_message(
            embed=embed, 
            view=MoshafView(moshaf_type, page_number, moshafs[str(moshaf['value'])]["page_end"], interaction.user.id),
            ephemeral=True
        )

class DownloadSurahView(BaseView):
    def __init__(self, link: str):
        super().__init__(timeout=None)
        self.add_item(Button(
            style=ButtonStyle.link,
            label="تحميل السورة",
            url=link
        ))


class ZkaatView(BaseView):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="نصاب زكاة المال", style=ButtonStyle.grey, custom_id="zakat:money")
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

    @discord.ui.button(label="لمن تعطي الزكاة", style=ButtonStyle.grey, custom_id="zakat:forwho")
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
    
    @discord.ui.button(label="0", emoji="👆", style=ButtonStyle.grey, custom_id="msbaha:click")
    async def msbaha_button(self, interaction: discord.Interaction, button: discord.Button):
        if self.user_id != interaction.author.id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه المسبحة", ephemeral=True)
        self.count += 1
        button.label = f"{self.count}"
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label="تصفير", style=ButtonStyle.red, custom_id="msbaha:reset")
    async def msbaha_reset(self, interaction: discord.Interaction, button: discord.Button):
        if self.user_id != interaction.author.id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه المسبحة", ephemeral=True)
        self.count = 0
        self.children[0].label = "0"
        await interaction.response.edit_message(view=self)

class TafsirView(BaseView):
    def __init__(self, postion: int, user_id: int, message: t.Optional[discord.Message] = None):
        super().__init__(timeout=60 * 5)
        self.user_id = user_id
        self.postion = postion
        self.message = message

    def set_position(self, position: int) -> None:
        self.postion = position

    @discord.ui.button(label="⏮️", style=ButtonStyle.grey, custom_id="tafsir:first")
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.edit_message()
        self.postion = 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="◀️", style=ButtonStyle.grey, custom_id="tafsir:prev")
    async def previous_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.send_message(content="لا يمكنك الرجوع للصفحة السابقة", ephemeral=True)
        self.postion -= 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏹️", style=ButtonStyle.red, custom_id="tafsir:close")
    async def close(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        await interaction.response.edit_message(view=None)

    @discord.ui.button(label="▶️", style=ButtonStyle.grey, custom_id="tafsir:next")
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 114:
            return await interaction.response.send_message(content="لا يمكنك التقدم للصفحة التالية", ephemeral=True)
        self.postion += 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏭️", style=ButtonStyle.grey, custom_id="tafsir:last")
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 114:
            return await interaction.response.edit_message()
        self.postion = 114
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="📌", style=ButtonStyle.green, custom_id="tafsir:save")
    async def save_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        db = SavesDatabase()
        data = db.find_one(f"tafsir_{self.user_id}")
        if not data:
            db.insert(f"tafsir_{self.user_id}", data={"postion": self.postion})
            return
        db.update(f"tafsir_{self.user_id}", data={"postion": self.postion})
        await interaction.response.send_message(content="تم حفظ الصفحة بنجاح", ephemeral=True)

    @discord.ui.button(label="🔢", style=ButtonStyle.grey, custom_id="tafsir:page")
    async def page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        await interaction.response.send_modal(MoveModule(self, 114))

    async def get_page(self) -> discord.Embed:
        embed = discord.Embed(
            title="قائمة بطاقات القرآن الكريم",
            color=0xffd430
        )
        embed.set_image(url=f"https://raw.githubusercontent.com/rn0x/albitaqat_quran/main/images/{convert_number_to_000(self.postion)}.jpg")
        embed.set_footer(text=f"البطاقة الحالية: {self.postion}/114")
        return embed

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
                app_commands: t.List[AppCommand] = self.bot.app_commands
                for command in cog_commands:
                    if command.name in normal_commands:
                        command_id = discord.utils.get(app_commands, name=command.name).id
                        embed.description += f"</{command.name}:{command_id}> -  {command.description}\n"
                    else:
                        command_id = discord.utils.get(app_commands, name=command.parent.name).id
                        embed.description += f"</{command.parent.name} {command.name}:{command_id}> -  {command.description}\n"

        await interaction.response.edit_message(embed=embed)

class TafsirAyahView(BaseView):
    def __init__(self, tafsir_data: dict, surah_text: dict, postion: int, user_id: int, message: t.Optional[discord.Message] = None) -> None:
        super().__init__(timeout=3600)
        self.tafsir_data = tafsir_data
        self.surah_text = surah_text
        self.postion = postion
        self.user_id = user_id
        self.message = message

    def set_position(self, position: int) -> None:
        self.postion = position

    @discord.ui.button(label="⏮️", style=ButtonStyle.grey, custom_id="tafsir:ayah:first")
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.edit_message()
        self.postion = 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="◀️", style=ButtonStyle.grey, custom_id="tafsir:ayah:prev")
    async def previous_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.send_message(content="لا يمكنك الرجوع للصفحة السابقة", ephemeral=True)
        self.postion -= 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏹️", style=ButtonStyle.red, custom_id="tafsir:ayah:close")
    async def close(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        await interaction.response.edit_message(view=None)

    @discord.ui.button(label="▶️", style=ButtonStyle.grey, custom_id="tafsir:ayah:next")
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == self.tafsir_data["count"]:
            return await interaction.response.send_message(content="لا يمكنك التقدم للصفحة التالية", ephemeral=True)
        self.postion += 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏭️", style=ButtonStyle.grey, custom_id="tafsir:ayah:last")
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == self.tafsir_data["count"]:
            return await interaction.response.edit_message()
        self.postion = self.tafsir_data["count"]
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="🔢", style=ButtonStyle.grey, custom_id="tafsir:ayah:page")
    async def page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        await interaction.response.send_modal(MoveModule(self, self.tafsir_data["count"]))

    async def get_page(self) -> discord.Embed:
        global surahs_cache
        if not surahs_cache:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://cdn.fdrbot.com/reciters/surah.json") as resp:
                    surahs_cache = await resp.json()
        surah_name = surahs_cache[self.tafsir_data["index"]-1]["titleAr"]
        embed = discord.Embed(
            title=f"سورة {surah_name} الآية رقم {self.postion} حسب التفسير المیسر", 
            description=f"قال الله تعالى ({self.surah_text['verse'][f'verse_' + str(self.postion)]})\n\n"
                        "-------------------------\n\n"
                        f"{self.tafsir_data['verse'][f'verse_' + str(self.postion)]}",
            color=0xffd430
        )
        embed.set_footer(text=f"{self.postion}/{self.tafsir_data['count']}")
        return embed

class VoiceView(BaseView):
    def __init__(self, player: lavalink.DefaultPlayer = None, user_id: int = None, reader: str = None, disabled: bool = False, message: t.Optional[discord.Message] = None):
        super().__init__(timeout=None)
        self.player = player
        self.user_id = user_id
        self.message = None
        self.postion = 1
        self.reader = reader
        self.message = message
        if disabled:
            for index, item in enumerate(self.children):
                if isinstance(item, discord.ui.TextInput) or (isinstance(item, discord.ui.Button) and item.style == ButtonStyle.link):
                    continue
                self.children[index].disabled = True
    
    def set_postion(self, postion: int):
        self.postion = postion
    
    @discord.ui.button(label="⏯️", style=ButtonStyle.grey, custom_id="voice:pause")
    async def pause(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.paused:
            await self.player.set_pause(False)
            await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))
        else:
            await self.player.set_pause(True)
            await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))

    @discord.ui.button(label="⏹️", style=ButtonStyle.red, custom_id="voice:stop")
    async def stop(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        self.player.queue.clear()
        if self.player.is_playing:
            await self.player.stop()
        await interaction.guild.voice_client.disconnect(force=True)
        for index, item in enumerate(self.children):
            if isinstance(item, discord.ui.TextInput) or (isinstance(item, discord.ui.Button) and item.style == ButtonStyle.link):
                continue
            self.children[index].disabled = True
        embed = interaction.message.embeds[0]
        state_field = list(filter(lambda x: x.name == "الحالة:", embed.fields))[0]
        embed.set_field_at(embed.fields.index(state_field), name="الحالة:", value="متوقف")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⏭️", style=ButtonStyle.grey, custom_id="voice:next")
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.is_playing:
            await self.player.skip()
        if len(self.player.queue) == 0:
            return await interaction.response.edit_message()
        
        await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))
    
    @discord.ui.button(label="🔉", style=ButtonStyle.grey, custom_id="voice:volume:down")
    async def down_volume(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.is_playing:
            await self.player.set_volume(self.player.volume - 10)
            await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))

    @discord.ui.button(label="🔊", style=ButtonStyle.grey, custom_id="voice:volume:up")
    async def up_volume(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.is_playing and self.player.volume < 100:
            await self.player.set_volume(self.player.volume + 10)
        await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))

    @discord.ui.button(label="🔂", style=ButtonStyle.grey, custom_id="voice:repeat:surah")
    async def repeat(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.is_playing:
            if self.player.loop == 1:
                self.player.set_loop(0)
            else:
                self.player.set_loop(1)
        await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))

    @discord.ui.button(label="🔁", style=ButtonStyle.grey, custom_id="voice:repaet:all")
    async def repeat_all(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.is_playing:
            if self.player.loop == 2:
                self.player.set_loop(0)
            else:
                self.player.set_loop(2)
        await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))   
