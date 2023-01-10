import json
import discord 
from discord.ext import commands
from discord import app_commands
import aiohttp
import typing as t
from utlits.db import SavesDatabase
from utlits import BaseView
from utlits.modals import MoveModule
from utlits import convert_number_to_000


class TafsirView(BaseView):
    def __init__(self, postion: int, user_id: int, message: t.Optional[discord.Message] = None):
        super().__init__(timeout=60 * 5)
        self.user_id = user_id
        self.postion = postion
        self.message = message

    def set_position(self, position: int) -> None:
        self.postion = position

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.grey, custom_id="tafsir:first")
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.edit_message()
        self.postion = 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.grey, custom_id="tafsir:prev")
    async def previous_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.send_message(content="لا يمكنك الرجوع للصفحة السابقة", ephemeral=True)
        self.postion -= 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.red, custom_id="tafsir:close")
    async def close(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        await interaction.response.edit_message(view=None)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.grey, custom_id="tafsir:next")
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 114:
            return await interaction.response.send_message(content="لا يمكنك التقدم للصفحة التالية", ephemeral=True)
        self.postion += 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.grey, custom_id="tafsir:last")
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 114:
            return await interaction.response.edit_message()
        self.postion = 114
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="📌", style=discord.ButtonStyle.green, custom_id="tafsir:save")
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

    @discord.ui.button(label="🔢", style=discord.ButtonStyle.grey, custom_id="tafsir:page")
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

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.grey, custom_id="tafsir:ayah:first")
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.edit_message()
        self.postion = 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.grey, custom_id="tafsir:ayah:prev")
    async def previous_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.send_message(content="لا يمكنك الرجوع للصفحة السابقة", ephemeral=True)
        self.postion -= 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.red, custom_id="tafsir:ayah:close")
    async def close(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        await interaction.response.edit_message(view=None)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.grey, custom_id="tafsir:ayah:next")
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == self.tafsir_data["count"]:
            return await interaction.response.send_message(content="لا يمكنك التقدم للصفحة التالية", ephemeral=True)
        self.postion += 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.grey, custom_id="tafsir:ayah:last")
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.postion == self.tafsir_data["count"]:
            return await interaction.response.edit_message()
        self.postion = self.tafsir_data["count"]
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="🔢", style=discord.ButtonStyle.grey, custom_id="tafsir:ayah:page")
    async def page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        await interaction.response.send_modal(MoveModule(self, self.tafsir_data["count"]))

    async def get_page(self) -> discord.Embed:
        with open(f"json/surahs.json", "r", encoding="utf-8") as f:
            surahs = json.load(f)
        surah_name = surahs[self.tafsir_data["index"]-1]["titleAr"]
        embed = discord.Embed(
            title=f"سورة {surah_name} الآية رقم {self.postion} حسب التفسير المیسر", 
            description=f"قال الله تعالى ({self.surah_text['verse'][f'verse_' + str(self.postion)]})\n\n"
                        "-------------------------\n\n"
                        f"{self.tafsir_data['verse'][f'verse_' + str(self.postion)]}",
            color=0xffd430
        )
        embed.set_footer(text=f"{self.postion}/{self.tafsir_data['count']}")
        return embed

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
