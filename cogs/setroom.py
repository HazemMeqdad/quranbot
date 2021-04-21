import discord
from discord.ext import commands
import db
import asyncio
from config import all
import random


class SetRoom(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="setroom", aliases=["channel", "setchannel", "set_room", "set_channel"], help='تحديد روم ارسال الاذكار', usage='[#الروم الجديده]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_channel_command(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            await ctx.send("يرجى منشن الروم او ايديه")
        db.set_channel(ctx.guild, channel)
        await ctx.send(f"! الله يكتب اجرك راح ارسل الاذكار للروم {channel.mention}")
        await channel.send(random.choice(all))

    @commands.command(name="remove", aliases=["removeroom"], help='توقف البوت عن إرسال الأذكار')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def remove_command(self, ctx):
        message = await ctx.send("سيتم الغاء ارسال الاذكار هل انت موافق على هاذ الامر")
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]
        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=60, check=check)
            if str(reaction.emoji) == "✅":
                db.remove_channel(ctx.guild)
                await message.edit(content="تم الغاء ارسال الاذكار")
            else:
                await message.delete()
        except asyncio.TimeoutError:
            await message.delete()


def setup(client):
    client.add_cog(SetRoom(client))
