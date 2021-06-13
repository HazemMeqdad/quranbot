import discord
from discord.ext import commands
import bot.db as db
import requests
import bot.config as config
from discord import Webhook, AsyncWebhookAdapter
import aiohttp


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=self._get_prefix,
            case_insensitive=True,
            description="بوت فذكروني",
            Intents=discord.Intents.default(),
            shard_count=6,
            owner_ids=config.owners
        )
        self.remove_command("help")
        self._cogs = [
            # "help",
            # "general",
            "play",
            # "owner",
            # "admin"
        ]
        self.load_extension("bot.cogs.errors")
        # self.load_extension("bot.events.loop")
        self.add_check(self.check_blacklist)

    @staticmethod
    def check_blacklist(ctx):
        return db.BlackList(ctx.author).check

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

    def _setup(self):
        for i in self._cogs:
            try:
                self.load_extension(f"bot.cogs.{i}")
            except Exception as error:
                print(f"the error is \n{error}")
        self.load_extension("bot.events.events")
        self.load_extension("bot.events.loop")

    async def on_ready(self):
        self._setup()
        for i in self.guilds:
            x = db.Guild(i)
            x.insert()
        await self.change_presence(
            activity=discord.Game(name='!help - fdrbot.xyz'),
            status=discord.Status.dnd)
        print(f"Name: {self.user.name}\nID: {self.user.id}")

    @staticmethod
    async def _send_webhook(msg):
        re = requests.post(config.webhook_shard, data={"content": msg})
        return re.status_code

    async def on_shard_ready(self, shard_id):
        print(f'`shard {shard_id} is ready`')
        await self._send_webhook("shard %s is ready" % shard_id)

    async def on_shard_disconnect(self, shard_id):
        # print(f'Shard {shard_id} has been disconnect.')
        await self._send_webhook("Shard %s has been disconnect." % shard_id)

    async def on_shard_resumed(self, shard_id):
        # print(f'Shard {shard_id} has been resumed.')
        await self._send_webhook("Shard %s has been resumed." % shard_id)

    def run(self):
        super().run(config.token)
