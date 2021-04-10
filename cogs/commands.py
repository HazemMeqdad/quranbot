import discord
from discord import Embed, Colour
from discord.ext import commands
import time


class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="ping", help='ارسال سرعة اتصال البوت')
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def ping_command(self, ctx):
        before = time.monotonic()
        msg = await ctx.send('pong!!!')
        ping = (time.monotonic() - before) * 1000
        embed = Embed(
            description="`-` Time taken: **{}ms** <:Online:826179501888766004>\n`-` Discord API: **{}ms** <:Online:826179501888766004>".format(
            int(ping),
            round(self.client.latency * 1000))
        )
        embed.set_author(name=" فاذكروني", icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await msg.edit(content="pong!! <a:discord:795053266111168562>", embed=embed)

    @commands.command(name="invite", aliases=['inv', "اضافه", "أضافه"], help='لإضافة البوت الى سيرفرك')
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def invite_command(self, ctx):
        embed = Embed(
            title='شكرا على اختيارك بوت فاذكروني 🌹',
            description="""
**Link:**
[click here](https://discord.com/oauth2/authorize?client_id=728782652454469662&permissions=8&scope=bot)
**Support:**
[click here](https://discord.gg/MYEvygbHXt)
**Vote:**
[click here](https://top.gg/bot/728782652454469662/vote)
**Support us:**
[click here](https://www.paypal.com/paypalme/codexv)     
        """,
            color=0xEFD881)
        embed.set_image(url="https://i8.ae/kJcVx")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text="بطلب من: {}".format(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="support", aliases=['server'], help="سيرفر الدعم الفني")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def support_command(self, ctx):
        embed = Embed(
            title='شكرا على اختيارك بوت فاذكروني 🌹',
            description="""
        **Link:**
        [click here](https://discord.com/oauth2/authorize?client_id=728782652454469662&permissions=8&scope=bot)
        **Support:**
        [click here](https://discord.gg/MYEvygbHXt)
        **Vote:**
        [click here](https://top.gg/bot/728782652454469662/vote)
        **Support us:**
        [click here](https://www.paypal.com/paypalme/codexv)     
                """,
            color=0xEFD881)
        embed.set_image(url="https://i8.ae/djPWO")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text="بطلب من: {}".format(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Commands(client))
