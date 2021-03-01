import discord
from discord.ext import commands
from discord.ext.commands import Cog
from discord import Embed, Colour
from db import db
import time


class Errors(commands.Cog):
    def __init__(self, client):
        self.client = client

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        # print(db.get_cooldown())
        if ctx.author.id in db.get_cooldown():
            return
        elif isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            await ctx.send(f" يجب عليك الانتظار `{int(s)}` ثواني")
            db.cr.execute("INSERT OR IGNORE INTO cooldown(user_id) VALUES(?)", (ctx.author.id,))
            db.commit()
            time.sleep(1)
            await ctx.message.delete()
            return
        elif isinstance(ctx.channel, discord.channel.DMChannel):
            return
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send("أنت بحاجة إلى صلاحيات.")
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        elif isinstance(error, commands.errors.ChannelNotFound):
            return
        elif isinstance(error, commands.errors.BotMissingPermissions):
            await ctx.send("البوت لا يمتلك صلاحيات كافيه")
        elif isinstance(error, commands.errors.MessageNotFound):
            return
        else:
            print(error)


def setup(client):
    client.add_cog(Errors(client))


