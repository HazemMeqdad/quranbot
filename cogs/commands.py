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
        embed = Embed(
            description=f"سرعة اتصال البوت {round(self.client.latency * 1000)}ms",
            color=Colour.red()
        )
        embed.set_author(name=" فاذكروني", icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    @command(name="invite", aliases=['inv', "اضافه", "أضافه"])
    @cooldown(1, 10, commands.BucketType.user)
    @guild_only()
    async def invite_command(self, ctx):
        embed = Embed(
            description=f"**[إضغط هنا لإضافة البوت](https://discord.com/oauth2/authorize?client_id={self.client.user.id}&permissions=8&scope=bot)**",
            color=Colour.red()
        )
        embed.set_author(name=" فاذكروني", icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    @command(name="support", aliases=['server'])
    @cooldown(1, 10, commands.BucketType.user)
    @guild_only()
    async def support_command(self, ctx):
        embed = Embed(
            description="**[سيرفر الدعم الفني للبوت](https://discord.gg/FB8Wps5)**",
            color=Colour.red()
        )
        embed.set_author(name="فاذكروني", icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Commands(client))
