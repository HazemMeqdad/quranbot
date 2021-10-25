import logging
from bot import utils
from bot import database
import hikari
import lightbulb
import lavasnek_rs
from .utils import EventHandler, CustomHelp, create_tasks, stop_tasks
import pymongo


class Bot(lightbulb.Bot):
    def __init__(self):
        token = open("./bot/config/token.txt", "r").read()
        self._extensions = [
            "commands.general", "commands.errors", "commands.admin", "commands.owner", "commands.play",
            "slash_commands.general", "slash_commands.admin", "slash_commands.play", "slash_commands.errors"
        ]
        super().__init__(
            insensitive_commands=True,
            prefix=lightbulb.when_mentioned_or(self.resolve_prefix),
            ignore_bots=False,
            owner_ids=[750376850768789534],
            token=token,
            help_class=CustomHelp,
            banner=None,
            delete_unbound_slash_commands=False
        )
        self.print_banner("bot.banner", True, True)
        self.emojis = utils.Emojis(self.rest)
        self.footer = "بوت فاذكروني لإحياء سنة ذكر الله"
        mongo_url = open("./bot/config/mongo_url.txt", "r").read()
        mongodb = pymongo.MongoClient(mongo_url)
        self.db: database.DB = database.DB(mongodb["fa-azcrone"])
        self.lavalink_is_ready: bool = False
        
    def setup(self):
        print("\n")
        for extension in self._extensions:
            self.load_extension(f"bot.plugins.{extension}")
            logging.info(f"Loaded: {extension}")

    @staticmethod
    async def check_only_guild(message: lightbulb.Context):
        return message.guild_id is not None

    async def on_guild_create_message(self, event: hikari.GuildMessageCreateEvent):
        if not self.db.get_guild(event.guild_id):
            self.db.insert(event.guild_id)

    async def resolve_prefix(self, bot: lightbulb.Bot, message: hikari.Message):
        if not message.guild_id:
            return "!"
        guild = self.db.get_guild(message.guild_id)
        if not guild:
            self.db.insert(guild)
            return "!"
        return guild.prefix

    async def on_ready(self, event: hikari.StartedEvent):
        logging.info(self.get_me().username)
        self.add_check(self.check_only_guild)
        builder = (
            lavasnek_rs.LavalinkBuilder(self.get_me().id, self._token)
            .set_host("127.0.0.1")
            .set_port(8888)
            .set_password("pass")
            .set_start_gateway(False)
            .set_shard_count(self.shard_count)
        )
        lavalink_client = await builder.build(EventHandler())
        self.lavalink = lavalink_client
        logging.info("lavalink is ready WOW")
        await create_tasks(self)
        logging.info("tasks now ready")

    async def on_shotdown(self, event: hikari.StoppedEvent):
        logging.info("shotdown event start")
        stop_tasks()
        logging.info("shotdown event end")


    async def on_guild_join(self, event: hikari.GuildAvailableEvent):
        owner = await event.get_guild().fetch_owner()
        embed = hikari.Embed(
            title="أضافة جديده",
            color=0x46FF00
        )
        embed.add_field("اسم الخادم:", f"{event.get_guild().name} (`{event.get_guild().id}`)")
        embed.add_field("عدد أعضاء الخادم:", event.get_guild().member_count)
        embed.add_field("مالك الخادم:", f"{owner.username}#{owner.discriminator} (`{owner.id}`)")
        embed.add_field("خوادم فاذكروني", str(len(self.cache.get_guilds_view())))
        embed.set_footer(text=event.get_guild().name, icon=event.get_guild().icon_url)
        embed.set_author(name=self.get_me().username, icon=self.get_me().avatar_url)
        await self.rest.execute_webhook(
            853316492631605268, 
            "En1BiIqnADnVRY7RGFGwMGxYNWwHBcSO_8SMvdEbMWMvD5ZgCAxMYhN3pKy1ON",
            embed=embed
        )
    
    async def on_guild_leave(self, event: hikari.GuildLeaveEvent):
        owner = await self.rest.fetch_user(event.get_guild().owner_id)
        embed = hikari.Embed(
            title="ازالة جديده",
            color=0xFF0000
        )
        embed.add_field("اسم الخادم:", f"{event.get_guild().name} (`{event.get_guild().id}`)")
        embed.add_field("عدد أعضاء الخادم:", event.get_guild().member_count)
        embed.add_field("مالك الخادم:", f"{owner.username}#{owner.discriminator} (`{owner.id}`)")
        embed.add_field("خوادم فاذكروني", str(len(self.cache.get_guilds_view())))
        embed.set_footer(text=event.get_guild().name, icon=event.get_guild().icon_url)
        embed.set_author(name=self.get_me().username, icon=self.get_me().avatar_url)
        await self.rest.execute_webhook(
            853316492631605268, 
            "En1BiIqnADnVRY7RGFGwMGxYNWwHBcSO_8SMvdEbMWMvD5ZgCAxMYhN3pKy1ON",
            embed=embed
        )

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
        super().run(
                activity=hikari.Activity(
                    name="/help - fdrbot.xyz",
                    type=hikari.ActivityType.PLAYING,
                ),
                status=hikari.Status.DO_NOT_DISTURB,
                asyncio_debug=False
            )

