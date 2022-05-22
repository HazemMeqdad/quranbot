import typing
from hikari.embeds import EmbedField
from hikari.messages import MessageFlag
import hikari
from hikari import ButtonStyle
import time
from lightbulb import Plugin, commands
import lightbulb
from lightbulb.commands.slash import SlashCommandGroup
from lightbulb.context.slash import SlashContext
from bot.bot import Bot
from bot.manger.manger import Manger
from bot.utils import Prayer


general_plugin = Plugin("general")

@general_plugin.command()
@lightbulb.command("ping", "سرعة اتصال البوت")
@lightbulb.implements(commands.SlashCommand, commands.PrefixCommand)
async def ping(ctx: SlashContext):
    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    embed.set_thumbnail(ctx.bot.get_me().avatar_url)
    embed.description = "```\nping\n```"
    before = time.monotonic()
    await ctx.respond(embed=embed)
    ping = (time.monotonic() - before) * 1000

    embed.description = "```python\nTime: %s ms\nLatency: %s ms\nDatabase: %s ms\n```" % (
        int(ping), round(ctx.bot.heartbeat_latency * 1000),
        ctx.bot.db.speed_test()
    )
    await ctx.edit_last_response(embed=embed)

@general_plugin.command()
@lightbulb.command("support", "طلب الدعم الفني")
@lightbulb.implements(commands.SlashCommand, commands.PrefixCommand)
async def support(ctx: SlashContext):
    embed = hikari.Embed(
        title="**شكراً على أختيارك بوت فاذكروني 🌹**",
        color=0xffd430
    )
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    buttons = ctx.bot.rest.build_action_row()
    buttons = (
        buttons.add_button(
            ButtonStyle.LINK, f"https://discord.com/oauth2/authorize?client_id={ctx.bot.get_me().id}&permissions=8&scope=bot%20applications.commands")
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
        buttons.add_button(ButtonStyle.LINK, "https://fdrbot.com")
        .set_label("لوحة التحكم")
        .add_to_container()
    )
    embed.set_thumbnail(ctx.bot.get_me().avatar_url)
    await ctx.respond(embed=embed, component=buttons)

@general_plugin.command()
@lightbulb.command("info", "طلب معلومات الخادم")
@lightbulb.implements(commands.SlashCommand, commands.PrefixCommand)
async def info(ctx: SlashContext):
    data = ctx.bot.db.fetch_guild(ctx.guild_id)
    times = {1800: "30m", 3600: "1h", 7200: "2h",
             21600: "6h", 43200: "12h", 86400: "24h"}

    embed = hikari.Embed(
        description="إعدادات خادم: %s" % ctx.get_guild().name,
        color=0xffd430
    )
    embed.add_field(
        name="%s - روم الاذكار:" % ctx.bot.emojis.hashtag,
        value=ctx.bot.cache.get_guild_channel(
            data.channel_id).mention if data.channel_id is not None else "لا يوجد",
        inline=True
    )
    embed.add_field(
        name="%s - وقت ارسال الاذكار:" % ctx.bot.emojis.hashtag,
        value=times.get(data.time),
        inline=True
    )
    embed.add_field(
        name="%s - وضع الامبد:" % ctx.bot.emojis.hashtag,
        value=ctx.bot.emojis.on if data.embed else ctx.bot.emojis.off,
        inline=True
    )
    embed.add_field(
        name="%s - رتبة القرآن الكريم" % ctx.bot.emojis.hashtag,
        value=ctx.get_guild().get_role(data.role_id).mention if data.role_id is not None else "لا يوجد",
        inline=True
    )
    embed.add_field(
        name="%s - ايدي الشارد:" % ctx.bot.emojis.hashtag,
        value=str(ctx.get_guild().shard_id),
        inline=True
    )
    embed.add_field(
        name="%s - سرعه الشارد:" % ctx.bot.emojis.hashtag,
        value=f"{round(ctx.bot.shards.get(ctx.get_guild().shard_id) .heartbeat_latency * 1000)}ms",
        inline=True
    )
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    embed.set_thumbnail(ctx.bot.get_me().avatar_url)
    await ctx.respond(embed=embed)

