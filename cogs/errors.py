import discord
from discord.ext import commands
from discord.ext.commands import Cog
import asyncio


cooldown = []


class Errors(commands.Cog):
    def __init__(self, client):
        self.client = client

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        if ctx.author.id in cooldown:
            return
        elif isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            await ctx.send(f" يجب عليك الانتظار `{int(s)}` ثواني", delete_after=1)
            cooldown.append(ctx.author.id)
            await asyncio.sleep(10)
            cooldown.remove(ctx.author.id)
            return
        elif isinstance(ctx.channel, discord.channel.DMChannel):
            return
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("أنت بحاجة إلى صلاحيات `ADMINISTRATOR` .")
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        elif isinstance(error, commands.errors.ChannelNotFound):
            return
        elif isinstance(error, commands.errors.BotMissingPermissions):
            await ctx.send("البوت لا يمتلك صلاحيات كافيه")
        elif isinstance(error, commands.errors.MessageNotFound):
            return
        elif isinstance(error, commands.errors.CommandInvokeError):
            return
        else:
            pass


def setup(client):
    client.add_cog(Errors(client))


