import discord
from discord.ext import commands
from discord.ext.commands import Cog
import asyncio
import db

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
            await ctx.send(f"<:errors:843739803870035979> يجب عليك الانتظار `{int(s)}` ثواني", delete_after=1)
            cooldown.append(ctx.author.id)
            await asyncio.sleep(10)
            cooldown.remove(ctx.author.id)
            return
        elif isinstance(ctx.channel, discord.channel.DMChannel):
            return
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("أنت بحاجة إلى صلاحيات `ADMINISTRATOR` <:errors:843739803870035979>.")
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        elif isinstance(error, commands.errors.ChannelNotFound):
            return
        elif isinstance(error, commands.errors.BotMissingPermissions):
            await ctx.send("<:errors:843739803870035979> البوت لا يمتلك صلاحيات كافيه")
        elif isinstance(error, commands.errors.MessageNotFound):
            return
        elif isinstance(error, commands.errors.CommandInvokeError):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                description=f"{db.get_prefix(ctx.guild)}{ctx.command.name} {ctx.command.signature}",
                color=discord.Colour.red()
            ).set_author(name=ctx.command.cog_name)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.errors.BadArgument):
            embed = discord.Embed(
                description=f"{db.get_prefix(ctx.guild)}{ctx.command.name} {ctx.command.signature}",
                color=discord.Colour.red()
            ).set_author(name=ctx.command.cog_name)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, discord.errors.Forbidden):
            return
        else :
            error_channel = self.client.get_channel(847459844382130197)
            await error_channel.send("Error from %s (`%s`)\n%s" % (ctx.guild.name, ctx.guild.id, erorr))
            return


def setup(client):
    client.add_cog(Errors(client))
