import discord
from discord.ext import commands
from discord.ext.commands import command, has_permissions, cooldown, guild_only
from db.db import *


class Prefix(commands.Cog):
    def __init__(self, client):
        self.client = client

    @command(name="prefix", aliases=["setprefix"])
    @has_permissions(manage_guild=True)
    @cooldown(1, 10, commands.BucketType.guild)
    @guild_only()
    async def prefix_command(self, ctx, prefix=None):
        if prefix is None:
            await ctx.send("الرجاء إدخال بادئة لتعيينها.")
        if len(prefix) > 5:
            await ctx.send("لا يمكنك وضع بادئه اكثر من خمس حروف")
            return
        cr.execute("UPDATE guilds SET prefix = ? WHERE guild_id = ?", (prefix, ctx.guild.id))
        db.commit()
        await ctx.send(f"تم تغير بداية البوت الى {prefix}")


def setup(client):
    client.add_cog(Prefix(client))

