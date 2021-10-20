from __future__ import annotations
import logging
from hikari.api.voice import VoiceConnection
from hikari.snowflakes import Snowflake
from lightbulb import Context
import hikari
import lightbulb

al_shyke = {
    "1": "https://youtu.be/wwMyn8a_puQ",  # ماهر المعيقلي
    "2": "https://youtu.be/fLkdQeeRtYs",  # ياسر الدوسري
    "3": "https://youtu.be/IrwPiwHWhXo",  # عبدالرحمن السديس
    "4": "https://youtu.be/V9UIIsai5E8",  # عبدالباسط عبدالصمد
    "5": "https://youtu.be/sPHuARcC6kE",  # اسلام صبحي
    "6": "https://youtu.be/MGEWrAtHFwU"   # مشاري بن راشد العفاسي
}


class EventHandler:
    """Events from the Lavalink server"""

    async def track_start(self, _lava_client, event):
        pass

    async def track_finish(self, _lava_client, event):
        pass

    async def track_exception(self, lavalink, event):
        logging.warning("Track exception event happened on guild: %d", event.guild_id)


async def join_voice_channel(ctx: Context) -> Snowflake | hikari.Embed | int:
    states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.get_guild())
    voice_state = list(
        filter(lambda i: i.user_id == ctx.author.id, states.iterator())
    )
    embed = hikari.Embed(color=0xffd430)
    if not voice_state:
        embed.description = "يجب عليك دخول غرفه صوتيه"
        return embed
    
    channel_id = voice_state[0].channel_id
    
    await ctx.bot.voice.connect_to(
        guild=ctx.get_guild(),
        channel=channel_id,
        voice_connection_type=VoiceConnection,
        deaf=True
    )
    return channel_id 

async def stop(ctx: Context):
    states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.get_guild())
    voice_state = list(
        filter(lambda i: i.user_id == ctx.bot.get_me().id, states.iterator())
    )

    if not voice_state:
        return
    await ctx.bot.lavalink.destroy(ctx.guild_id)
    await ctx.bot.lavalink.leave(ctx.guild_id)
    await ctx.bot.lavalink.remove_guild_node(ctx.guild_id)
    await ctx.bot.lavalink.remove_guild_from_loops(ctx.guild_id)
    return voice_state[0].channel_id

