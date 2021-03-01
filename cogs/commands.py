import discord
from discord import Embed, Colour
from discord.ext import commands
from discord.ext.commands import command, cooldown, guild_only


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @command(name="ping")
    @cooldown(1, 10, commands.BucketType.user)
    @guild_only()
    async def ping_command(self, ctx):
        msg = await ctx.send("pong!!!")
        await msg.edit(content=f"سرعة اتصال البوت {round(self.client.latency * 1000)}ms")

    @command(name="invite", aliases=['inv', "اضافه", "أضافه"])
    @cooldown(1, 10, commands.BucketType.user)
    @guild_only()
    async def invite_command(self, ctx):
        await ctx.send(embed=Embed(
            description=f"**[إضغط هنا لإضافة البوت](https://discord.com/oauth2/authorize?client_id={self.client.user.id}&permissions=8&scope=bot)**"
        ))

    @command(name="support", aliases=['server'])
    @cooldown(1, 10, commands.BucketType.user)
    @guild_only()
    async def support_command(self, ctx):
        await ctx.send(embed=Embed(
            description="**[سيرفر الدعم الفني للبوت](https://discord.gg/FB8Wps5)**"
        ).set_thumbnail(
            url="https://cdn.discordapp.com/avatars/728782652454469662/bfac83755b54d890fc8850bb6b3f09a7.png?size=1024")
        )


def setup(client):
    client.add_cog(Commands(client))
