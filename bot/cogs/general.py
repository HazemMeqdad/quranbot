import discord
from discord import Embed
from discord.ext import commands
import time
import bot.db as db
import bot.config as config
import prayer
from discord_components import Button, ButtonStyle
import bot.lang as lang
from functools import reduce


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)
        self.int_to_time = {1800: "30m", 3600: "1h", 7200: "2h", 21600: "6h", 43200: "12h", 86400: "24h"}

    @commands.command(name="ping", help='ارسال سرعة اتصال البوت')
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def ping_command(self, ctx):
        before = time.monotonic()
        embed = discord.Embed(description="```\nping\n```")
        embed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        msg = await ctx.reply(embed=embed)
        ping = (time.monotonic() - before) * 1000
        embed = discord.Embed(
            description="```py\nTime: %s ms\nLatency: %s ms\nDatabase: %s ms\n```" % (int(ping), round(self.bot.latency * 1000), db.speedtest()),
            color=self.bot.get_color(self.bot.color.gold)
        )
        embed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await msg.edit(embed=embed)

    @commands.command(name="support", aliases=['server', "inv", "invite"], help="سيرفر الدعم الفني")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def support_command(self, ctx):
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        embed = Embed(
            title=_["thanks"],
            color=self.bot.get_color(self.bot.color.gold),
        )
        embed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.reply(
            embed=embed,
            components=[
                [
                    Button(label=_["add_bot"], url="http://fdrbot.xyz/invite", style=ButtonStyle.URL),
                    Button(label=_["support"], url="http://discord.gg/fdrbot", style=ButtonStyle.URL),
                    Button(label=_["paypal"], url="https://fdrbot.xyz/paypal", style=ButtonStyle.URL)
                ]
            ]
        )

    @commands.command(name="info", aliases=['معلومات'], help="الحصول على معلومات الخادم المحفوظة")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def info_(self, ctx):
        data = db.Guild(ctx.guild).info
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        embed = discord.Embed(
            description=_["settings_server"] % ctx.guild.name,
            color=self.bot.get_color(self.bot.color.gold)
        )
        embed.add_field(name=_["prefix"] % self.emoji.fdr_50, value=data.get("prefix"), inline=True)
        embed.add_field(name=_["channel"] % self.emoji.fdr_50, value=self.bot.get_channel(data.get("channel")).mention if data.get("channel") is not None else "لا يوجد", inline=True)
        embed.add_field(name=_["time"] % self.emoji.fdr_50, value=self.int_to_time.get(data["time"]), inline=True)
        embed.add_field(name=_["spam"] % self.emoji.fdr_50, value=self.emoji.on if data["anti_spam"] else self.emoji.off, inline=True)
        embed.add_field(name=_["embed"] % self.emoji.fdr_50, value=self.emoji.on if data["embed"] else self.emoji.off, inline=True)
        if self.bot.user.public_flags.verified_bot:
            embed.add_field(name=_["shard_id"] % self.emoji.fdr_50, value=str(ctx.guild.shard_id), inline=True)
            embed.add_field(name=_["shard_latency"] % self.emoji.fdr_50, value=f"{int(self.bot.get_shard(ctx.guild.shard_id).latency * 1000)}ms <a:ping:845021892943544330>", inline=True)
        embed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(name="zker", aliases=["ذكر", "اذكار", "أذكار"], help='ارسال ذكر عشوائي')
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def test(self, ctx):
        x = db.Azkar()
        rn = x.random
        embed = discord.Embed(
            title=str(rn["_id"]),
            description=rn["msg"],
            color=self.bot.get_color(self.bot.color.gold)
        )
        embed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(name='azan', aliases=["الأذان", "الصلاه", "الصلاة"], help='معرف وقت رفع الاذان في دولتك')
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def azan(self, ctx, country: str):
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        e = discord.Embed(
            description=_["search"],
            color=self.bot.get_color(self.bot.color.gold)
        )
        msg = await ctx.reply(embed=e)
        x = prayer.by_country(country)
        if x.get("msg"):
            x = prayer.by_city(country)
            if x.get("msg"):
                embed = discord.Embed(
                    description=_["if_not_found"],
                    color=self.bot.get_color(self.bot.color.gold)
                )
                await msg.edit(embed=embed)
                return
        embed = discord.Embed(
            color=self.bot.get_color(self.bot.color.gold),
        )
        prayers = _["prayers"]
        embed.set_author(name=x["description"], url=x["url"])
        embed.add_field(name=prayers["fjer"], value=x["fjer"])
        embed.add_field(name=prayers["sunrise"], value=x["sunrise"])
        embed.add_field(name=prayers["noon"], value=x["noon"])
        embed.add_field(name=prayers["pressing"], value=x["pressing"])
        embed.add_field(name=prayers["moroccan"], value=x["moroccan"])
        embed.add_field(name=prayers["supper"], value=x["supper"])
        embed.set_footer(text=self.bot.footer)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await msg.edit(embed=embed)

    @commands.group(name="bot", aliases=["botinfo", "بوت"], help='معلومات البوت')
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def info_bot(self, ctx):
        embed = discord.Embed()
        embed.add_field(name="الخوادم", value="{:,}".format(len(self.bot.guilds)))
        embed.add_field(name="المستخدمين", value="{:,}".format(reduce(lambda x, y: x + y, [i.member_count for i in self.bot.guilds])))
        embed.add_field(name="تأخير الأستجابه", value="%sms" % round(self.bot.latency * 1000))
        embed.add_field(name="سرعة استجابة قواعد البيانات", value="%sms" % db.speedtest())
        await ctx.reply(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
