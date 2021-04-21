import discord
from discord.ext import commands
import db


class Prefix(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="prefix", aliases=["setprefix", "set_prefix", "set-prefix"], help='أمر تعيين البادئة.', usage='[البادئه الجديده]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def prefix_command(self, ctx, prefix=None):
        if prefix is None:
            await ctx.send("الرجاء إدخال بادئة لتعيينها.")
        if len(prefix) > 5:
            await ctx.send("لا يمكنك وضع بادئه اكثر من خمس حروف")
            return
        db.set_prefix(ctx.guild, prefix)
        await ctx.send(f"تم تغير بداية البوت الى {prefix}")


def setup(client):
    client.add_cog(Prefix(client))

