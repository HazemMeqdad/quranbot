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
            "quran", "general", "admin",  "moshaf", "owner", "hadith", "events"
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
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        tasks.load(self)
        
    def setup(self):
        self.load_extensions(*[f"bot.extensions.{i}" for i in self._extensions])

    async def make_tasks(self):
        await asyncio.sleep(20)
        timers = [1800, 3600, 7200, 21600, 43200, 86400]
        for timer in timers:
            task_manger = manger.Manger(timer)
            task = tasks.Task(task_manger.start, triggers.UniformTrigger(timer), auto_start=True, max_consecutive_failures=0, max_executions=None, pass_app=True, wait_before_execution=False)
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


    def run(self):
        self.setup()
        self.event_manager.subscribe(hikari.StartedEvent, self.on_ready)
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_shotdown)
        self.event_manager.subscribe(hikari.ShardReadyEvent, self.on_shard_ready)

        super().run(
            activity=hikari.Activity(
                name="/help - fdrbot.com",
                type=hikari.ActivityType.PLAYING,
            ),
            status=hikari.Status.DO_NOT_DISTURB,
            asyncio_debug=False
        )

