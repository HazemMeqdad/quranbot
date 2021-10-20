import hikari
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import MessageFlag
from lightbulb.slash_commands.context import SlashCommandContext
from lightbulb.slash_commands import SlashCommand
from lightbulb.slash_commands import Option
from bot import Bot
from bot.utils import join_voice_channel, stop, al_shyke
from lightbulb.errors import CommandError

choics = {
    "ماهر المعيقلي": "1",
    "ياسر الدوسري": "2",
    "عبدالرحمن السديس": "2",
    "عبدالباسط عبدالصمد": "4",
    "اسلام صبحي": "5",
    "مشاري بن راشد العفاسي": "6",
}


GUILD_ID = 872200812129054730


class Play(SlashCommand):
    name = "play"
    description = "تشغيل القران الكريم"
    # enable_guilds = (GUILD_ID,)

    choice: str = Option("اختر القارئ المناسب", name="القارئ",
                         required=True, choices=list(choics.keys()))

    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        value = context.option_values._options.get("القارئ").value
        _value = al_shyke.get(choics.get(value))
        embed = hikari.Embed(color=0xffd430)
        channel = await join_voice_channel(context)
        if isinstance(channel, hikari.Embed):
            await context.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, flags=MessageFlag.EPHEMERAL, embed=channel)
            return
        information = await self.bot.lavalink.auto_search_tracks(_value)
        await self.bot.lavalink.play(context.guild_id, information.tracks[0]).requester(context.author.id).queue()
        embed.description = "تم تشغيل القرآن الكريم بصوت الشيخ: **%s**" % value
        await context.interaction.edit_initial_response(embed=embed)


class Live(SlashCommand):
    name = "live"
    description = "تشغيل اذاعه القران الكريم"
    # enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        channel_id = await join_voice_channel(context)
        if isinstance(channel_id, hikari.Embed):
            await context.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, flags=MessageFlag.EPHEMERAL, embed=channel_id)
            return
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        embed = hikari.Embed(color=0xffd430)
        information = await self.bot.lavalink.get_tracks("https://qurango.net/radio/tarateel")
        await self.bot.lavalink.play(context.guild_id, information.tracks[0]).requester(context.author.id).queue()
        embed.description = "تم تشغيل أذاعة القران الكريم في روم <#%s>" % channel_id
        await context.interaction.edit_initial_response(embed=embed)


class Stop(SlashCommand):
    name = "stop"
    description = "ايقاف تشغيل القران الكريم"
    # enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        data = await stop(context)
        embed = hikari.Embed(color=0xffd430)
        if not data:
            raise CommandError("البوت غير موجود في روم صوتي")
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        embed.description = "تم مغادره الروم الصوتي"
        await context.interaction.edit_initial_response(embed=embed)


class Join(SlashCommand):
    name = "join"
    description = "انظمام البوت الى روم صوتي"
    # enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        channel_id = await join_voice_channel(context)
        embed = hikari.Embed(color=0xffd430)
        if isinstance(channel_id, hikari.Embed):
            await context.interaction.create_initial_response(ResponseType.MESSAGE_CREATE, embed=channel_id, flags=MessageFlag.EPHEMERAL)
        embed.description = "تم انظمام البوت الى <#%s>" % channel_id
        await context.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed=embed)


class Volume(SlashCommand):
    name = "volume"
    description = "تغير مستوى الصوت للقران الكريم"
    # enable_guilds = (GUILD_ID,)

    volume: int = Option("المستوى الجديد للصوت", name="المتسوى")

    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        vol = context.option_values._options.get("المتسوى").value
        embed = hikari.Embed(color=0xffd430)
        if vol > 100 or vol < 0:
            raise CommandError("الصوت المتاح من 0 - 100")
        self.bot.lavalink.volume(context.guild_id, vol)
        embed.description = f"تم تغير مستوى الصوت إلى `{vol}%`"
        await context.interaction.edit_initial_response(embed=embed)


def load(bot: Bot):
    bot.add_slash_command(Play, True)
    bot.add_slash_command(Live, True)
    bot.add_slash_command(Stop, True)
    bot.add_slash_command(Join, True)
    bot.add_slash_command(Volume, True)


def unload(bot: Bot):
    bot.remove_slash_command("play")
    bot.remove_slash_command("live")
    bot.remove_slash_command("stop")
    bot.remove_slash_command("join")
    bot.remove_slash_command("volume")
