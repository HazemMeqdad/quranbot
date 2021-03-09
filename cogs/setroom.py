import discord
from discord.ext import commands
from discord.ext.commands import command, has_permissions, cooldown, guild_only
from db.db import *
import asyncio
from config import all
import random


class SetRoom(commands.Cog):
    def __init__(self, client):
        self.client = client

    @command(name="setroom", aliases=["set_channel"])
    @has_permissions(manage_guild=True)
    @cooldown(1, 10, commands.BucketType.guild)
    @guild_only()
    async def set_channel_command(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            await ctx.send("يرجى منشن الروم او ايديه")
        cr.execute(
            "DELETE FROM channels WHERE guild_id = ? and guild_name = ?",
            (ctx.guild.id, ctx.guild.name))
        commit()
        cr.execute(
            "INSERT OR IGNORE INTO channels(guild_id, guild_name, channel) VALUES(?, ?, ?)",
            (ctx.guild.id, ctx.guild.name, channel.id))
        commit()

        await ctx.send(f"! الله يكتب اجرك راح ارسل الاذكار للروم {channel.mention}")
        await channel.send(random.choice(all))

    @command(name="remove", aliases=["removeroom"])
    @has_permissions(manage_guild=True)
    @cooldown(1, 10, commands.BucketType.guild)
    @guild_only()
    async def remove_command(self, ctx):
        message = await ctx.send("سيتم الغاء ارسال الاذكار هل انت موافق على هاذ الامر")
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]
        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
            if str(reaction.emoji) == "✅":
                cr.execute(
                    "DELETE FROM channels WHERE guild_id = ? and guild_name = ?",
                    (ctx.guild.id, ctx.guild.name))
                commit()
                await message.edit(content="تم الغاء ارسال الاذكار")
            elif str(reaction.emoji) == "✅":
                await message.edit(content="تم الغاء ارسال الاذكار")
            else:
                await message.delete()
        except asyncio.TimeoutError:
            await message.delete()


def setup(client):
    client.add_cog(SetRoom(client))
