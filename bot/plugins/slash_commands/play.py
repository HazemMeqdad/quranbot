import hikari
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import MessageFlag
from lightbulb.slash_commands.context import SlashCommandContext
from lightbulb.slash_commands import SlashCommand
from lightbulb.slash_commands import Option
from bot import Bot
from bot.utils import join_voice_channel, stop, al_shyke

choics = {
    "ماهر المعيقلي": "1",
    "ياسر الدوسري": "2",
    "عبدالرحمن السديس": "2",
    "عبدالباسط عبدالصمد": "4",
    "اسلام صبحي": "5",
    "مشاري بن راشد العفاسي": "6",
}


GUILD_ID = 843865725886398554

class Play(SlashCommand):
    name = "play"
    description = "تشغيل القران الكريم"
    enable_guilds = (GUILD_ID,)

    choice: str = Option("اختر القارئ المناسب", name="القارئ", required=True, choices=list(choics.keys()))

    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        value = context.option_values._options.get("القارئ").value
        _value = al_shyke.get(choics.get(value))
        embed = hikari.Embed(color=0xffd430)
        await join_voice_channel(context)
        
        information = await self.bot.lavalink.auto_search_tracks(_value)
        await self.bot.lavalink.play(context.guild_id, information.tracks[0]).requester(context.author.id).queue()
        embed.description = "تم تشغيل القرآن الكريم بصوت الشيخ: **%s**" % value
        await context.interaction.edit_initial_response(embed=embed)

class Live(SlashCommand):
    name = "live"
    description = "تشغيل اذاعه القران الكريم"
    enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        channel_id = await join_voice_channel(context, slash=True)
        if channel_id == 0:
            return
        embed = hikari.Embed(color=0xffd430)
        information = await self.bot.lavalink.get_tracks("https://qurango.net/radio/tarateel")
        await self.bot.lavalink.play(context.guild_id, information.tracks[0]).requester(context.author.id).queue()
        embed.description = "تم تشغيل أذاعة القران الكريم في روم <#%s>" % channel_id
        await context.interaction.edit_initial_response(embed=embed)

class Stop(SlashCommand):
    name = "stop"
    description = "ايقاف تشغيل القران الكريم"
    enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        data = await stop(context)
        embed = hikari.Embed(color=0xffd430)
        if not data:
            embed.description = "البوت ليس موجود في روم صوتي"
            await context.interaction.edit_initial_response(embed=embed)
            return
        embed.description = "تم مغادره الروم الصوتي"
        await context.interaction.edit_initial_response(embed=embed)

class Join(SlashCommand):
    name = "join"
    description = "انظمام البوت الى روم صوتي"
    enable_guilds = (GUILD_ID,)

    async def callback(self, context: SlashCommandContext):
        channel_id = await join_voice_channel(context)
        embed = hikari.Embed(color=0xffd430)
        if isinstance(channel_id, int):
            embed.description = "تم انظمام البوت الى <#%s>" % channel_id
            await context.interaction.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed=embed)
        await context.interaction.create_initial_response(ResponseType.MESSAGE_CREATE, embed=channel_id, flags=MessageFlag.EPHEMERAL)


class Volume(SlashCommand):
    name = "volume"
    description = "تغير مستوى الصوت للقران الكريم"
    enable_guilds = (GUILD_ID,)
    
    volume: int = Option("المستوى الجديد للصوت", name="المتسوى")
    async def callback(self, context: SlashCommandContext):
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        vol = context.option_values._options.get("المتسوى").value
        embed = hikari.Embed(color=0xffd430)
        if vol > 100 or vol < 0:
            embed.description = "الصوت المتاح من 0 - 100"
            await context.interaction.edit_initial_response(embed=embed)
            return
        self.bot.lavalink.volume(context.guild_id, vol)
        embed.description = f"تم تغير مستوى الصوت إلى `{vol}%`"
        await context.interaction.edit_initial_response(embed=embed)

def load(bot: Bot):
    bot.add_slash_command(Play)
    bot.add_slash_command(Live)
    bot.add_slash_command(Stop)
    bot.add_slash_command(Join)
    bot.add_slash_command(Volume)


def unload(bot: Bot):
    bot.remove_slash_command("play")
    bot.remove_slash_command("live")
    bot.remove_slash_command("stop")
    bot.remove_slash_command("join")
    bot.remove_slash_command("volume")
