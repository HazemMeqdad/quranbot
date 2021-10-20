import asyncio
import hikari
from hikari.messages import ButtonStyle
import lightbulb
from bot import Bot
import time
from bot import db
from bot.utils import Prayer, Sunnah



class General(lightbulb.Plugin):
    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__()

    @lightbulb.command(name="ping")
    async def ping_command(self, ctx: lightbulb.Context):
        # start message #
        before = time.monotonic()
        embed = hikari.Embed(
            description="```\nping\n```"
        )
        embed.set_footer(
            text="بوت فاذكروني لإحياء سنة ذكر الله",
            icon=ctx.bot.get_me().avatar_url
        )
        embed.set_thumbnail(ctx.bot.get_me().avatar_url)
        msg = await ctx.respond(embed=embed, reply=True, mentions_reply=False)

        ping = (time.monotonic() - before) * 1000
        # New message #
        embed = hikari.Embed(
            description="```py\nTime: %s ms\nLatency: %s ms\nDatabase: %s ms\n```" % (
                int(ping), round(ctx.bot.heartbeat_latency * 1000), db.speedtest()),
            color=0xFF0000
        )
        embed.set_footer(
            text="بوت فاذكروني لإحياء سنة ذكر الله",
            icon=ctx.bot.get_me().avatar_url
        )
        embed.set_thumbnail(ctx.bot.get_me().avatar_url)
        await msg.edit(embed=embed)

    @lightbulb.command(name="support", aliases=["inv", "invite"])
    async def support_command(self, ctx: lightbulb.Context):
        embed = hikari.Embed(
            title="**شكرا على اختيارك بوت فاذكروني 🌹**",
            color=0xffd430
        )
        embed.set_footer(text=self.bot.footer,
                         icon=ctx.bot.get_me().avatar_url)
        embed.set_thumbnail(ctx.bot.get_me().avatar_url)
        
        buttons = ctx.bot.rest.build_action_row()
        buttons = (
            buttons.add_button(ButtonStyle.LINK, f"https://discord.com/oauth2/authorize?client_id={ctx.bot.get_me().id}&permissions=8&scope=bot%20applications.commands")
                .set_label("أضافة البوت") 
                .add_to_container()
        )
        buttons = (
            buttons.add_button(ButtonStyle.LINK, "https://discord.gg/EpZJwpSgka") 
                .set_label("الدعم الفني") 
                .add_to_container()
        )
        buttons = (
            buttons.add_button(ButtonStyle.LINK, "https://fdrbot.xyz/paypal") 
                .set_label("التبرع") 
                .add_to_container()
        )
        await ctx.respond(embed=embed, reply=True, mentions_reply=False, component=buttons)

    @lightbulb.command(name="info", aliases=['معلومات'])
    async def info_command(self, ctx: lightbulb.Context):
        data = db.Guild(ctx.guild_id).info
        times = {1800: "30m", 3600: "1h", 7200: "2h",
                 21600: "6h", 43200: "12h", 86400: "24h"}
        hashtag = await self.bot.emojis.hashtag
        ping = await self.bot.emojis.ping
        off = await self.bot.emojis.off
        on = await self.bot.emojis.on

        embed = hikari.Embed(
            description="إعدادات خادم: %s" % ctx.get_guild().name,
            color=0xffd430
        )
        embed.add_field(
            name="%s - البادئه:" % hashtag,
            value=data.get("prefix"),
            inline=True
        )
        embed.add_field(
            name="%s - روم الاذكار:" % hashtag,
            value=ctx.bot.cache.get_guild_channel(data.get("channel")).mention if data.get(
                "channel") is not None else "لا يوجد",
            inline=True
        )
        embed.add_field(
            name="%s - وقت ارسال الاذكار:" % hashtag,
            value=times.get(data.get("time")),
            inline=True
        )
        embed.add_field(
            name="%s - وضع تكرار الرسائل:" % hashtag,
            value=on if data["anti_spam"] else off,
            inline=True
        )
        embed.add_field(
            name="%s - وضع الامبد:" % hashtag,
            value=on if data["embed"] else off,
            inline=True
        )
        embed.add_field(
            name="%s - ايدي الشارد:" % hashtag,
            value=str(ctx.get_guild().shard_id),
            inline=True)

        embed.add_field(
            name="%s - سرعه الشارد:" % hashtag,
            value=f"{round(ctx.bot.shards.get(ctx.get_guild().shard_id) .heartbeat_latency * 1000)}ms {ping}",
            inline=True
        )
        embed.set_footer(text=self.bot.footer,
                         icon=ctx.bot.get_me().avatar_url)
        embed.set_thumbnail(ctx.bot.get_me().avatar_url)
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)

    @lightbulb.command(name="zker", aliases=["ذكر", "اذكار", "أذكار"])
    async def zker_command(self, ctx: lightbulb.Context):
        x = db.Azkar().random
        embed = hikari.Embed(
            title=str(x.get("_id")),
            description=x.get("msg"),
            color=0xffd430
        )
        embed.set_footer(text=self.bot.footer,
                         icon=ctx.bot.get_me().avatar_url)
        embed.set_thumbnail(ctx.bot.get_me().avatar_url)
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)

    @lightbulb.command(name="azan")
    async def azan_command(self, ctx: lightbulb.Context, country: str):
        embed = hikari.Embed(
            description="🔍 جاري البحث عن الدولة او المدينة",
            color=0xffd430
        )
        msg = await ctx.respond(embed=embed, reply=True, mentions_reply=False)
        prayer = Prayer(country=country)
        x = prayer.country()
        if isinstance(x, dict):
            x = prayer.city()
            if isinstance(x, dict):
                embed = hikari.Embed(
                    description="لم استطع العثور على المدينه او الدوله",
                    color=0xffd430
                )
                await msg.edit(embed=embed)
                return
        embed = hikari.Embed(
            color=0xffd430,
        )
        embed.set_author(name=x.description, url=x.url)
        embed.add_field(name="صلاة الفجْر", value=x.fjer, inline=True)
        embed.add_field(name="الشروق", value=x.sunrise, inline=True)
        embed.add_field(name="صلاة الظُّهْر", value=x.noon, inline=True)
        embed.add_field(name="صلاة العَصر", value=x.pressing, inline=True)
        embed.add_field(name="صلاة المَغرب", value=x.moroccan, inline=True)
        embed.add_field(name="صلاة العِشاء", value=x.isha, inline=True)
        embed.set_footer(text=self.bot.footer)
        embed.set_thumbnail(ctx.bot.get_me().avatar_url)
        await msg.edit(embed=embed)

    @lightbulb.command(name="bot", aliases=["botinfo", "بوت"])
    async def botinfo_command(self, ctx: lightbulb.Context):
        hashtag = await self.bot.emojis.hashtag
        guilds_count = len(await ctx.bot.rest.fetch_my_guilds())

        embed = hikari.Embed(
            color=0xffd430,
            description=ctx.bot.get_me().username,
            url="http://fdrbot.xyz/invite"
        )
        embed.add_field(
            name="%s - الخوادم" % hashtag,
            value="{:,}".format(guilds_count),
            inline=True
        )
        embed.add_field(
            name="%s - تأخير الأستجابه" % hashtag,
            value="%sms" % round(ctx.bot.heartbeat_latency * 1000),
            inline=True
        )
        embed.add_field(
            name="%s - سرعة استجابة قواعد البيانات" % hashtag,
            value="%sms" % db.speedtest(),
            inline=True
        )
        embed.add_field(
            name="%s - أصدار النسخة" % hashtag,
            value="V3.0.0",
            inline=True
        )
        embed.add_field(
            name="%s - الشاردات" % hashtag,
            value="%s/%s" % (
                len(self.bot.shards),
                len([shard for shard in ctx.bot.shards.values() if shard.is_alive])
            ),
            inline=True
        )
        embed.add_field(
            name="%s - أصدار المكتبة" % hashtag,
            value="`hikari %s`" % hikari.__version__,
            inline=True
        )
        embed.set_footer(text=self.bot.footer,
                         icon=ctx.bot.get_me().avatar_url)
        embed.set_thumbnail(ctx.bot.get_me().avatar_url)
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)


    # @lightbulb.command(name="sunnah")
    # async def sunnah(self, ctx: lightbulb.Context, *, query: str):
    #     result = Sunnah(query)
    #     pages = [i for i in result.result().split("\n\n\n") if i != ""]
    #     embed = hikari.Embed(
    #         description=pages[0],
    #         color=0xffd430
    #     )
    #     embed.set_thumbnail(ctx.bot.get_me().avatar_url)
    #     embed.set_footer(text=f"1/{len(pages)}")
    #     raw = ctx.bot.rest.build_action_row()
    #     left = raw.add_button(ButtonStyle.SUCCESS, "left")
    #     left.set_label("يسار")
    #     left.set_emoji("⬅️")
    #     left.add_to_container()

    #     stop = raw.add_button(ButtonStyle.DANGER, "stop")
    #     stop.set_emoji("⏹️")
    #     stop.set_label("توقف")
    #     stop.add_to_container()

    #     right = raw.add_button(ButtonStyle.SUCCESS, "right")
    #     right.set_label("يمين")
    #     right.set_emoji("➡️")
    #     right.add_to_container()

    #     more = raw.add_button(ButtonStyle.LINK, result.url)
    #     more.set_emoji("ℹ️")
    #     more.set_label("المزيد")
    #     more.add_to_container()

    #     stats = True
    #     msg = await ctx.respond(embed=embed, component=raw)
        
    #     page = 1

    #     def check(res): 
    #         return res.interaction.user.id == ctx.author.id and \
    #             res.interaction.channel_id == ctx.channel_id
    #     while stats:
    #         try:
    #             event = await ctx.bot.wait_for(hikari.InteractionCreateEvent, predicate=check, timeout=30.0)
    #             await event.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_UPDATE)
    #         except asyncio.TimeoutError:
    #             left.set_is_disabled(True)
    #             stop.set_is_disabled(True)
    #             right.set_is_disabled(True)
    #             await msg.edit(component=raw)
    #             stats = False
    #             return
    #         custom_id = event.interaction.custom_id
    #         if custom_id == "stop":
    #             left.set_is_disabled(True)
    #             stop.set_is_disabled(True)
    #             right.set_is_disabled(True)
    #             await msg.edit(component=raw)
    #             stats = False
    #         elif custom_id == "left":
    #             page -= 1
    #             if page < 0:
    #                 page = len(pages) - 1
    #         elif custom_id == "right":
    #             page += 1
    #             if page > len(pages) - 1:
    #                 page = 0

    #         embed.description = pages[page]
    #         embed.set_footer(text=f"{page+1}/{len(pages)}")
    #         await msg.edit(embed=embed)


def load(bot: Bot):
    bot.add_plugin(General(bot))


def unload(bot: Bot):
    bot.remove_plugin("General")
