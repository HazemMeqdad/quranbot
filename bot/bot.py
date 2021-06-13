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
            shard_count=5,
            owner_ids=config.owners
        )
        self.remove_command("help")
        self._cogs = [
            "help",
            "general",
            "play",
            "errors",
            "owner",
            "admin"
        ]
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
        re = requests.post(config.webhook_shard, data={"content": msg})
        return re.status_code

    async def on_shard_ready(self, shard_id):
        await self._send_webhook("shard %s is ready" % shard_id)

    async def on_shard_disconnect(self, shard_id):
        await self._send_webhook("Shard %s has been disconnect." % shard_id)

    async def on_shard_resumed(self, shard_id):
        await self._send_webhook("Shard %s has been resumed." % shard_id)

    async def on_guild_join(self, guild):
        x = db.Guild(guild)
        x.insert()
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(config.webhook_log, adapter=AsyncWebhookAdapter(session))
            embed = discord.Embed(title="add guild", color=0x46FF00)
            embed.add_field(name='name guild: ', value="%s (`%s`)" % (guild.name, guild.id), inline=False)
            embed.add_field(name='member guild: ', value=guild.member_count, inline=False)
            embed.add_field(name='owner guild: ', value="%s (`%s`)" % (self.fetch_user(int(guild.owner_id)), guild.owner_id), inline=False)
            embed.add_field(name='bot server: ', value=f'{len(self.guilds)}', inline=False)
            embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
            await webhook.send(embed=embed)

    async def on_guild_remove(self, guild):
        x = db.Guild(guild)
        x.insert()
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(config.webhook_log, adapter=AsyncWebhookAdapter(session))
            embed = discord.Embed(title="remove guild", color=0xFF0000)
            embed.add_field(name='name guild: ', value="%s (`%s`)" % (guild.name, guild.id), inline=False)
            embed.add_field(name='member guild: ', value=guild.member_count, inline=False)
            embed.add_field(name='owner guild: ', value="%s (`%s`)" % (self.fetch_user(int(guild.owner_id)), guild.owner_id), inline=False)
            embed.add_field(name='bot server: ', value=f'{len(self.guilds)}', inline=False)
            embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
            await webhook.send(embed=embed)

    def run(self):
        super().run(config.token)
