from hikari.interactions.base_interactions import ResponseType
from hikari.messages import MessageFlag
from bot.plugins.slash_commands.admin import Embed
from sys import flags
import hikari
from hikari import ButtonStyle
import time
from lightbulb.slash_commands.context import SlashCommandContext
from lightbulb.slash_commands import SlashCommand
from lightbulb.slash_commands import Option
import typing
from bot import Bot
from bot import db
from bot.utils import Prayer
from lightbulb.errors import CommandError

GUILD_ID = 872200812129054730


class Ping(SlashCommand):
    name = "ping"
    description = "ارسال سرعة اتصال البوت"
    enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        before = time.monotonic()
        embed = hikari.Embed(color=0xffd430)
        embed.set_footer(
            text="بوت فاذكروني لإحياء سنة ذكر الله",
            icon=context.bot.get_me().avatar_url
        )
        embed.set_thumbnail(context.bot.get_me().avatar_url)
        embed.description = "```\nping\n```"
        await context.interaction.edit_initial_response(embed=embed)
        ping = (time.monotonic() - before) * 1000

        embed.description = "```python\nTime: %s ms\nLatency: %s ms\nDatabase: %s ms\n```" % (
            int(ping), round(context.bot.heartbeat_latency * 1000),
            db.speedtest()
        )
        await context.interaction.edit_initial_response(embed=embed)


class Support(SlashCommand):
    name = "support"
    description = "طلب الدعم الفني"
    enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        embed = hikari.Embed(
            title="**شكرا على اختيارك بوت فاذكروني 🌹**",
            color=0xffd430
        )
        embed.set_footer(
            text="بوت فاذكروني لإحياء سنة ذكر الله",
            icon=context.bot.get_me().avatar_url
        )
        buttons = context.bot.rest.build_action_row()
        buttons = (
            buttons.add_button(
                ButtonStyle.LINK, f"https://discord.com/oauth2/authorize?client_id={context.bot.get_me().id}&permissions=8&scope=bot%20applications.commands")
            .set_label("أضافة البوت")
            .add_to_container()
        )
        buttons = (
            buttons.add_button(
                ButtonStyle.LINK, "https://discord.gg/VX5F54YNuy")
            .set_label("الدعم الفني")
            .add_to_container()
        )
        buttons = (
            buttons.add_button(ButtonStyle.LINK, "https://fdrbot.xyz/paypal")
            .set_label("التبرع")
            .add_to_container()
        )
        embed.set_thumbnail(context.bot.get_me().avatar_url)
        await context.interaction.edit_initial_response(embed=embed, component=buttons)


