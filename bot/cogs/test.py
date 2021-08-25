import discord
from discord.ext import commands
from discord import ui, ButtonStyle


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="test")
    async def hhh(self, ctx):
        view = ui.View(timeout=30)
        select = ui.Select()
        select.add_option(label="HI", value="Hello")
        select.add_option(label="Man", value="Move")
        view.add_item(item=select)
        await ctx.send("I love you", view=view)
        res = await self.bot.wait_for("interaction")
        select.disabled = True
        await res.edit_original_message(content=f"{res.data['values'][0]}", view=view)


def setup(bot):
    bot.add_cog(Test(bot))

