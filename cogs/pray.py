import discord
from discord.ext import commands
from discord import app_commands
import json
import typing as t
from utlits import prosses_pray_embed, get_pray
from utlits import BaseView
from utlits.modals import MoveModule


class PrayView(BaseView):
    def __init__(self, user_id: int, prays: t.List[t.Dict[str, t.Any]], bot: commands.Bot, message: t.Optional[discord.Message] = None) -> None:
        super().__init__(timeout=3600)
        self.user_id = user_id
        self.message = message
        self.prays = prays
        self.bot = bot
        self.postion = 1

    def set_position(self, position: int) -> None:
        self.postion = position

    @discord.ui.button(label="⏮️", style=discord.ButtonStyle.grey, custom_id="pray:first")
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام قائمة الذكِر فهي لشخص أخر", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.edit_message()
        self.postion = 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.grey, custom_id="pray:prev")
    async def previous_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام قائمة الذكِر فهي لشخص أخر", ephemeral=True)
        if self.postion == 1:
            return await interaction.response.send_message(content="لا يمكنك الرجوع للذِكر السابق", ephemeral=True)
        self.postion -= 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.red, custom_id="pray:close")
    async def close(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام قائمة الذكِر فهي لشخص أخر", ephemeral=True)
        await interaction.response.edit_message(view=None)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.grey, custom_id="pray:next")
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام قائمة الذكِر فهي لشخص أخر", ephemeral=True)
        if self.postion == len(self.prays):
            return await interaction.response.send_message(content="لا يمكنك التقدم للذِكر التالي", ephemeral=True)
        self.postion += 1
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.grey, custom_id="pray:last")
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام قائمة الذكِر فهي لشخص أخر", ephemeral=True)
        if self.postion == len(self.prays):
            return await interaction.response.edit_message()
        self.postion = len(self.prays)
        await interaction.response.edit_message(embed=await self.get_page())

    @discord.ui.button(label="🔢", style=discord.ButtonStyle.grey, custom_id="pray:page")
    async def page(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام قائمة الذكِر فهي لشخص أخر", ephemeral=True)
        await interaction.response.send_modal(MoveModule(self, len(self.prays)))
    
    async def get_page(self) -> discord.Embed:
        embed = prosses_pray_embed(self.prays[self.postion - 1], self.bot.user.avatar.url)
        embed.set_footer(text=f"{self.postion}/{len(self.prays)}")
        return embed


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
