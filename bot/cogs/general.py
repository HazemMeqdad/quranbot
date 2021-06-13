import discord
from discord import Embed, Colour
from discord.ext import commands
import time
import bot.db as db
import bot.config as config


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)

    @staticmethod
    def _time(time):
        time_ = 0
        if time == '30m':
            time_ = 1800
        elif time == '1h':
            time_ = 3600
        elif time == '2h':
            time_ = 7200
        elif time == '6h':
            time_ = 21600
        elif time == '12h':
            time_ = 43200
        elif time == '24h':
            time_ = 86400
        return time_

    @staticmethod
    def int_to_time(_time: int):
        new_time = ""
        if _time == 1800:
            new_time = "30m"
        elif _time == 3600:
            new_time = "1h"
        elif _time == 7200:
            new_time = "2h"
        elif _time == 21600:
            new_time = "6h"
        elif _time == 43200:
            new_time = "12h"
        elif _time == 86400:
            new_time = "24h"
        return new_time

    @commands.command(name="ping", help='ارسال سرعة اتصال البوت')
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def ping_command(self, ctx):
        before = time.monotonic()
        msg = await ctx.send('pong!!!')
        ping = (time.monotonic() - before) * 1000
        embed = Embed(
            description="Time taken: **%sms** \nDiscord API: **%sms**\nSpeedtest database: **%sms**" % (
                int(ping),
                round(self.bot.latency * 1000),
                db.speedtest()
            ),
            color=0xEFD881
        )
        embed.set_author(name=" فاذكروني", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="بطلب من: %s" % ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await msg.edit(content="pong!! %s" % self.emoji.ping, embed=embed)

    @commands.command(name="support", aliases=['server', "inv", "invite"], help="سيرفر الدعم الفني")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def support_command(self, ctx):
        embed = Embed(
            title='شكرا على اختيارك بوت فاذكروني 🌹',
            description="""
**{0} - Link:**
[click here](http://fdrbot.xyz/invite)
**{0} - Support:**
[click here](https://discord.gg/EpZJwpSgka)
**{0} - Vote:**
[click here](https://fdrbot.xyz/vote)
**{0} - Donation  تبرع:**
[click here](https://fdrbot.xyz/paypal) 
""".format(self.emoji.fdr_50),
            color=0xEFD881)
        embed.set_image(url="https://i8.ae/IjVZC")
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="بطلب من: {}".format(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name="info", aliases=['معلومات'], help="الحصول على معلومات الخادم المحفوظة")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def info_(self, ctx):
        data = db.Guild(ctx.guild).info
        embed = discord.Embed(
            description='إعدادات خادم: %s' % ctx.guild.name,
            color=0xEFD881
        )
        embed.add_field(name='%s - البادئه:' % self.emoji.fdr_50, value=data[2], inline=True)
        embed.add_field(name='%s - روم الاذكار:' % self.emoji.fdr_50, value=self.bot.get_channel(data[3]).mention if data[3] is not None else "لا يوجد", inline=True)
        embed.add_field(name='%s - وقت ارسال الاذكار:' % self.emoji.fdr_50, value=str(data[4]), inline=True)
        embed.add_field(name='%s - وضع تكرار الرسائل:' % self.emoji.fdr_50, value=self.emoji.on if data[5] == 1 else self.emoji.off, inline=True)
        embed.add_field(name='%s - وضع الامبد:' % self.emoji.fdr_50, value=self.emoji.on if data[6] == 1 else self.emoji.off, inline=True)
        embed.add_field(name='%s - ايدي الشارد:' % self.emoji.fdr_50, value=str(ctx.guild.shard_id), inline=True)
        embed.add_field(name='%s - سرعه الشارد:' % self.emoji.fdr_50, value=f"{int(self.bot.get_shard(ctx.guild.shard_id).latency * 1000)}ms <a:ping:845021892943544330>", inline=True)
        embed.set_author(name=" فاذكروني", icon_url=self.bot.user.avatar_url)
        embed.set_footer(text="بطلب من: %s" % ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
