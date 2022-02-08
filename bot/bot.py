import logging
from bot import utils
from bot import database
import hikari
import lightbulb
import lavasnek_rs
from .utils import EventHandler, create_tasks, stop_tasks
import pymongo
import yaml
from bot.api import Api

class Bot(lightbulb.BotApp):
    def __init__(self):
        self.config = yaml.load(open("configuration.yml", "r", encoding="utf-8"), Loader=yaml.FullLoader)
        self._extensions = [  # plugins
            "quran", "general", "admin",  "moshaf",
        ]
        super().__init__(
            prefix="/",
            ignore_bots=False,
            owner_ids=self.config["bot"]["owner_ids"],
            token=self.config["bot"]["token"],
            banner=None,
            delete_unbound_commands=True,
            default_enabled_guilds=self.config["bot"]["default_enabled_guilds"],
            case_insensitive_prefix_commands=True,
            help_class=None,
            
        )
        self.print_banner("bot.banner", True, True)
        self.emojis = utils.Emojis(self.config["emojis"])
        self.footer = self.config["bot"]["footer"]
        mongodb = pymongo.MongoClient(self.config["bot"]["mongo_url"])
        self.db: database.DB = database.DB(mongodb["fa-azcrone"])
        self.lavalink_is_ready: bool = False
        self.lavalink = None
        
    def setup(self):
        self.load_extensions(*[f"bot.extensions.{i}" for i in self._extensions])

    async def on_guild_create_message(self, event: hikari.GuildMessageCreateEvent):
        if not self.db.get_guild(event.guild_id):
            self.db.insert(event.guild_id)

    # not used because the prefix for all guilds is `/`
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
        

    async def on_shotdown(self, event: hikari.StoppedEvent):
        stop_tasks()
        logging.info("shotdown event tasks")

    async def on_shard_ready(self, event: hikari.ShardReadyEvent):
        if event.shard.id == self.shard_count-1:
            await self.create_lavalink_connection()
            # await create_tasks(self)
            # logging.info("tasks now ready")


    async def create_lavalink_connection(self):
        builder = (
            lavasnek_rs.LavalinkBuilder(self.get_me().id, self._token)
            .set_host(self.config["lavalink"]["host"])
            .set_port(self.config["lavalink"]["port"])
            .set_password(self.config["lavalink"]["password"])
            .set_start_gateway(False)
            .set_shard_count(self.shard_count)
        )
        lavalink_client = await builder.build(EventHandler())
        self.lavalink = lavalink_client
        self.lavalink_is_ready = True
        logging.info("new lavalink connection")


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
        if self.lavalink_is_ready:
            await self.lavalink.raw_handle_event_voice_state_update(
                event.state.guild_id,
                event.state.user_id,
                event.state.session_id,
                event.state.channel_id,
            )

    async def voice_server_update(self, event: hikari.VoiceServerUpdateEvent) -> None:
        if self.lavalink_is_ready:
            await self.lavalink.raw_handle_event_voice_server_update(
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
                    name="/help - fdrbot.xyz",
                    type=hikari.ActivityType.PLAYING,
                ),
                status=hikari.Status.DO_NOT_DISTURB,
                asyncio_debug=False
            )

