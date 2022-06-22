import hikari
from hikari.commands import CommandChoice
from hikari.messages import MessageFlag
from lightbulb import Plugin, commands 
import lightbulb
from lightbulb.context import SlashContext
import json
from bot.utils import voice


quran_plugin = Plugin("القرآن الكريم")

# JSON Files quran_surahs
quran_reader = json.load(open("bot/json/quran_reader.json", "r", encoding="utf-8"))
surah_optins = json.load(open("bot/json/surah_optins.json", "r", encoding="utf-8"))
quran_stream_readers = json.load(open("bot/json/quran_stream_readers.json", "r", encoding="utf-8"))
quran_surahs = json.load(open("bot/json/quran_surahs.json", "r", encoding="utf-8"))


def check_permission(context: SlashContext, permission: hikari.Permissions, /):
    perms = [
        role.permissions.any(permission) for role in context.member.get_roles() if role.permissions.any(permission, hikari.Permissions.ADMINISTRATOR)]
    if len(perms) > 0 or context.get_guild().owner_id == context.author.id:
        return True
    return False

@lightbulb.Check
async def only_role(ctx: SlashContext):
    _guild = ctx.get_guild()
    guild = ctx.bot.db.fetch_guild(_guild.id)
    role = _guild.get_role(guild.role_id) if guild.role_id else None
    if not role or guild.role_id in [i.id for i in ctx.member.get_roles()] or check_permission(ctx, hikari.Permissions.MANAGE_GUILD):
        return True
    embed = hikari.Embed(color=0xffd430, description="ليس لديك صلاحية لاستخدام هذا الأمر")
    await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
    return False

@quran_plugin.command()
@lightbulb.command("quran", "quran group commands")
@lightbulb.implements(commands.SlashCommandGroup, commands.PrefixSubGroup)
async def quran(ctx: SlashContext):
    ...


@quran.child()
@lightbulb.add_checks(only_role)
@lightbulb.option(
    name="quran_reader",
    description="أختر القارئ المناسب", 
    required=True, 
    choices=[CommandChoice(name=i["name"], value=i["value"]) for i in quran_reader],
)
@lightbulb.option(
    name="surah",
    description="السورة المطلوبة يمكن كتابة رقم أو أسم السورة",
    required=False,
    autocomplete=True
)
@lightbulb.command("play", "تشغيل القران الكريم")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def quran_play(ctx: SlashContext):
    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    stream_url = ctx.options.quran_reader

    name = [i["name"] for i in quran_reader if i["value"] == stream_url][0]

    surah_number = ctx.options.surah
    surah_number = str(surah_number) if surah_number else None

    channel = await voice.join_voice_channel(bot=ctx.bot, guild=ctx.guild_id, auther=ctx.author)

    if not channel:
        embed.description = "يجب عليك دخول قناة صوتية"
        await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)
        return

    if surah_number and not surah_number.isdigit():
        embed.description = "السورة المطلوبة غير موجودة"
        await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)
        return

    if surah_number:
        if name == "حسن صالح" or name == "اسلام صبحي":
            embed.description = "للأسف هاذ القارئ غير متاح في الوقت الحالي"
            await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)
            return
        
        if int(surah_number) > 114 or int(surah_number) < 1:
            embed.description = "خطأ في أدخال رقم السورة يرجى العلم بان عدد سور القرآن الكريم 114 سورة"
            await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)
            return

        surah = quran_surahs.get(str(surah_number))
        stream_url = [i["value"] for i in surah_optins if i["name"] == name][0]

        stream_url = stream_url+surah_number if len(surah_number) == 3 \
                                            else stream_url+"0"+surah_number \
                                            if len(surah_number) == 2 \
                                            else stream_url+"00"+surah_number

        await voice.play_lavalink_source(ctx.bot.lavalink, ctx.guild_id, stream_url+".mp3", ctx.author)
        embed.description = "تم تشغيل سوره %s بصوت الشيخ: **%s**" % (surah, name)
        await ctx.respond(embed=embed)
        return

    tracks = await ctx.bot.lavalink.get_tracks(stream_url)
    await ctx.bot.lavalink.play(ctx.guild_id, tracks[0], ctx.author.id)
    embed.description = "تم تشغيل القرآن الكريم بصوت الشيخ: **%s**" % name
    await ctx.respond(embed=embed)


@quran_play.autocomplete("surah")
async def quran_autocomplete(ctx: SlashContext, query: hikari.AutocompleteInteraction):
    try:
        option = query.options[0].options[1].value
    except IndexError:
        return []
    if not option:
        return [CommandChoice(name=i[1], value=str(i[0])) for i in quran_surahs.items()][:25]
    return [CommandChoice(name=i[1], value=str(i[0])) for i in quran_surahs.items() if option in i[1]][:25]

@quran.child()
@lightbulb.add_checks(only_role)
@lightbulb.option(
    name="quran_reader",
    description="أختر القارء المناسب",
    required=False,
    choices=[CommandChoice(name=i["name"], value=i["value"]) for i in quran_stream_readers]
)
@lightbulb.command("radio", "تشغيل اذاعه القران الكريم")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def quran_radio(ctx: SlashContext):
    
    await ctx.respond(response_type=hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    
    channel = await voice.join_voice_channel(bot=ctx.bot, guild=ctx.guild_id, auther=ctx.author)

    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)

    if not channel:
        embed.description = "يجب عليك دخول قناة صوتية"
        await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)
        return
    stream_url = ctx.options.quran_reader
    if stream_url:
        name = [i["name"] for i in quran_stream_readers if i["value"] == stream_url][0]
        await voice.play_lavalink_source(ctx.bot.lavalink, ctx.guild_id, stream_url, ctx.author)
        embed.description = "تم تشغيل أذاعة القران الكريم الخاص بالقارئ %s في روم <#%s>" % (
            name, channel)
        await ctx.respond(embed=embed)
        return

    await voice.play_lavalink_source(ctx.bot.lavalink, ctx.guild_id, "https://qurango.net/radio/tarateel", ctx.author)
    embed.description = "تم تشغيل أذاعة القران الكريم المتنوعه في روم <#%s>" % channel
    await ctx.respond(embed=embed)


@quran.child()
@lightbulb.add_checks(only_role)
@lightbulb.command("stop", "إيقاف تشغيل القران الكريم")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def quran_stop(ctx: SlashContext):
    data = await voice.leave_and_stop(ctx.bot, ctx.guild_id)
    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    if not data:
        embed.description = "البوت غير موجود في روم صوتي"
        await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)
        return
    embed.description = "تم مغادره الروم الصوتي"
    await ctx.respond(embed=embed)

@quran.child()
@lightbulb.add_checks(only_role)
@lightbulb.option(
    name="المتسوى", 
    description="المستوى الجديد للصوت",
    type=int,
    required=True,
)
@lightbulb.command("volume", "تغير مستوى الصوت للقرآن الكريم")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def quran_volume(ctx: SlashContext):
    vol = ctx.raw_options.get("المتسوى")
    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    # check if bot is in voice channel
    data = await voice.get_voice_data(ctx.bot, ctx.guild_id)
    if not data:
        embed.description = "البوت غير موجود في روم صوتي"
        await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)
        return
    if vol > 100 or vol < 0:
        embed.description = "المستوى يجب أن يكون بين 0 - 100"
        await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
        return
    await ctx.bot.lavalink.volume(ctx.guild_id, vol)
    embed.description = f"تم تغير مستوى الصوت إلى `{vol}%`"
    await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(quran_plugin)


def unload(bot):
    bot.remove_plugin(quran_plugin)
