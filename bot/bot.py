import asyncio
import hikari
from lightbulb.ext import tasks
from lightbulb.ext.tasks import triggers
import lightbulb
import lavaplayer
import pymongo
import yaml
import logging
from bot.api import Api
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
        self.db: database.DB = database.DB(mongodb["fa-azcrone"])
        self.lavalink: lavaplayer.LavalinkClient = None
        self.tasks = []
        tasks.load(self)
        
    def setup(self):
        self.load_extensions(*[f"bot.extensions.{i}" for i in self._extensions])

    async def make_tasks(self):
        await asyncio.sleep(20)
        timers = [1800, 3600, 7200, 10800, 21600, 43200, 86400]
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

    async def on_ready(self, event: hikari.StartedEvent):
        log.info(self.get_me().username + " is ready")
        self.create_task(self.make_tasks())

    async def on_shotdown(self, event: hikari.StoppedEvent):
        log.info("shotdown event tasks")

    async def on_shard_ready(self, event: hikari.ShardReadyEvent):
        if event.shard.id == self.shard_count-1:
            await self.create_lavalink_connection()

    async def on_guild_join(self, event: hikari.GuildJoinEvent):
        self.db.insert(event.get_guild().id)
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
            self.config["webhook"]["id"], 
            self.config["webhook"]["token"],
            embed=embed
        )
    
    async def on_guild_leave(self, event: hikari.GuildLeaveEvent):
        self.db.delete_guild(event.guild_id)
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
                self.config["webhook"]["id"], 
                self.config["webhook"]["token"],
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

    def run(self):
        self.setup()
        self.event_manager.subscribe(hikari.StartedEvent, self.on_ready)
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_shotdown)
        self.event_manager.subscribe(hikari.ShardReadyEvent, self.on_shard_ready)

        self.event_manager.subscribe(hikari.GuildJoinEvent, self.on_guild_join)
        self.event_manager.subscribe(hikari.GuildLeaveEvent, self.on_guild_leave)

        self.event_manager.subscribe(hikari.VoiceServerUpdateEvent, self.voice_server_update)
        self.event_manager.subscribe(hikari.VoiceStateUpdateEvent, self.voice_state_update)
        
        self.api = Api(self)
        self.api.run_as_thread()
        super().run(
            activity=hikari.Activity(
                name="/help - fdrbot.com",
                type=hikari.ActivityType.PLAYING,
            ),
            status=hikari.Status.DO_NOT_DISTURB,
            asyncio_debug=False
        )

