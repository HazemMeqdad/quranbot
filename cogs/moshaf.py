import discord
from discord.ext import commands
from discord import app_commands
from .utlits.db import Database, SavesDatabase
from .utlits.views import MoshafView, OpenMoshafView
from .utlits.msohaf_data import moshaf_types, moshafs
import typing as t


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
        db = SavesDatabase()
        db_data = db.find_one(f"moshaf_{interaction.user.id}")
        data = db_data.data if db_data else None
        page_number = page if page else 1
        if (data is not None and data["moshaf_type"] == moshaf_type) and page is None:
            page_number = data["page_number"]
        moshaf = [i for i in moshaf_types if i["value"] == moshaf_type][0]

        embed = discord.Embed(title=moshaf["name"], color=0xffd430)
        embed.set_image(url=f"http://www.islamicbook.ws/{moshaf_type}/{page_number}.{moshafs[str(moshaf['value'])]['type']}")
        embed.set_footer(text=f"الصفحة {page_number}/{moshafs[str(moshaf['value'])]['page_end']}")
        await interaction.response.send_message(
            embed=embed, 
            view=MoshafView(moshaf_type, page_number, moshafs[str(moshaf['value'])]["page_end"], interaction.user.id),
            ephemeral=hide
        )

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
        await interaction.response.send_message(
            embed=embed, 
            view=MoshafView(moshaf_type, page, moshafs[str(moshaf['value'])]["page_end"], interaction.user.id)
        )

    @app_commands.command(name="setup", description="تعين لوحة للقرآن الكريم 📚")
    @app_commands.choices(moshaf_type=[app_commands.Choice(name=i["name"], value=i["value"]) for i in moshaf_types])
    @app_commands.describe(moshaf_type="نوع القرآن الكريم")
    @app_commands.default_permissions(manage_guild=True)
    async def setup(self, interaction: discord.Interaction, moshaf_type: int) -> None:
        db = Database()
        if not db.find_guild(interaction.guild.id):
            db.insert_guild(interaction.guild.id)
            
        moshaf = [i for i in moshaf_types if i["value"] == moshaf_type][0]

        embed = discord.Embed(title=moshaf["name"], color=0xffd430)
        embed.set_image(url=moshafs[str(moshaf["value"])]["cover"])
        embed.set_footer(text="أضغط على الزر الموجود أسفل لفتح المصحف")

        db.update_guild(interaction.guild.id, moshaf_type=moshaf_type)
        await interaction.response.send_message("تم تعيين لوحة القرآن الكريم بنجاح", ephemeral=True)
        await interaction.channel.send(embed=embed, view=OpenMoshafView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moshaf(bot))
