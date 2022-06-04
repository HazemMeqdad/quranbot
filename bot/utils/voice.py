from hikari.snowflakes import Snowflake
import lightbulb
import hikari
import typing as t
import lavaplayer


async def get_voice_data(bot: lightbulb.BotApp, guild: hikari.SnowflakeishOr[hikari.Guild]) -> t.Optional[Snowflake]:
    states = bot.cache.get_voice_states_view_for_guild(guild)
    voice_state = list(
        filter(lambda i: i.user_id == bot.get_me().id, states.iterator())
    )
    if not voice_state:
        return None
    
    return voice_state[0].channel_id


async def join_voice_channel(bot: lightbulb.BotApp, guild: hikari.SnowflakeishOr[hikari.Guild], auther: t.Union[hikari.Member, hikari.User]) -> t.Optional[Snowflake]:
    states = bot.cache.get_voice_states_view_for_guild(guild)
    voice_state = list(
        filter(lambda i: i.user_id == auther.id, states.iterator())
    )
    if not voice_state:
        return None
    
    channel_id = voice_state[0].channel_id
    await bot.update_voice_state(guild, channel_id, self_deaf=True)
    await bot.lavalink.wait_for_connection(guild)
    return channel_id 

async def leave_and_stop(bot: lightbulb.BotApp, guild: hikari.SnowflakeishOr[hikari.Guild]):
    states = bot.cache.get_voice_states_view_for_guild(guild)
    voice_state = list(
        filter(lambda i: i.user_id == bot.get_me().id, states.iterator())
    )

    if not voice_state:
        return
    await bot.update_voice_state(guild, None)
    await bot.lavalink.wait_for_remove_connection(guild)
    return voice_state[0].channel_id

async def play_lavalink_source(
    lavalink: lavaplayer.LavalinkClient, 
    guild: hikari.SnowflakeishOr[hikari.Guild], 
    source: str, 
    user: hikari.SnowflakeishOr[hikari.User]
    ) -> t.Optional[lavaplayer.LavalinkClient]:
    guild_id = guild.id if isinstance(guild, hikari.Guild) else guild
    
    queue = await lavalink.queue(guild_id)

    if queue:
        return

    tracks = await lavalink.get_tracks(source)
    await lavalink.play(guild_id, tracks[0], user.id)
    return tracks[0]