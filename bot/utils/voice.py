import logging
from hikari.api.voice import VoiceConnection
from hikari.snowflakes import Snowflake
from lightbulb.context import Context
import hikari
import typing as t


async def join_voice_channel(ctx: Context) -> t.Union[Snowflake, hikari.Embed]:
    states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.get_guild())
    voice_state = list(
        filter(lambda i: i.user_id == ctx.author.id, states.iterator())
    )
    embed = hikari.Embed(color=0xffd430)
    if not voice_state:
        embed.description = "يجب عليك دخول غرفه صوتيه"
        return embed
    
    channel_id = voice_state[0].channel_id
    await ctx.bot.update_voice_state(ctx.get_guild(), channel_id, self_deaf=True)
    await ctx.bot.lavalink.wait_for_connection(ctx.guild_id)
    return channel_id 

async def leave_and_stop(ctx: Context):
    states = ctx.bot.cache.get_voice_states_view_for_guild(ctx.get_guild())
    voice_state = list(
        filter(lambda i: i.user_id == ctx.bot.get_me().id, states.iterator())
    )

    if not voice_state:
        return
    await ctx.bot.update_voice_state(ctx.guild_id, None)
    await ctx.bot.lavalink.wait_for_remove_connection(ctx.guild_id)
    return voice_state[0].channel_id