class Info(SlashCommand):
    name = "info"
    description = "طلب معلومات الخادم"
    enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        data = db.Guild(context.guild_id).info
        times = {1800: "30m", 3600: "1h", 7200: "2h",
                 21600: "6h", 43200: "12h", 86400: "24h"}
        hashtag = await self.bot.emojis.hashtag
        ping = await self.bot.emojis.ping
        off = await self.bot.emojis.off
        on = await self.bot.emojis.on

        embed = hikari.Embed(
            description="إعدادات خادم: %s" % context.get_guild().name,
            color=0xffd430
        )
        embed.add_field(
            name="%s - البادئه:" % hashtag,
            value=data.get("prefix"),
            inline=True
        )
        embed.add_field(
            name="%s - روم الاذكار:" % hashtag,
            value=context.bot.cache.get_guild_channel(data.get("channel")).mention if data.get(
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
            value=str(context.get_guild().shard_id),
            inline=True)

        embed.add_field(
            name="%s - سرعه الشارد:" % hashtag,
            value=f"{round(context.bot.shards.get(context.get_guild().shard_id) .heartbeat_latency * 1000)}ms {ping}",
            inline=True
        )
        embed.set_footer(text=self.bot.footer,
                         icon=context.bot.get_me().avatar_url)
        embed.set_thumbnail(context.bot.get_me().avatar_url)
        await context.interaction.edit_initial_response(embed=embed)


class Azan(SlashCommand):
    name = "azan"
    description = "معرفة وقت الاذان في المدينة الخاصه بك"
    enable_guilds = (GUILD_ID,)

    country: typing.Optional[str] = Option(
        description="الدولة المراد معرفه وقت الصلاة بيها", name="المدينة", required=True)

    async def callback(self, context: SlashCommandContext):
        country = context.options.get("المدينة").value
        embed = hikari.Embed(color=0xffd430)
        prayer = Prayer(country=country)
        x = prayer.country()
        if isinstance(x, dict):
            x = prayer.city()
            if isinstance(x, dict):
                raise CommandError("لم استطع العثور على المدينه او الدوله")
        embed.set_author(name=x.description, url=x.url)
        embed.add_field(name="صلاة الفجْر", value=x.fjer, inline=True)
        embed.add_field(name="الشروق", value=x.sunrise, inline=True)
        embed.add_field(name="صلاة الظُّهْر", value=x.noon, inline=True)
        embed.add_field(name="صلاة العَصر", value=x.pressing, inline=True)
        embed.add_field(name="صلاة المَغرب", value=x.moroccan, inline=True)
        embed.add_field(name="صلاة العِشاء", value=x.isha, inline=True)
        embed.set_footer(text=self.bot.footer)
        embed.set_thumbnail(context.bot.get_me().avatar_url)
        await context.interaction.create_initial_response(ResponseType.MESSAGE_CREATE, embed=embed)


class BotInfo(SlashCommand):
    name = "bot"
    description = "جلب معلومات البوت"
    enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        hashtag = await self.bot.emojis.hashtag
        guilds_count = len(await context.bot.rest.fetch_my_guilds())

        embed = hikari.Embed(
            color=0xffd430,
            description=context.bot.get_me().username,
            url="http://fdrbot.xyz/invite"
        )
        embed.add_field(
            name="%s - الخوادم" % hashtag,
            value="{:,}".format(guilds_count),
            inline=True
        )
        embed.add_field(
            name="%s - تأخير الأستجابه" % hashtag,
            value="%sms" % round(context.bot.heartbeat_latency * 1000),
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
                len([shard for shard in context.bot.shards.values() if shard.is_alive])
            ),
            inline=True
        )
        embed.add_field(
            name="%s - أصدار المكتبة" % hashtag,
            value="`hikari %s`" % hikari.__version__,
            inline=True
        )
        embed.set_footer(text=self.bot.footer,
                         icon=context.bot.get_me().avatar_url)
        embed.set_thumbnail(context.bot.get_me().avatar_url)
        await context.interaction.edit_initial_response(embed=embed)


class HelpCommand(SlashCommand):
    name = "help"
    description = "جلب معلومات البوت"
    enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        embed = hikari.Embed(
            color=0xffd430,
            description="شكرا على استخدامك اوامر الشرطه المائله الخاصه ببوت فاذكروني\nيمكننك كتابه شرطه مائلة و العثور على جميع الاوامر"
        )
        await context.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            flags=hikari.MessageFlag.EPHEMERAL,
            embed=embed
        )


class Invite(SlashCommand):
    name = "invite"
    description = "أضافة البوت إلى خادمك"
    enable_guilds = (GUILD_ID,)
    
    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE, 
            f"<https://discord.com/oauth2/authorize?client_id={context.bot.get_me().id}&permissions=8&scope=bot%20applications.commands>",
            flags=MessageFlag.EPHEMERAL    
        )


def load(bot: Bot):
    bot.add_slash_command(Ping, True)
    bot.add_slash_command(Support, True)
    bot.add_slash_command(Info, True)
    bot.add_slash_command(Azan)
    bot.add_slash_command(BotInfo, True)
    bot.add_slash_command(HelpCommand, True)
    bot.add_slash_command(Invite, True)


def unload(bot: Bot):
    bot.remove_slash_command("ping")
    bot.remove_slash_command("support")
    bot.remove_slash_command("info")
    bot.remove_slash_command("azan")
    bot.remove_slash_command("bot")
    bot.remove_slash_command("help")
    bot.remove_slash_command("invite")
