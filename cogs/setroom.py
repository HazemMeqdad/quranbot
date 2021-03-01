import discord
from discord.ext import commands
from discord.ext.commands import command, has_permissions, cooldown, guild_only
from db.db import *
import asyncio


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
        cr.execute("UPDATE guilds SET channel = ? WHERE guild_id = ?", (channel.id, ctx.guild.id))
        commit()
        await ctx.send(f"! الله يكتب اجرك راح ارسل الاذكار للروم {channel.mention}")

    @command(name="remove", aliases=["removeroom"])
    @has_permissions(manage_guild=True)
    @cooldown(1, 10, commands.BucketType.guild)
    @guild_only()
    async def remove_command(self, ctx):
        # channel = cr.execute("SELECT channel FROM guilds WHEN ?", (ctx.guild.id,))
        # if channel is None:
        #     await ctx.send("انت لم تحدد روم لل ارسال حتى تحذفها")
        #     return
        message = await ctx.send("سيتم الغاء ارسال الاذكار هل انت موافق على هاذ الامر")
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]
        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
            if str(reaction.emoji) == "✅":
                cr.execute("UPDATE guilds SET channel = ? WHERE guild_id = ?", (None, ctx.guild.id))
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
