import asyncio
import json
import hikari
from lightbulb.ext import tasks
from lightbulb.ext.tasks import triggers
import lightbulb
import lavaplayer
import pymongo
import redis
import yaml
import logging
from bot import manger, utils, database
import os

log = logging.getLogger("fdrbot")

class Bot(lightbulb.BotApp):
    def __init__(self):
        self.config = yaml.load(open("configuration.yml", "r", encoding="utf-8"), Loader=yaml.FullLoader)
        self._extensions = [  # plugins
            "quran", "general", "admin",  "moshaf", "owner"
        ]
        self.config["bot"].get("debug", False) or self._extensions.append("errors")
        if not self.config["bot"].get("token"):
            raise ValueError("Token is not configured")
        super().__init__(
            ignore_bots=True,
            owner_ids=self.config["bot"].get("owner_ids", []),
            token=self.config["bot"]["token"],
            banner=None,
            default_enabled_guilds=self.config["bot"].get("default_enabled_guilds", ()) if self.config["bot"].get("debug", False) else [],
            help_class=None,
        )
        self.print_banner("bot.banner", True, True)
        self.emojis = utils.Emojis(self.config.get("emojis", {}))
        self.footer = self.config["bot"].get("footer", "بوت فاذكروني لإحياء سنة ذكر الله")
        if not os.environ.get("MONGODB_URI", self.config["bot"].get("mongo_url")):
            raise ValueError("MongoDB URI is not configured")
        mongodb = pymongo.MongoClient(os.environ.get("MONGODB_URI", self.config["bot"]["mongo_url"]))
        self.db: database.DB = database.DB(mongodb["fdrbot"])
        self.lavalink: lavaplayer.LavalinkClient = None
        self.tasks = []
        if not self.config.get("redis"):
            log.warn("[ Configuration ] redis is not configured")
        self.redis = redis.Redis(**self.config["redis"])
        tasks.load(self)
        
    def setup(self):
        self.load_extensions(*[f"bot.extensions.{i}" for i in self._extensions])

    async def make_tasks(self):
        await asyncio.sleep(20)
        timers = [1800, 3600, 7200, 21600, 43200, 86400]
        for timer in timers:
            task_manger = manger.Manger(timer)
            task = tasks.Task(task_manger.start, triggers.UniformTrigger(timer), auto_start=True, max_consecutive_failures=100, max_executions=None, pass_app=True, wait_before_execution=False)
            self.tasks.append(task)
            # this is for not to make the bot crash when the bot is restarted
            await asyncio.sleep(timer / 8)

    async def create_lavalink_connection(self):
        if not self.config.get("lavalink"):
            log.warning("[ Configuration ] lavalink is not configured")
            return
        self.lavalink = lavaplayer.LavalinkClient(
            host=self.config["lavalink"]["host"],
            password=self.config["lavalink"]["password"],
            port=self.config["lavalink"]["port"],
            user_id=self.get_me().id,
            num_shards=self.shard_count,
        )
        self.lavalink.connect()

    @classmethod
    @tasks.task(s=10, auto_start=True, pass_app=True)
    async def stats_redis_update(app: lightbulb.BotApp):
        status = {
            "shards": app.shard_count,
            "guilds": len(app.cache.get_available_guilds_view().values()),
            "channels": len(app.cache.get_guild_channels_view().values()),
            "online": True
        }
        app.redis.set("bot:stats", json.dumps(status))

    async def on_ready(self, event: hikari.StartedEvent):
        log.info(self.get_me().username + " is ready")
        # self.status_redis_update.start()
        self.create_task(self.make_tasks())

    async def on_shotdown(self, event: hikari.StoppedEvent):
        for key in self.redis.scan_iter(match="guild:*"):
            self.redis.delete(key)
        stats = json.loads(self.redis.get("bot:stats"))
        stats["online"] = False
        self.redis.set("bot:stats", json.dumps(stats))
        log.info("[ Redis ] cache reset")

    async def on_shard_ready(self, event: hikari.ShardReadyEvent):
        if event.shard.id == self.shard_count-1:
            await self.create_lavalink_connection()

    async def on_guild_join(self, event: hikari.GuildJoinEvent):
        self.db.insert(event.get_guild().id)
        if not self.config.get("webhooks") or not self.config["webhooks"].get("logger"):
            return
        owner_id = event.get_guild().owner_id
        owner = await self.rest.fetch_user(owner_id)
        
        embed = hikari.Embed(
            title="أضافة جديده",
            color=0x46FF00
        )
        embed.add_field("اسم الخادم:", f"{event.get_guild().name} (`{event.get_guild().id}`)")
        embed.add_field("عدد أعضاء الخادم:", str(event.get_guild().member_count))
        embed.add_field("مالك الخادم:", f"{owner.username}#{owner.discriminator} (`{owner.id}`)")
        embed.add_field("خوادم فاذكروني", str(len(self.cache.get_guilds_view())))
        embed.set_footer(text=event.get_guild().name, icon=event.get_guild().icon_url)
        embed.set_author(name=self.get_me().username, icon=self.get_me().avatar_url)
        await self.rest.execute_webhook(
            self.config["webhooks"]["logger"]["id"], 
            self.config["webhooks"]["logger"]["token"],
            embed=embed
        )
    
    async def on_guild_leave(self, event: hikari.GuildLeaveEvent):
        self.db.delete_guild(event.guild_id)
        if not self.config.get("webhooks") or not self.config["webhooks"].get("logger"):
            return
        guild = event.old_guild
        if guild:
            owner_id = guild.owner_id
            owner = await self.rest.fetch_user(owner_id)
            embed = hikari.Embed(
                title="أضافة جديده",
                color=0xFF0000
            )
            embed.add_field("اسم الخادم:", f"{guild.name} (`{guild.id}`)")
            embed.add_field("عدد أعضاء الخادم:", str(guild.member_count))
            embed.add_field("مالك الخادم:", f"{owner.username}#{owner.discriminator} (`{owner.id}`)")
            embed.add_field("خوادم فاذكروني", str(len(self.cache.get_guilds_view())))
            embed.set_footer(text=guild.name, icon=guild.icon_url)
            embed.set_author(name=self.get_me().username, icon=self.get_me().avatar_url)
            await self.rest.execute_webhook(
                self.config["webhooks"]["logger"]["id"], 
                self.config["webhooks"]["logger"]["token"],
                embed=embed
            )

    async def voice_state_update(self, event: hikari.VoiceStateUpdateEvent) -> None:
        if self.lavalink and self.lavalink.is_connect:
            await self.lavalink.raw_voice_state_update(
                event.state.guild_id,
                event.state.user_id,
                event.state.session_id,
                event.state.channel_id,
            )

    async def voice_server_update(self, event: hikari.VoiceServerUpdateEvent) -> None:
        if self.lavalink and self.lavalink.is_connect:
            await self.lavalink.raw_voice_server_update(
                event.guild_id, event.endpoint, event.token
            )

    # Redis cache events
    async def update_redis_cache(self, guild: hikari.Guild):
        data = {
            "id": guild.id.__str__(),
            "name": guild.name,
            "icon_url": guild.icon_url.url if guild.icon_url else None,
            "member_count": guild.member_count.__str__(),
            "description": guild.description,
            "owner_id": guild.owner_id.__str__(),
            "channels": [{"id": channel.id.__str__(), "name": channel.name, "type": channel.type.value} for channel in guild.get_channels().values()],
            "roles": [{"id": role.id.__str__(), "name": role.name} for role in guild.get_roles().values()],
        }
        self.redis.set(f"guild:{guild.id}", json.dumps(data))

    async def guild_available(self, event: hikari.GuildAvailableEvent) -> None:
        await self.update_redis_cache(event.guild)

    async def guild_unavailable(self, event: hikari.GuildUnavailableEvent) -> None:
        self.redis.delete(f"guild:{event.guild_id}")

    async def on_guild_update(self, event: hikari.GuildUpdateEvent) -> None:
        await self.update_redis_cache(event.guild)

    async def on_channel_update(self, event: hikari.GuildChannelEvent) -> None:
        await self.update_redis_cache(event.get_guild())

    async def on_role_update(self, event: hikari.RoleUpdateEvent) -> None:
        await self.update_redis_cache(self.cache.get_available_guild(event.guild_id))

    async def on_role_create(self, event: hikari.RoleCreateEvent):
        await self.update_redis_cache(self.cache.get_available_guild(event.guild_id))
    
    async def on_role_delete(self, event: hikari.RoleDeleteEvent):
        await self.update_redis_cache(self.cache.get_available_guild(event.guild_id))

    def run(self):
        self.setup()
        self.event_manager.subscribe(hikari.StartedEvent, self.on_ready)
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_shotdown)
        self.event_manager.subscribe(hikari.ShardReadyEvent, self.on_shard_ready)

        self.event_manager.subscribe(hikari.GuildJoinEvent, self.on_guild_join)
        self.event_manager.subscribe(hikari.GuildLeaveEvent, self.on_guild_leave)

        self.event_manager.subscribe(hikari.VoiceServerUpdateEvent, self.voice_server_update)
        self.event_manager.subscribe(hikari.VoiceStateUpdateEvent, self.voice_state_update)

        # To redis cache
        self.event_manager.subscribe(hikari.GuildAvailableEvent, self.guild_available)
        self.event_manager.subscribe(hikari.GuildUnavailableEvent, self.guild_unavailable)
        self.event_manager.subscribe(hikari.GuildUpdateEvent, self.on_guild_update)
        self.event_manager.subscribe(hikari.GuildChannelEvent, self.on_channel_update)
        self.event_manager.subscribe(hikari.RoleUpdateEvent, self.on_role_update)
        self.event_manager.subscribe(hikari.RoleCreateEvent, self.on_role_create)
        self.event_manager.subscribe(hikari.RoleDeleteEvent, self.on_role_delete)

        super().run(
            activity=hikari.Activity(
                name="/help - fdrbot.com",
                type=hikari.ActivityType.PLAYING,
            ),
            status=hikari.Status.DO_NOT_DISTURB,
            asyncio_debug=False
        )

