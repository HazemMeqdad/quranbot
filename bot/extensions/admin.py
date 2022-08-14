import hikari
import lightbulb
from lightbulb import Plugin, commands
from lightbulb.context.slash import SlashContext
from bot.database import GuildUpdateType
from hikari import Permissions


admin_plugin = Plugin("الأداره")

@admin_plugin.command()
@lightbulb.command("set", "set command group")
@lightbulb.implements(commands.SlashCommandGroup, commands.PrefixCommandGroup)
async def _set(ctx: SlashContext):
    ...

@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="mode",
    description="تحديد الوضع",
    type=bool
)
@lightbulb.command("embed", "تغير خاصية أرسال الأذكار إلى أمبد 📋")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def set_embed(ctx: SlashContext):
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    mode = ctx.raw_options.get("mode")
    msg = "تم تفعيل خاصية الأمبد بنجاح ✅" if mode else "تم الغاء خاصية الأمبد"
    ctx.bot.db.update_guild(guild, GuildUpdateType.embed, mode)
    await ctx.respond(msg)

times = {
    "30 دقيقة": 1800, 
    "ساعه": 3600, 
    "ساعتين": 7200,
    "6 ساعات": 21600,
    "12 ساعه": 43200,
    "24 ساعه": 86400,
}

@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="time", 
    description="أختر الوقت المناسب ⌛", 
    required=True, 
    choices=list(times.keys())
)
@lightbulb.command("time", "⌛ تغير وقت أرسال الأذكار")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def set_time(ctx: SlashContext):
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    if not guild.channel_id:
        await ctx.respond("يجب عليك تثبيت قناة أذكار حتى تستطيع أستخدام هذا الأمر 🙄", flags=hikari.MessageFlag.EPHEMERAL)
        return
    value = ctx.raw_options.get("time")
    ctx.bot.db.update_guild(guild, GuildUpdateType.time, times.get(value))
    await ctx.respond("تم تعين أرسال الأذكار كل **%s**" % value)


@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="channel",
    description="أختر القناة المناسبة",
    type=hikari.TextableChannel,
    required=False,
)
@lightbulb.command("channel", "أختيار قناة مخصصة للأذكار 📢")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def set_channel(ctx: SlashContext):
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    channel_id = ctx.raw_options.get("channel")

    # if not setup a channel
    if not channel_id:
        if not guild.channel_id:
            await ctx.respond("يجب عليك تثبيت قناة أذكار حتى تستطيع أستخدام هذا الأمر", flags=hikari.MessageFlag.EPHEMERAL)
            return
        ctx.bot.db.update_guild(guild, GuildUpdateType.channel_id, None)
        ctx.bot.db.update_guild(guild, GuildUpdateType.webhook, None)
        await ctx.respond("تم إيقاف أرسال الأذكار في قناة <#%s>" % guild.channel_idd)

    channel = ctx.bot.cache.get_guild_channel(channel_id)

    if channel.type != hikari.ChannelType.GUILD_TEXT:
        await ctx.respond("يجب التأكد من نوع القناة المحدده من انها كتابية", flags=hikari.MessageFlag.EPHEMERAL)
        return
    if int(channel_id) == guild.channel_id:
        await ctx.respond("لقد قمت بتحديد هذه القناة مسبقًا", flags=hikari.MessageFlag.EPHEMERAL)
        return
    try:
        webhooks = await ctx.bot.rest.fetch_channel_webhooks(channel_id)
    except hikari.ForbiddenError:
        await ctx.respond("البوت لا يمتلك صلاحيات كافية, تأكد من تفعيل خاصية `MANAGE_WEBHOOKS` في رتبة البوت")
        return
    bot_webhooks = list(filter(lambda webhook: webhook.author.id == ctx.bot.get_me().id, webhooks))
    if not bot_webhooks:
        webhook = await ctx.bot.rest.create_webhook(channel_id, "فاذكروني", avatar=ctx.bot.get_me().avatar_url)
    else:
        webhook = bot_webhooks[0]

    ctx.bot.db.update_guild(guild, GuildUpdateType.channel_id, channel.id)
    ctx.bot.db.update_guild(guild, GuildUpdateType.webhook, {"id": webhook.id, "token": webhook.token})
    await ctx.respond("الله يكتب أجرك سيتم أرسال الأذكار بشكل تلقائي للقناة الآتية %s" % channel.mention)

@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="role",
    description="أختر الرتبة",
    type=hikari.Role,
    required=False
)
@lightbulb.command("role", "تقيد صلاحيات التحكم بأوامر القرآن الكريم الصوتية ❗")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def set_role(ctx: SlashContext):
    role = ctx.raw_options.get("role")
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)

    if not role:
        if not guild.role_id:
            await ctx.respond("لقد تم الغاء تقيد صلاحيات التحكم بالقرآن الكريم")
            return 
        ctx.bot.db.update_guild(guild, GuildUpdateType.role_id, None)
        role = ctx.bot.cache.get_role(guild.role_id)
        if not role:
            await ctx.respond("لقد تم الغاء تقيد صلاحيات التحكم بالقرآن الكريم")
            return
        await ctx.respond("لقد تم الغاء تقيد صلاحيات التحكم بالقرآن الكريم من رتبة `%s`" % role.name)
        return

    ctx.bot.db.update_guild(guild, GuildUpdateType.role_id, role.id)
    await ctx.respond("لقد تم تعين رتبة %s للتحكم بالقرآن الكريم" % role.name)


def load(bot):
    bot.add_plugin(admin_plugin)


def unload(bot):
    bot.remove_plugin(admin_plugin)
