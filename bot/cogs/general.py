import discord
from discord import Embed, Colour
from discord.ext import commands
import time
import bot.db as db
import bot.config as config
import prayer
from discord_components import Button, ButtonStyle

int_to_time = {1800: "30m", 3600: "1h", 7200: "2h", 21600: "6h", 43200: "12h", 86400: "24h"}


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)

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
        embed = Embed(
            title="**شكرا على اختيارك بوت فاذكروني 🌹**",
            color=self.bot.get_color(self.bot.color.gold),
        )
        embed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.reply(
            embed=embed,
            components=[
                [
                    Button(label="أضافة البوت", url="http://fdrbot.xyz/invite", style=ButtonStyle.URL),
                    Button(label="الدعم الفني", url="http://discord.gg/fdrbot", style=ButtonStyle.URL),
                    Button(label="التبرع", url="https://fdrbot.xyz/paypal", style=ButtonStyle.URL)
                ]
            ]
        )

    @commands.command(name="info", aliases=['معلومات'], help="الحصول على معلومات الخادم المحفوظة")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def info_(self, ctx):
        data = db.Guild(ctx.guild).info
        embed = discord.Embed(
            description='إعدادات خادم: %s' % ctx.guild.name,
            color=self.bot.get_color(self.bot.color.gold)
        )
        embed.add_field(name='%s - البادئه:' % self.emoji.fdr_50, value=data.get("prefix"), inline=True)
        embed.add_field(name='%s - روم الاذكار:' % self.emoji.fdr_50, value=self.bot.get_channel(data.get("channel")).mention if data.get("channel") is not None else "لا يوجد", inline=True)
        embed.add_field(name='%s - وقت ارسال الاذكار:' % self.emoji.fdr_50, value=int_to_time.get(data["time"]), inline=True)
        embed.add_field(name='%s - وضع تكرار الرسائل:' % self.emoji.fdr_50, value=self.emoji.on if data["anti_spam"] else self.emoji.off, inline=True)
        embed.add_field(name='%s - وضع الامبد:' % self.emoji.fdr_50, value=self.emoji.on if data["embed"] else self.emoji.off, inline=True)
        # embed.add_field(name='%s - ايدي الشارد:' % self.emoji.fdr_50, value=str(ctx.guild.shard_id), inline=True)
        # embed.add_field(name='%s - سرعه الشارد:' % self.emoji.fdr_50, value=f"{int(self.bot.get_shard(ctx.guild.shard_id).latency * 1000)}ms <a:ping:845021892943544330>", inline=True)
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
        e = discord.Embed(
            description="🔍 جاري البحث عن الدولة او المدينة",
            color=self.bot.get_color(self.bot.color.gold)
        )
        msg = await ctx.reply(embed=e)
        x = prayer.by_country(country)
        if x.get("msg"):
            x = prayer.by_city(country)
            if x.get("msg"):
                embed = discord.Embed(
                    description="لم استطع العثور على المدينه او الدوله",
                    color=self.bot.get_color(self.bot.color.gold)
                )
                await msg.edit(embed=embed)
                return
        embed = discord.Embed(
            color=self.bot.get_color(self.bot.color.gold),
        )
        embed.set_author(name=x["description"], url=x["url"])
        embed.add_field(name="صلاة الفجْر", value=x["fjer"])
        embed.add_field(name="الشروق", value=x["sunrise"])
        embed.add_field(name="صلاة الظُّهْر", value=x["noon"])
        embed.add_field(name="صلاة العَصر", value=x["pressing"])
        embed.add_field(name="صلاة المَغرب", value=x["moroccan"])
        embed.add_field(name="صلاة العِشاء", value=x["supper"])
        embed.set_footer(text=self.bot.footer)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await msg.edit(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
