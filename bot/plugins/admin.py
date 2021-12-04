import hikari
import lightbulb
from lightbulb import Plugin, commands
from lightbulb.context.slash import SlashContext
from bot.database import GuildUpdateType
from bot.utils import command_error
from hikari import ButtonStyle, Permissions
import asyncio


admin_plugin = Plugin("admin")

@admin_plugin.command()
@lightbulb.command("set", "set command group")
@lightbulb.implements(commands.SlashCommandGroup)
async def _set(ctx: SlashContext):
    ...

@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="new_prefix", 
    description="البادئة الجديدة",
    required=True
)
@lightbulb.command("prefix", "تغير البادئة الخاصة بالخادم")
@lightbulb.implements(commands.SlashSubCommand)
async def prefix(ctx: SlashContext):
    new_prefix = ctx.raw_options.get("new_prefix")
    embed = hikari.Embed(color=0xffd430)
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    error = await ctx.bot.emojis.error
    if len(new_prefix) > 5:
        return await command_error(ctx, "%s لا يمكنك وضع بادئه اكثر من خمس حروف" % error)
    await ctx.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    ctx.bot.db.update_guild(guild, GuildUpdateType.prefix, new_prefix)
    embed.description = "تم تغير البادئه الى `%s`" % new_prefix
    await ctx.interaction.edit_initial_response(embed=embed)

@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="mode",
    description="تحديد الوضع",
    type=bool,
    required=True
)
@lightbulb.command("spam", "خاصية تمنع تكرر ارسال الاذكار في حالة عدم تفاعل الشات")
@lightbulb.implements(commands.SlashSubCommand)
async def set_spam(ctx: SlashContext):
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    mode = ctx.raw_options.get("mode")
    msg = "تم تفعيل خاصية تكرار الرسائل" if mode else "تم اطفاء خاصية تكرار الرسائل"
    await ctx.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    ctx.bot.db.update_guild(guild, GuildUpdateType.anti_spam, mode)
    embed = hikari.Embed(
        description=msg,
        color=0xffd430
    )
    await ctx.interaction.edit_initial_response(embed=embed)


@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="mode",
    description="تحديد الوضع",
    type=bool
)
@lightbulb.command("embed", "تغير خاصيه ارسال الاذكار الى امبد")
@lightbulb.implements(commands.SlashSubCommand)
async def set_embed(ctx: SlashContext):
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    mode = ctx.raw_options.get("mode")
    msg = "تم تفعيل خاصية الأمبد" if mode else "تم اطفاء خاصية الأمبد"
    await ctx.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    ctx.bot.db.update_guild(guild, GuildUpdateType.embed, mode)
    embed = hikari.Embed(
        description=msg,
        color=0xffd430
    )
    await ctx.interaction.edit_initial_response(embed=embed)

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
@lightbulb.implements(commands.SlashSubCommand)
async def set_time(ctx: SlashContext):
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    embed = hikari.Embed(color=0xffd430)
    if not guild.channel_id:
        return await command_error(ctx, "يجب عليك تثبيت روم لاستعمال هاذ الامر")
    value = ctx.raw_options.get("time")
    ctx.bot.db.update_guild(
        guild, GuildUpdateType.time, times.get(value))
    embed.description = "تم تغير وقت ارسال الأذكار إلى: **%s**" % value
    await ctx.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed=embed)


@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="channel",
    description="أختر القناة المناسبة",
    type=hikari.TextableChannel,
    required=False,
)
@lightbulb.command("room", "أختيار قناة الأذكار")
@lightbulb.implements(commands.SlashSubCommand)
async def set_room(ctx: SlashContext):
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)
    channel_id = ctx.raw_options.get("channel")

    if not channel_id:
        guild = ctx.bot.db.fetch_guild(ctx.guild_id)
        embed = hikari.Embed(color=0xffd430)
        channel = guild.channel_id
        if not channel:
            return await command_error(ctx, "انت لم تقم بتثبيت الروم من قبل")
        await ctx.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        yes = await ctx.bot.emojis.yes
        no = await ctx.bot.emojis.no
        embed.description = "هل انت موافق على ايقاف ارسال الاذكار في روم <#%s>" % channel
        buttons = ctx.bot.rest.build_action_row()

        true = buttons.add_button(ButtonStyle.SUCCESS, "true")
        true.set_label("موافق")
        true.set_emoji(yes)
        true.add_to_container()

        false = buttons.add_button(ButtonStyle.DANGER, "false")
        false.set_label("غير موافق")
        false.set_emoji(no)
        false.add_to_container()

        await ctx.interaction.edit_initial_response(embed=embed, component=buttons)

        def check(res):
            return res.interaction.user.id == ctx.author.id and \
                res.interaction.channel_id == ctx.channel_id and \
                res.interaction.custom_id in ["true", "false"]

        true.set_is_disabled(True)
        false.set_is_disabled(True)
        try:
            event = await ctx.bot.wait_for(hikari.InteractionCreateEvent, predicate=check, timeout=15)
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE)
        except asyncio.TimeoutError:
            embed.description = "تم الغاء الأمر بسبب نفاذ الوقت"
            await ctx.interaction.edit_initial_response(embed=embed, component=buttons)
            return
        if event.interaction.custom_id == "true":
            ctx.bot.db.update_guild(guild, GuildUpdateType.channel, None)
            embed.description = "تم الغاء ارسال الاذكار بنجاح"
            await ctx.interaction.edit_initial_response(embed=embed, component=buttons)
            return
        embed.description = "تم الغاء الأمر"
        await ctx.interaction.edit_initial_response(embed=embed, component=buttons)
        return

    channel = ctx.bot.cache.get_guild_channel(channel_id)
    embed = hikari.Embed(color=0xffd430)

    if channel.type != hikari.ChannelType.GUILD_TEXT:
        return await command_error(ctx, "يجب التأكد من نوع القناة المحدده من انها كتابية")
    if int(channel_id) == guild.channel_id:
        return await command_error(ctx, "لقد قمت بتحديد هذا الروم مسبقًا")
    await ctx.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    ctx.bot.db.update_guild(guild, GuildUpdateType.channel, channel.id)
    embed.description = "! الله يكتب اجرك راح ارسل الاذكار للروم %s" % channel.mention
    await ctx.interaction.edit_initial_response(embed=embed)

@_set.child()
@lightbulb.add_checks(lightbulb.has_guild_permissions(Permissions.MANAGE_GUILD))
@lightbulb.option(
    name="role",
    description="أختر الرتبة",
    type=hikari.Role,
    required=False
)
@lightbulb.command("role", "تقيد صلاحيات التحكم بالقرآن الكريم")
@lightbulb.implements(commands.SlashSubCommand)
async def set_role(ctx: SlashContext):
    role = ctx.raw_options.get("role")
    guild = ctx.bot.db.fetch_guild(ctx.guild_id)

    if not role:
        ctx.bot.db.update_guild(guild, GuildUpdateType.role_id, None)
        embed = hikari.Embed(
            description="لقد تم الغاء تقيد صلاحيات التحكم بالقرآن الكريم من رتبة <@&{}>".format(
                guild.role_id),
            color=0xffd430
        )
        await ctx.respond(embed=embed)
        return

    ctx.bot.db.update_guild(guild, GuildUpdateType.role_id, role.id)
    embed = hikari.Embed(
        description="لقد تم تعين رتبة <@&{}> للتحكم بالقرآن الكريم".format(role.id),
        color=0xffd430
    )
    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(admin_plugin)


def unload(bot):
    bot.remove_plugin(admin_plugin)
