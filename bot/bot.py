import logging
from bot import utils
from bot import db
import hikari
import lightbulb
from .utils import CustomHelp
import lavasnek_rs
from .utils import EventHandler
import tasks

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
            # intents=hikari.Intents.ALL,
            help_class=CustomHelp,
            banner=None
        )
        self.print_banner("bot.banner", True, True)
        self.emojis = utils.Emojis(self.rest)
        self.footer = "بوت فاذكروني لإحياء سنة ذكر الله"
        # self.tasks = [
        #     Task(sender_task, 1800, self.rest, 1800),    # 30 minutes
        #     Task(sender_task, 3600, self.rest, 3600),    # 1 hour
        #     Task(sender_task, 7200, self.rest, 7200),    # 2 hours
        #     Task(sender_task, 21600, self.rest, 21600),  # 6 hours
        #     Task(sender_task, 43200, self.rest, 43200),  # 12 hours
        #     Task(sender_task, 86400, self.rest, 86400),  # 24 hours
        # ]
        
    def setup(self):
        print("\n")
        for extension in self._extensions:
            self.load_extension(f"bot.plugins.{extension}")
            logging.info(f"Loaded: {extension}")

    @staticmethod
    async def check_only_guild(message: lightbulb.Context):
        return message.guild_id is not None

    async def on_guild_available(self, event: hikari.GuildAvailableEvent):
        x = db.Guild(event.guild_id)
        self.cache.get_guilds_view()
        if not x.info:
            await x.insert()

    async def resolve_prefix(self, bot: lightbulb.Bot, message: hikari.Message):
        if not message.guild_id:
            return "!"
        prefix = db.Guild(message.guild_id).info.get("prefix")
        return prefix if prefix else "!"

    async def on_ready(self, event: hikari.StartedEvent):
        logging.info(self.get_me().username)
        self.add_check(self.check_only_guild)
        builder = (
            lavasnek_rs.LavalinkBuilder(self.get_me().id, self._token)
            .set_host("127.0.0.1")
            .set_port(8888)
            .set_password("pass")
            .set_shard_count(self.shard_count)
        )
        lavalink_client = await builder.build(EventHandler())
        self.lavalink = lavalink_client

    async def tasks_ready(self, event: hikari.ShardReadyEvent):
        # t = tasks.Loop(await tasks.sender_task(self.rest, 1800), seconds=1800)
        # t.start()
        logging.info("tasks now ready")

    async def start_lavalink(self, event: hikari.ShardReadyEvent):
        pass

    async def on_shotdown(self, event: hikari.StoppedEvent):
        pass

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
        owner = await event.get_guild().fetch_owner()
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

    def run(self):
        self.setup()
        self.event_manager.subscribe(hikari.StartedEvent, self.on_ready)
        self.event_manager.subscribe(hikari.GuildAvailableEvent, self.on_guild_available)
        self.event_manager.subscribe(hikari.ShardReadyEvent, self.start_lavalink)
        self.event_manager.subscribe(hikari.ShardReadyEvent, self.tasks_ready)
        self.event_manager.subscribe(hikari.StoppedEvent, self.on_shotdown)
        self.event_manager.subscribe(hikari.GuildJoinEvent, self.on_guild_join)
        self.event_manager.subscribe(hikari.GuildLeaveEvent, self.on_guild_leave)
        super().run(
                activity=hikari.Activity(
                    name="/help - فاذكروني الأصدار التجريبي",
                    type=hikari.ActivityType.PLAYING,
                ),
                status=hikari.Status.DO_NOT_DISTURB,
                asyncio_debug=False
            )

