import hikari
import lightbulb
from lightbulb import Plugin, commands
from lightbulb.context.slash import SlashContext
from bot.database import GuildUpdateType
from bot.utils import command_error
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
@lightbulb.command("embed", "تغير خاصيه ارسال الاذكار الى امبد")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def set_embed(ctx: SlashContext):
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    mode = ctx.raw_options.get("mode")
    msg = "تم تفعيل خاصية الأمبد" if mode else "تم اطفاء خاصية الأمبد"
    ctx.bot.db.update_guild(guild, GuildUpdateType.embed, mode)
    embed = hikari.Embed(
        description=msg,
        color=0xffd430
    )
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    await ctx.respond(embed=embed)

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
    description="أختر الوقت المناسب", 
    required=True, 
    choices=list(times.keys())
)
@lightbulb.command("time", "تغير وقت ارسال الأذكار")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def set_time(ctx: SlashContext):
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    if not guild.channel:
        return await command_error(ctx, "يجب عليك تثبيت روم لاستعمال هاذ الامر")
    value = ctx.raw_options.get("time")
    ctx.bot.db.update_guild(guild, GuildUpdateType.time, times.get(value))
    embed.description = "تم تغير وقت ارسال الأذكار إلى: **%s**" % value
    await ctx.respond(embed=embed)


@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="channel",
    description="أختر القناة المناسبة",
    type=hikari.TextableChannel,
    required=False,
)
@lightbulb.command("channel", "أختيار قناة الأذكار")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def set_channel(ctx: SlashContext):
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    channel_id = ctx.raw_options.get("channel")
    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)

    # if not setup a channel
    if not channel_id:
        if not guild.channel_id:
            return await command_error(ctx, "انت لم تقم بتثبيت الروم من قبل")
        ctx.bot.db.update_guild(guild, GuildUpdateType.channel_id, None)
        ctx.bot.db.update_guild(guild, GuildUpdateType.webhook, None)
        embed.description = "تم إيقاف أرسال الأذكار في قناة <#%s>" % guild.channel_id
        await ctx.respond(embed=embed)

    channel = ctx.bot.cache.get_guild_channel(channel_id)

    if channel.type != hikari.ChannelType.GUILD_TEXT:
        return await command_error(ctx, "يجب التأكد من نوع القناة المحدده من انها كتابية")
    if int(channel_id) == guild.channel_id:
        return await command_error(ctx, "لقد قمت بتحديد هذا الروم مسبقًا")

    webhook = await ctx.bot.rest.create_webhook(channel_id, "فاذكروني", avatar=ctx.bot.get_me().avatar_url.url)

    ctx.bot.db.update_guild(guild, GuildUpdateType.channel_id, channel.id)
    ctx.bot.db.update_guild(guild, GuildUpdateType.webhook, {"id": webhook.id, "token": webhook.token})
    embed.description = "الله يكتب أجرك سيتم أرسال الأذكار بشكل تلقائي للقناة الآتية %s" % channel.mention
    await ctx.respond(embed=embed)

@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="role",
    description="أختر الرتبة",
    type=hikari.Role,
    required=False
)
@lightbulb.command("role", "تقيد صلاحيات التحكم بالقرآن الكريم")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def set_role(ctx: SlashContext):
    role = ctx.raw_options.get("role")
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)

    if not role:
        ctx.bot.db.update_guild(guild, GuildUpdateType.role_id, None)
        embed.description = "لقد تم الغاء تقيد صلاحيات التحكم بالقرآن الكريم من رتبة <@&{}>".format(guild.role_id)
        await ctx.respond(embed=embed)
        return

    ctx.bot.db.update_guild(guild, GuildUpdateType.role_id, role.id)
    embed.description = "لقد تم تعين رتبة <@&{}> للتحكم بالقرآن الكريم".format(role.id)
    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(admin_plugin)


def unload(bot):
    bot.remove_plugin(admin_plugin)
