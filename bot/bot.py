import discord
from discord.ext import commands
import bot.db as db
import requests
import bot.config as config


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self._get_prefix,
            case_insensitive=True,
            description="بوت فذكروني",
            Intents=discord.Intents.default(),
            shard_count=5,
            owner_ids=config.owners
        )
        self.remove_command("help")
        self._cogs = [
            "prefix",
            "help",
            "commands",
            "setroom",
            "set_time",
            "play",
            'errors',
            'event',
            'set',
            'owner'
        ]

    @staticmethod
    def _get_prefix(bot, msg):
        x = db.Guild(msg.guild)
        prefix = commands.when_mentioned_or('!')
        try:
            prefix = commands.when_mentioned_or(x.info[2])
        except AttributeError:
            prefix = commands.when_mentioned_or('!')
        finally:
            return prefix(bot, msg)

    async def _setup(self):
        for i in self._cogs:
            try:
                self.load_extension(f"bot.cogs.{i}")
                print(f"load: {i}")
            except Exception as error:
                print(f"the error is \n{error}")

    async def on_ready(self):
        await self._setup()
        for i in self.guilds:
            x = db.Guild(i)
            x.insert()
        await self.change_presence(
            activity=discord.Game(type=discord.ActivityType.listening, name='!help - بوت فاذكروني'),
            status=discord.Status.idle)
        print(f"Name: {self.user.name}\nID: {self.user.id}")

    @staticmethod
    async def _send_webhook(msg):
        re = requests.post(config.webhook, data={"content": msg})
        return re.status_code

    async def on_shard_ready(self, shard_id):
        await self._send_webhook("shard %s is ready" % shard_id)

    async def on_shard_disconnect(self, shard_id):
        await self._send_webhook("Shard %s has been disconnect." % shard_id)

    async def on_shard_resumed(self, shard_id):
        await self._send_webhook("Shard %s has been resumed." % shard_id)

    def run(self):
        super().run(config.token)