@general_plugin.command()
@lightbulb.option(
    name="city_or_country",
    description="الدولة المراد معرفه وقت الصلاة بيها", 
    required=True
)
@lightbulb.command("azan", "معرفة وقت الأذان في المدينة الخاصه بك")
@lightbulb.implements(commands.SlashCommand, commands.PrefixCommand)
async def azan(ctx: SlashContext):
    country = ctx.options.city_or_country
    embed = hikari.Embed(color=0xffd430)
    prayer = Prayer(country=country)
    x = prayer.country()
    if isinstance(x, dict):
        x = prayer.city()
        if isinstance(x, dict):
            embed.description = "لم أستطع العثور على المدينة او الدولة المطلوبة"
            await ctx.respond(embed=embed)
            return
    embed.set_author(name=x.description, url=x.url)
    embed.add_field(name="صلاة الفجْر", value=x.fjer, inline=True)
    embed.add_field(name="الشروق", value=x.sunrise, inline=True)
    embed.add_field(name="صلاة الظُّهْر", value=x.noon, inline=True)
    embed.add_field(name="صلاة العَصر", value=x.pressing, inline=True)
    embed.add_field(name="صلاة المَغرب", value=x.moroccan, inline=True)
    embed.add_field(name="صلاة العِشاء", value=x.isha, inline=True)
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    embed.set_thumbnail(ctx.bot.get_me().avatar_url)
    try:
        await ctx.respond(embed=embed)
    except hikari.BadRequestError:
        embed.set_author(name=x.description)
        await ctx.respond(embed=embed)

@general_plugin.command()
@lightbulb.command("bot", "جلب معلومات البوت")
@lightbulb.implements(commands.SlashCommand, commands.PrefixCommand)
async def bot(ctx: SlashContext):
    hashtag = ctx.bot.emojis.hashtag

    guilds_count = len(ctx.bot.cache.get_guilds_view())

    embed = hikari.Embed(
        color=0xffd430,
        description=ctx.bot.get_me().username,
        url="http://fdrbot.com/invite"
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
        name="%s - سرعة أستجابة قواعد البيانات" % hashtag,
        value="%sms" % ctx.bot.db.speed_test(),
        inline=True
    )
    embed.add_field(
        name="%s - أصدار النسخة" % hashtag,
        value="V3.0.2",
        inline=True
    )
    embed.add_field(
        name="%s - الشاردات" % hashtag,
        value="%s/%s" % (
             len(ctx.bot.shards),
             len([shard for shard in ctx.bot.shards.values() if shard.is_alive])
        ),
        inline=True
    )
    embed.add_field(
        name="%s - أصدار المكتبة" % hashtag,
        value="`hikari %s`" % hikari.__version__,
        inline=True
    )
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    embed.set_thumbnail(ctx.bot.get_me().avatar_url)
    await ctx.respond(embed=embed)

@general_plugin.command()
@lightbulb.command("invite", "أضافة البوت إلى خادمك")
@lightbulb.implements(commands.SlashCommand, commands.PrefixCommand)
async def invite(ctx: SlashContext):
    await ctx.respond(
        f"<https://discord.com/oauth2/authorize?client_id={ctx.bot.get_me().id}&permissions=8&scope=bot%20applications.commands>",
        flags=MessageFlag.EPHEMERAL
    )

@general_plugin.command()
@lightbulb.command("zker", "أرسال ذكر عشوائي")
@lightbulb.implements(commands.SlashCommand, commands.PrefixCommand)
async def zker(ctx: SlashContext):
    random_zker = ctx.bot.db.get_random_zker()
    embed = hikari.Embed(
        title=str(random_zker.id),
        description=random_zker.content,
        color=0xffd430
    )
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    await ctx.respond(embed=embed)

@general_plugin.command()
@lightbulb.command("help", "أرسل هذا الرسالة للحصول على مساعدة")
@lightbulb.implements(commands.SlashCommand, commands.PrefixCommand)
async def help_command(ctx: SlashContext):
    category = {
        "quran": "القرآن الكريم",
        "set": "الأداره",
        "moshaf": "المصحف",
    }
    embed = hikari.Embed(color=0xffd430)
    commands = ctx.bot._slash_commands
    description = ""
    description = "[لوحة التحكم](https://fdrbot.com) | [أضف البوت](https://discordapp.com/oauth2/authorize?client_id={}&permissions=8&scope=bot%20applications.commands) | [الدعم الفني](https://discord.gg/VX5F54YNuy)\n".format(ctx.bot.get_me().id.__str__()) 
    fields: typing.List[EmbedField] = []
    for name, command in commands.items():
        if isinstance(command, SlashCommandGroup):
            value = ""
            for com_name, com in command.subcommands.items():
                value += f"`/{name} {com_name}` - {com.description}\n"
            fields.append(EmbedField(name=category.get(name, name), value=value, inline=True))
            continue
        if command.hidden:
            continue
        description += f"`/{name}` - {command.description}\n"
    embed.description = description
    embed._fields = fields
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    await ctx.respond(embed=embed)


def load(bot: Bot):
    bot.add_plugin(general_plugin)


def unload(bot: Bot):
    bot.remove_plugin(general_plugin)
