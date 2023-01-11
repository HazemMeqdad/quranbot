import discord
from discord.ext import commands
from discord import app_commands
from database.objects import Saves
from database import Database, DataNotFound
from utlits import BaseView
from utlits.modals import MoveModule
from utlits.msohaf_data import moshaf_types, moshafs
import typing as t

surahs_cache = []

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

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.grey, custom_id="moshaf:first")
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.edit_message()
        self.postion = 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.grey, custom_id="moshaf:prev")
    async def previous_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.send_message(content="لا يمكنك الرجوع للصفحة السابقة", ephemeral=True)
        self.postion -= 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.red, custom_id="moshaf:close")
    async def close(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        await interaction.response.edit_message(view=None)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.grey, custom_id="moshaf:next")
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        if self.postion == self.page_end:
            return await interaction.response.send_message(content="لا يمكنك التقدم للصفحة التالية", ephemeral=True)
        self.postion += 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.grey, custom_id="moshaf:last")
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        if self.postion == self.page_end:
            return await interaction.response.edit_message()
        self.postion = self.page_end
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="📌", style=discord.ButtonStyle.green, custom_id="moshaf:save")
    async def save_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذا المصحف", ephemeral=True)
        try:
            await Database.find_one("saves", {"_id": f"moshaf_{self.user_id}"})
        except DataNotFound:
            obj = Saves(f"moshaf_{self.user_id}", {"moshaf_type": self.moshaf_type, "page_number": self.postion})
            await Database.insert("saves", obj)
        await Database.update_one("saves", {"_id": f"moshaf_{self.user_id}"}, {"moshaf_type": self.moshaf_type, "page_number": self.postion})
        await interaction.response.send_message(content="تم حفظ الصفحة بنجاح", ephemeral=True)

    @discord.ui.button(label="🔢", style=discord.ButtonStyle.grey, custom_id="moshaf:page")
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

class Moshaf(commands.GroupCog, name="moshaf"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="open", description="عرض صفحات القرآن الكريم 📚")
    @app_commands.choices(moshaf_type=[app_commands.Choice(name=i["name"], value=i["value"]) for i in moshaf_types])
    @app_commands.describe(
        moshaf_type="نوع القرآن الكريم", 
        page="رقم الصفحة",
        hide="جعل الرسالة بينك و بين البوت فقط, True(أخفاء الرسالة)/False(أضهار الرسالة)"
    )
    async def open(self, interaction: discord.Interaction, moshaf_type: int, page: t.Optional[int] = None, hide: bool = False) -> None:
        db_data = await Database.find_one("saves", {"_id": f"moshaf_{interaction.user.id}"}, raise_not_found=False)
        data = db_data.data if db_data else None
        page_number = page if page else 1
        if (data is not None and data["moshaf_type"] == moshaf_type) and page is None:
            page_number = data["page_number"]
        moshaf = [i for i in moshaf_types if i["value"] == moshaf_type][0]

        embed = discord.Embed(title=moshaf["name"], color=0xffd430)
        embed.set_image(url=f"http://www.islamicbook.ws/{moshaf_type}/{page_number}.{moshafs[str(moshaf['value'])]['type']}")
        embed.set_footer(text=f"الصفحة {page_number}/{moshafs[str(moshaf['value'])]['page_end']}")
        view = MoshafView(moshaf_type, page_number, moshafs[str(moshaf['value'])]["page_end"], interaction.user.id)
        await interaction.response.send_message(
            embed=embed, 
            view=view,
            ephemeral=hide
        )
        view.message = await interaction.original_response()

    @app_commands.command(name="page", description="عرض صفحة معينة من القرآن الكريم 📚")
    @app_commands.choices(moshaf_type=[app_commands.Choice(name=i["name"], value=i["value"]) for i in moshaf_types])
    @app_commands.describe(
        moshaf_type="نوع القرآن الكريم",
        page="رقم الصفحة",
    )
    async def page(self, interaction: discord.Interaction, moshaf_type: int, page: int) -> None:
        moshaf = [i for i in moshaf_types if i["value"] == moshaf_type][0]
        if page > moshafs[str(moshaf['value'])]["page_end"] or page < 1:
            await interaction.response.send_message(f"الصفحة غير موجودة", ephemeral=True)
            return
        embed = discord.Embed(title=moshaf["name"], color=0xffd430)
        embed.set_image(url=f"http://www.islamicbook.ws/{moshaf_type}/{page}.{moshafs[str(moshaf['value'])]['type']}")
        embed.set_footer(text=f"الصفحة {page}/{moshafs[str(moshaf['value'])]['page_end']}")
        view = MoshafView(moshaf_type, page, moshafs[str(moshaf['value'])]["page_end"], interaction.user.id)
        await interaction.response.send_message(
            embed=embed, 
            view=view
        )
        view.message = await interaction.original_response()

    # async def surah_autocomplete(self, interaction: discord.Interaction, current: t.Optional[str] = None) -> t.List[app_commands.Choice]:
    #     global surahs_cache
    #     if not surahs_cache:
    #         async with aiohttp.ClientSession() as session:
    #             async with session.get(f"https://cdn.fdrbot.com/reciters/surah.json") as resp:
    #                 surahs_cache = await resp.json()
    #     if not current:
    #         return [app_commands.Choice(name=i["titleAr"], value=c+1) for c, i in enumerate(surahs_cache)][:25]
    #     return [app_commands.Choice(name=i["titleAr"], value=c+1) for c, i in enumerate(surahs_cache) if current in i["titleAr"]][:25]

    # @app_commands.command(name="surah", description="عرض سورة معينة من القرآن الكريم")
    # @app_commands.autocomplete(surah=surah_autocomplete)
    # @app_commands.describe(
    #     moshaf_type="نوع القرآن الكريم",
    #     surah="رقم السورة",
    # )
    # @app_commands.choices(moshaf_type=[app_commands.Choice(name=i["name"], value=i["value"]) for i in moshaf_types])
    # async def surah_command(self, interaction: discord.Interaction, moshaf_type: int, surah: int) -> None:
    #     moshaf = [i for i in moshaf_types if i["value"] == moshaf_type][0]
    #     if surah > 114 or surah < 1:
    #         await interaction.response.send_message(f"السورة غير موجودة", ephemeral=True)
    #         return
    #     page = int(surahs_cache[surah-1]["pages"])
    #     embed = discord.Embed(title=moshaf["name"], color=0xffd430)
    #     embed.set_image(url=f"http://www.islamicbook.ws/{moshaf_type}/{page}.{moshafs[str(moshaf['value'])]['type']}")
    #     embed.set_footer(text=f"الصفحة {page}/{moshafs[str(moshaf['value'])]['page_end']}")
    #     await interaction.response.send_message(
    #         embed=embed, 
    #         view=MoshafView(moshaf_type, page, moshafs[str(moshaf['value'])]["page_end"], interaction.user.id)
    #     )




async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moshaf(bot))
