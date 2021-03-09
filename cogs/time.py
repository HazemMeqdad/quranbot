import discord
from discord.ext import commands
from discord.ext.commands import command, has_permissions, cooldown, guild_only
from db.db import *


class Time(commands.Cog):
    def __init__(self, client):
        self.client = client

    @command(name="time", aliases=["set_time"])
    @has_permissions(manage_guild=True)
    @cooldown(1, 10, commands.BucketType.guild)
    @guild_only()
    async def set_timer(self, ctx, time: str = None):
        if time is None:
            await ctx.send("يجب تحديد الوقت مثل: `{}time 1`")
            return
        channels = cr.execute("SELECT * FROM channels").fetchall()
        find = False
        for i in channels:
            if i[0] != ctx.guild.id:
                continue
            find = True
        if find is not True:
            await ctx.send("يجب عليك تثبيت روم لاستعمال هاذ الامر `{}setroom`".format(get_prefix(ctx)))
            return
        time_available = ["0.5", "1", "2", "6", "12", "24"]
        if time in time_available:
            cr.execute("UPDATE channels SET date_time = ? WHERE channel = ?", (time, ctx.guild.id))
            commit()
            await ctx.send(f"تم تعين وقت ارسال الاذكار كل `{time}`h")
            return
        await ctx.send("الاوقات المتوفره هي `{}`".format(", ".join(time_available)))


def setup(client):
    client.add_cog(Time(client))
