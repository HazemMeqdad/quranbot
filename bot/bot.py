import logging
from bot import utils
from bot import database
import hikari
import lightbulb
import lavaplayer
from .utils import Tasks
import pymongo
import yaml
from bot.api import Api
from lightbulb.ext import tasks


class Bot(lightbulb.BotApp):
    def __init__(self):
        self.config = yaml.load(open("configuration.yml", "r", encoding="utf-8"), Loader=yaml.FullLoader)
        self._extensions = [  # plugins
            "quran", "general", "admin",  "moshaf", "owner"
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
        mongodb = pymongo.MongoClient(self.config["bot"]["mongo_url"])
        self.db: database.DB = database.DB(mongodb["fa-azcrone"])
        self.lavalink: lavaplayer.LavalinkClient = None
        # logging.getLogger().setLevel(logging.DEBUG)
        
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
        tasks.load(self)
        self.azkar_task.start()

    @tasks.task(h=4)
    async def azkar_task(self):
        self.tasks = Tasks(
            guilds=self.cache.get_available_guilds_view(), 
            rest=self.rest, 
            bot=self.get_me(), 
            db=self.db
        )
        await self.tasks.start()

    async def on_shotdown(self, event: hikari.StoppedEvent):
        # stop_tasks()
        logging.info("shotdown event tasks")

    async def on_shard_ready(self, event: hikari.ShardReadyEvent):
        if event.shard.id == self.shard_count-1:
            await self.create_lavalink_connection()
            # await create_tasks(self)
            # logging.info("tasks now ready")


    async def create_lavalink_connection(self):
        self.lavalink = lavaplayer.LavalinkClient(
            host=self.config["lavalink"]["host"],
            password=self.config["lavalink"]["password"],
            port=self.config["lavalink"]["port"],
            user_id=self.get_me().id,
            num_shards=self.shard_count,
        )
        self.lavalink.connect()

    async def interaction_create_event(self, event: hikari.InteractionCreateEvent):
        if event.interaction.type == hikari.InteractionType.MESSAGE_COMPONENT and event.interaction.custom_id == "add_role":
            user = self.cache.get_member(event.interaction.member.guild_id, event.interaction.member.user)
            if not user:
                user = await event.app.rest.fetch_member(event.interaction.member.guild_id, event.interaction.member.user)
            role_ids = user.role_ids
            if 960519125082464287 in role_ids:
                await event.app.rest.remove_role_from_member(event.interaction.member.guild_id, user, 960519125082464287)
                await event.app.rest.create_interaction_response(
                    interaction=event.interaction,
                    token=event.interaction.token,
                    response_type=hikari.ResponseType.MESSAGE_CREATE,
                    content="تم الغاء أشتراك بالرتبه بنجاح",
                    flags=hikari.MessageFlag.EPHEMERAL
                )
            else:
                await event.app.rest.add_role_to_member(event.interaction.member.guild_id, user, 960519125082464287)
                await event.app.rest.create_interaction_response(
                    interaction=event.interaction,
                    token=event.interaction.token,
                    response_type=hikari.ResponseType.MESSAGE_CREATE,
                    content="تم أشتراكك بالرتبه بنجاح",
                    flags=hikari.MessageFlag.EPHEMERAL
                )

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

    async def on_error(self, event: lightbulb.CommandErrorEvent):
        logging.error(event.exception)

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
        self.event_manager.subscribe(lightbulb.CommandErrorEvent, self.on_error)
        self.event_manager.subscribe(hikari.InteractionCreateEvent, self.interaction_create_event)

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

