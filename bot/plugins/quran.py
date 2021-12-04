import hikari
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import MessageFlag
from lightbulb import Plugin, commands 
import lightbulb
from lightbulb.checks import has_guild_permissions
from lightbulb.context import SlashContext
from bot.utils import voice, command_error
from bot.database import GuildUpdateType


quran_plugin = Plugin("quran")


def check_permission(context: SlashContext, permission: hikari.Permissions, /):
    perms = [
        role.permissions.any(permission) for role in context.member.get_roles() if role.permissions.any(permission, hikari.Permissions.ADMINISTRATOR)]
    if len(perms) > 0 or context.get_guild().owner_id == context.author.id:
        return True
    return False

async def only_role(ctx: SlashContext):
    _guild = ctx.get_guild()
    guild = ctx.bot.db.fetch_guild(_guild.id)
    role = _guild.get_role(guild.role_id) if guild.role_id else None
    if not role or guild.role_id in [i.id for i in ctx.member.get_roles()] or check_permission(ctx, hikari.Permissions.MANAGE_GUILD):
        return True
    await command_error(ctx, "أنت لا تمتلك صلاحيات للتحكم بهاذ الأمر")
    return False

@quran_plugin.command()
@lightbulb.command("quran", "quran group commands")
@lightbulb.implements(commands.SlashCommandGroup)
async def quran(ctx: SlashContext):
    ...

quran_options = {
    "ماهر المعيقلي": "1",
    "ياسر الدوسري": "2",
    "عبدالرحمن السديس": "2",
    "عبدالباسط عبدالصمد": "4",
    "اسلام صبحي": "5",
    "مشاري بن راشد العفاسي": "6",
    "حسن صالح": "7"
}

reciter = {
    "1": "https://youtu.be/wwMyn8a_puQ",  # ماهر المعيقلي
    "2": "https://youtu.be/fLkdQeeRtYs",  # ياسر الدوسري
    "3": "https://youtu.be/IrwPiwHWhXo",  # عبدالرحمن السديس
    "4": "https://youtu.be/V9UIIsai5E8",  # عبدالباسط عبدالصمد
    "5": "https://youtu.be/sPHuARcC6kE",  # اسلام صبحي
    "6": "https://youtu.be/MGEWrAtHFwU",  # مشاري بن راشد العفاسي
    "7": "https://youtu.be/-55QeK_VbnQ",  # حسن صالح
}

@quran.child()
@lightbulb.option(
    name="quran_reader",
    description="أختر القارئ المناسب", 
    required=True, 
    choices=list(quran_options.keys()),
)
@lightbulb.command("play", "تشغيل القران الكريم")
@lightbulb.implements(commands.SlashSubCommand)
async def quran_play(ctx: SlashContext):
    check = await only_role(ctx)
    if check == False:
        return
    value = ctx.raw_options.get("القارئ")
    choice = reciter.get(quran_options.get(value))
    embed = hikari.Embed(color=0xffd430)
    channel = await voice.join_voice_channel(ctx)
    if isinstance(channel, hikari.Embed):
        await ctx.interaction.create_initial_response(ResponseType.MESSAGE_CREATE, flags=MessageFlag.EPHEMERAL, embed=channel)
        return
    await ctx.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_CREATE)
    information = await ctx.bot.lavalink.auto_search_tracks(choice)
    await ctx.bot.lavalink.play(ctx.guild_id, information.tracks[0]).requester(ctx.author.id).queue()
    embed.description = "تم تشغيل القرآن الكريم بصوت الشيخ: **%s**" % value
    await ctx.interaction.edit_initial_response(embed=embed)


@quran.child()
@lightbulb.command("radio", "تشغيل اذاعه القران الكريم")
@lightbulb.implements(commands.SlashSubCommand)
async def quran_radio(ctx: SlashContext):
    check = await only_role(ctx)
    if check == False:
        return
    channel_id = await voice.join_voice_channel(ctx)
    if isinstance(channel_id, hikari.Embed):
        await ctx.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, flags=MessageFlag.EPHEMERAL, embed=channel_id)
        return
    await ctx.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    embed = hikari.Embed(color=0xffd430)
    information = await ctx.bot.lavalink.get_tracks("https://qurango.net/radio/tarateel")
    await ctx.bot.lavalink.play(ctx.guild_id, information.tracks[0]).requester(ctx.author.id).queue()
    embed.description = "تم تشغيل أذاعة القران الكريم في روم <#%s>" % channel_id
    await ctx.interaction.edit_initial_response(embed=embed)


@quran.child()
@lightbulb.command("stop", "إيقاف تشغيل القران الكريم")
@lightbulb.implements(commands.SlashSubCommand)
async def quran_stop(ctx: SlashContext):
    check = await only_role(ctx)
    if check == False:
        return
    data = await voice.leave_and_stop(ctx)
    embed = hikari.Embed(color=0xffd430)
    if not data:
        return await command_error(ctx, "البوت غير موجود في روم صوتي")
    await ctx.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    embed.description = "تم مغادره الروم الصوتي"
    await ctx.interaction.edit_initial_response(embed=embed)

@quran.child()
@lightbulb.option(
    name="المتسوى", 
    description="المستوى الجديد للصوت",
    type=int,
    required=True,
)
@lightbulb.command("volume", "تغير مستوى الصوت للقرآن الكريم")
@lightbulb.implements(commands.SlashSubCommand)
async def quran_volume(ctx: SlashContext):
    check = await only_role(ctx)
    if check == False:
        return
    vol = ctx.raw_options.get("المتسوى")
    embed = hikari.Embed(color=0xffd430)
    if vol > 100 or vol < 0:
        return await command_error(ctx, "الصوت المتاح من 0 - 100")
    await ctx.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    ctx.bot.lavalink.volume(ctx.guild_id, vol)
    embed.description = f"تم تغير مستوى الصوت إلى `{vol}%`"
    await ctx.interaction.edit_initial_response(embed=embed)


def load(bot):
    bot.add_plugin(quran_plugin)


def unload(bot):
    bot.remove_plugin(quran_plugin)
