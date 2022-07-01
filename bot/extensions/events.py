import logging
import threading
import time
import hikari
import lightbulb
import json
import lavaplayer
from bot.utils import voice

events = lightbulb.Plugin(__name__)

@events.listener(hikari.GuildJoinEvent)
async def on_guild_join(event: hikari.GuildJoinEvent):
    bot = events.bot
    bot.db.insert(event.get_guild().id)
    if not bot.config.get("webhooks") or not bot.config["webhooks"].get("logger"):
        return
    owner_id = event.get_guild().owner_id
    owner = await bot.rest.fetch_user(owner_id)
    
    embed = hikari.Embed(
        title="أضافة جديده",
        color=0x46FF00
    )
    embed.add_field("اسم الخادم:", f"{event.get_guild().name} (`{event.get_guild().id}`)")
    embed.add_field("عدد أعضاء الخادم:", str(event.get_guild().member_count))
    embed.add_field("مالك الخادم:", f"{owner.username}#{owner.discriminator} (`{owner.id}`)")
    embed.add_field("خوادم فاذكروني", str(len(bot.cache.get_guilds_view())))
    embed.set_footer(text=event.get_guild().name, icon=event.get_guild().icon_url)
    embed.set_author(name=bot.get_me().username, icon=bot.get_me().avatar_url)
    await bot.rest.execute_webhook(
        bot.config["webhooks"]["logger"]["id"], 
        bot.config["webhooks"]["logger"]["token"],
        embed=embed
    )

@events.listener(hikari.GuildLeaveEvent)
async def on_guild_leave(event: hikari.GuildLeaveEvent):
    bot = events.bot
    bot.db.delete_guild(event.guild_id)
    if not bot.config.get("webhooks") or not bot.config["webhooks"].get("logger"):
        return
    guild = event.old_guild
    if guild:
        owner_id = guild.owner_id
        owner = await bot.rest.fetch_user(owner_id)
        embed = hikari.Embed(
            title="أضافة جديده",
            color=0xFF0000
        )
        embed.add_field("اسم الخادم:", f"{guild.name} (`{guild.id}`)")
        embed.add_field("عدد أعضاء الخادم:", str(guild.member_count))
        embed.add_field("مالك الخادم:", f"{owner.username}#{owner.discriminator} (`{owner.id}`)")
        embed.add_field("خوادم فاذكروني", str(len(bot.cache.get_guilds_view())))
        embed.set_footer(text=guild.name, icon=guild.icon_url)
        embed.set_author(name=bot.get_me().username, icon=bot.get_me().avatar_url)
        await bot.rest.execute_webhook(
            bot.config["webhooks"]["logger"]["id"], 
            bot.config["webhooks"]["logger"]["token"],
            embed=embed
        )

@events.listener(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent) -> None:
    bot = events.bot
    if bot.lavalink and bot.lavalink.is_connect:
        await bot.lavalink.raw_voice_state_update(
            event.state.guild_id,
            event.state.user_id,
            event.state.session_id,
            event.state.channel_id,
        )

@events.listener(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent) -> None:
    bot = events.bot
    if bot.lavalink and bot.lavalink.is_connect:
        if not event.endpoint:
            return
        await bot.lavalink.raw_voice_server_update(
            event.guild_id, event.endpoint, event.token
        )


############################ Lavalink ############################

async def on_player_update(event: lavaplayer.PlayerUpdateEvent) -> None:
    ...


async def track_start_event(event: lavaplayer.TrackStartEvent) -> None:
    ...

async def track_end_event(event: lavaplayer.TrackEndEvent) -> None:
    lavalink: lavaplayer.LavalinkClient = events.bot.lavalink
    node = await lavalink.get_guild_node(event.guild_id)
    if node and not node.queue:
        await voice.leave_and_stop(events.bot, event.guild_id)

############################ Redis ############################

# Redis cache events
async def update_redis_cache(guild: hikari.Guild):
    bot = events.bot
    data = {
        "id": guild.id.__str__(),
        "name": guild.name,
        "icon_url": guild.icon_url.url if guild.icon_url else None,
        "member_count": guild.member_count.__str__(),
        "description": guild.description,
        "owner_id": guild.owner_id.__str__(),
        "channels": [{"id": str(channel.id), "name": channel.name, "type": channel.type.value} for channel in guild.get_channels().values()],
        "roles": [{"id": role.id.__str__(), "name": role.name} for role in guild.get_roles().values()],
    }
    await bot.redis.set(f"guild:{guild.id}", json.dumps(data))

@events.listener(hikari.GuildAvailableEvent)
async def guild_available(event: hikari.GuildAvailableEvent) -> None:
    await update_redis_cache(event.guild)

@events.listener(hikari.GuildUnavailableEvent)
async def guild_unavailable(event: hikari.GuildUnavailableEvent) -> None:
    bot = events.bot
    await bot.redis.delete(f"guild:{event.guild_id}")

@events.listener(hikari.GuildUpdateEvent)
async def on_guild_update(event: hikari.GuildUpdateEvent) -> None:
    await update_redis_cache(event.guild)

@events.listener(hikari.GuildChannelEvent)
async def on_channel_update(event: hikari.GuildChannelEvent) -> None:
    await update_redis_cache(event.get_guild())

@events.listener(hikari.RoleUpdateEvent)
async def on_role_update(event: hikari.RoleUpdateEvent) -> None:
    bot = events.bot
    await update_redis_cache(bot.cache.get_available_guild(event.guild_id))

@events.listener(hikari.RoleCreateEvent)
async def on_role_create(event: hikari.RoleCreateEvent):
    bot = events.bot
    await update_redis_cache(bot.cache.get_available_guild(event.guild_id))

@events.listener(hikari.RoleDeleteEvent)
async def on_role_delete(event: hikari.RoleDeleteEvent):
    bot = events.bot
    await update_redis_cache(bot.cache.get_available_guild(event.guild_id))

############################# Redis #############################

def make_lavalink_events(bot: lightbulb.BotApp):
    while not bot.lavalink:
        time.sleep(.1)
    lavalink: lavaplayer.LavalinkClient = bot.lavalink
    lavalink.event_manager.add_listener(lavaplayer.PlayerUpdateEvent, on_player_update)
    lavalink.event_manager.add_listener(lavaplayer.TrackStartEvent, track_start_event)
    lavalink.event_manager.add_listener(lavaplayer.TrackEndEvent, track_end_event)

def load(bot: lightbulb.BotApp):
    bot.add_plugin(events)
    threading.Thread(target=make_lavalink_events, args=(bot,)).start()

def unload(bot: lightbulb.BotApp):
    lavalink: lavaplayer.LavalinkClient = bot.lavalink
    lavalink.event_manager.remove_listener(lavaplayer.PlayerUpdateEvent, on_player_update)
    lavalink.event_manager.remove_listener(lavaplayer.TrackStartEvent, track_start_event)
    lavalink.event_manager.remove_listener(lavaplayer.TrackEndEvent, track_end_event)
    bot.remove_plugin(events)

