import asyncio
import json
import aioredis
import hikari
from lightbulb.ext import tasks
import lightbulb
import lavaplayer
import pymongo
import logging
from bot import manger, utils, database
import os
import json
try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    ...

log = logging.getLogger("fdrbot")

class Bot(lightbulb.BotApp):
    def __init__(self):
        self._extensions = [  # plugins
            "quran", "general", "admin",  "moshaf", "owner", "hadith", "events"
        ]
        os.environ.get("DEBUG", False) or self._extensions.append("errors")
        token = os.environ.get("TOKEN")
        if not token:
            raise ValueError("Token is not configured")
        super().__init__(
            ignore_bots=True,
            owner_ids=json.loads(os.environ.get("OWNER_IDS", "[]")),
            token=token,
            banner=None,
            default_enabled_guilds=json.loads(os.environ.get("DEFAULT_ENABLED_GUILDS", "[]")) if os.environ.get("DEBUG", False) else [],
            help_class=None,
        )
        self.print_banner("bot.banner", True, True)
        self.emojis = utils.Emojis()
        self.footer = os.environ.get("FOOTER", "بوت فاذكروني لإحياء سنة ذكر الله")
        mongo_url = os.environ.get("MONGO_URL")
        if not mongo_url:
            raise ValueError("MongoDB URI is not configured")
        mongodb = pymongo.MongoClient(mongo_url)
        self.db: database.DB = database.DB(mongodb["fdrbot"])
        self.lavalink: lavaplayer.LavalinkClient = None
        self.tasks = []
        if not os.environ.get("REDIS_URL"):
            log.warn("[ Configuration ] redis is not configured")
        self.redis = aioredis.from_url(os.environ["REDIS_URL"], decode_responses=True)
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        tasks.load(self)
        
    def setup(self):
        self.load_extensions(*[f"bot.extensions.{i}" for i in self._extensions])

    # async def make_tasks(self):
    #     await asyncio.sleep(20)
    #     timers = [1800, 3600, 7200, 21600, 43200, 86400]
    #     for timer in timers:
    #         task_manger = manger.Manger(timer)
    #         task = tasks.Task(task_manger.start, triggers.UniformTrigger(timer), auto_start=True, max_consecutive_failures=0, max_executions=None, pass_app=True, wait_before_execution=False)
    #         self.tasks.append(task)
    #         # this is for not to make the bot crash when the bot is restarted
    #         await asyncio.sleep(timer / 8)

    async def create_lavalink_connection(self):
        if not os.environ.get("LAVALINK_HOST") and not os.environ.get("LAVALINK_PORT") and not os.environ.get("LAVALINK_PASSWORD"):
            log.warning("[ Configuration ] lavalink is not configured")
            return
        self.lavalink = lavaplayer.LavalinkClient(
            host=os.environ["LAVALINK_HOST"],
            password=os.environ["LAVALINK_PASSWORD"],
            port=os.environ["LAVALINK_PORT"],
            user_id=self.get_me().id,
            num_shards=self.shard_count,
        )
        self.lavalink.connect()

    @classmethod
    @tasks.task(s=10, auto_start=True, pass_app=True, max_consecutive_failures=0)
    async def azkar_sender_update(app: lightbulb.BotApp):
        cache_guilds = filter(lambda guild: isinstance(guild, hikari.Guild), app.cache.get_guilds_view().values())
        db_guilds = app.db.fetch_guilds_with_datetime()
        guilds = list(filter(lambda x: x.id in [i.id for i in db_guilds], list(cache_guilds)))

        task_manager = manger.Manger(app, guilds[:3])
        await task_manager.start()

    @classmethod
    @tasks.task(s=10, auto_start=True, pass_app=True)
    async def stats_redis_update(app: lightbulb.BotApp):
        status = {
            "shards": app.shard_count,
            "guilds": len(app.cache.get_available_guilds_view().values()),
            "channels": len(app.cache.get_guild_channels_view().values()),
            "online": True
        }
        await app.redis.set("bot:stats", json.dumps(status))

    async def on_ready(self, event: hikari.StartedEvent):
        log.info(self.get_me().username + " is ready")

    # async def on_shotdown(self, event: hikari.StoppedEvent): 
    #     async for key in self.redis.scan_iter(match="guild:*"):
    #         await self.redis.delete(key)
    #     stats = json.loads(await self.redis.get("bot:stats"))
    #     stats["online"] = False
    #     await self.redis.set("bot:stats", json.dumps(stats))
    #     log.info("[ Redis ] cache reset")

    async def on_shard_ready(self, event: hikari.ShardReadyEvent):
        if event.shard.id == self.shard_count-1:
            await self.create_lavalink_connection()


    def run(self):
        self.setup()
        self.event_manager.subscribe(hikari.StartedEvent, self.on_ready)
        # self.event_manager.subscribe(hikari.StoppedEvent, self.on_shotdown)
        self.event_manager.subscribe(hikari.ShardReadyEvent, self.on_shard_ready)

        super().run(
            activity=hikari.Activity(
                name="/help - fdrbot.com",
                type=hikari.ActivityType.PLAYING,
            ),
            status=hikari.Status.DO_NOT_DISTURB,
            asyncio_debug=False
        )

