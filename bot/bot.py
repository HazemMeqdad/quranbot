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

class Bot(lightbulb.BotApp):
    def __init__(self):
        self.config = yaml.load(open("configuration.yml", "r", encoding="utf-8"), Loader=yaml.FullLoader)
        self._extensions = [  # plugins
            "quran", "general", "admin",  "moshaf", "owner", "errors"
        ]
        super().__init__(
            prefix="/",
            ignore_bots=False,
            owner_ids=self.config["bot"]["owner_ids"],
            token=self.config["bot"]["token"],
            banner=None,
            # default_enabled_guilds=[843865725886398554],
            case_insensitive_prefix_commands=True,
            help_class=None,

        )
        self.print_banner("bot.banner", True, True)
        self.emojis = utils.Emojis(self.config["emojis"])
        self.footer = self.config["bot"]["footer"]
        mongodb = pymongo.MongoClient(os.environ.get("MONGODB_URI", self.config["bot"]["mongo_url"]))
        self.db: database.DB = database.DB(mongodb["fa-azcrone"])
        self.lavalink: lavaplayer.LavalinkClient = None
        tasks.load(self)
        
    def setup(self):
        self.load_extensions(*[f"bot.extensions.{i}" for i in self._extensions])

    async def on_guild_create_message(self, event: hikari.GuildMessageCreateEvent):
        if not self.db.get_guild(event.guild_id):
            self.db.insert(event.guild_id)

    # not used because the prefix for all guilds is use slash commands
    async def resolve_prefix(self, bot: lightbulb.BotApp, message: hikari.Message):
        if not message.guild_id:
            return ["!", "/"]
        guild = self.db.get_guild(message.guild_id)
        if not guild:
            self.db.insert(guild)
            return ["!", "/"]
        return [guild.prefix, "/"]

    async def on_ready(self, event: hikari.StartedEvent):
        logging.info(self.get_me().username)
        # self.create_task(self.make_tasks())

    async def make_tasks(self):
        await asyncio.sleep(20)
        timers = [1800, 3600, 7200, 10800, 21600, 43200, 86400]
        for timer in timers:
            x = tasks.Task(self.task, triggers.UniformTrigger(timer), auto_start=True, max_consecutive_failures=3, max_executions=None, pass_app=False, wait_before_execution=False)
            x.start()

    async def task(self, timer: int) -> None:
        x = filter(lambda guild: isinstance(guild, hikari.Guild), self.cache.get_guilds_view().values())
        guilds = filter(lambda x: x.id in self.db.fetch_guilds_by_time(timer), x)
        task_manger = manger.Manger(list(guilds), self.rest, self.get_me(), self.db)
        await task_manger.start(timer)

    async def on_shotdown(self, event: hikari.StoppedEvent):
        # stop_tasks()
        logging.info("shotdown event tasks")

    async def on_shard_ready(self, event: hikari.ShardReadyEvent):
        if event.shard.id == self.shard_count-1:
            await self.create_lavalink_connection()

    async def create_lavalink_connection(self):
        self.lavalink = lavaplayer.LavalinkClient(
            host=self.config["lavalink"]["host"],
            password=self.config["lavalink"]["password"],
            port=self.config["lavalink"]["port"],
            user_id=self.get_me().id,
            num_shards=self.shard_count,
        )
        self.lavalink.connect()

    async def on_guild_join(self, event: hikari.GuildAvailableEvent):
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
        """
        removed because of not get_guild(...) work 😭
        """

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
        self.event_manager.subscribe(hikari.GuildMessageCreateEvent, self.on_guild_create_message)
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_shotdown)
        self.event_manager.subscribe(hikari.GuildJoinEvent, self.on_guild_join)
        self.event_manager.subscribe(hikari.GuildLeaveEvent, self.on_guild_leave)
        self.event_manager.subscribe(hikari.VoiceServerUpdateEvent, self.voice_server_update)
        self.event_manager.subscribe(hikari.VoiceStateUpdateEvent, self.voice_state_update)
        self.event_manager.subscribe(hikari.ShardReadyEvent, self.on_shard_ready)
        
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

