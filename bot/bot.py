import discord
from discord.ext import commands
import bot.db as db
from requests import request
import bot.config as config
from base64 import b64encode


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self._get_prefix,
            case_insensitive=True,
            description="بوت فذكروني",
            Intents=discord.Intents.default(),
            shard_count=config.shards_count,
            owner_ids=config.owners
        )
        self.remove_command("help")
        _cogs = [
            "help",
            "general",
            "play",
            "owner",
            "admin",
            "loop"
        ]
        self.load_extension("bot.cogs.errors")
        if isinstance(self, commands.AutoShardedBot):
            _cogs.append("shards")
        self.footer = "بوت فاذكروني لإحياء سنة ذكر الله"
        self.support_url = "https://discord.gg/q3E6WCSThX"
        self.color = config.Color()
        self.version = "`V2.1`"
        self.add_check(self.check_blacklist)
        self.config = config
        self._cogs = _cogs

    @staticmethod
    def check_blacklist(ctx):
        return db.BlackListUser(ctx.author).check

    @staticmethod
    def get_color(table: tuple):
        return discord.Colour.from_rgb(*table)

    @staticmethod
    def _get_prefix(bot, msg):
        x = db.Guild(msg.guild)
        if not x.info:
            x.insert()
        prefix = x.info.get("prefix")
        if not prefix:
            prefix = "!"
        return commands.when_mentioned_or(prefix)(bot, msg)

    def _setup(self):
        for i in self._cogs:
            try:
                self.load_extension(f"bot.cogs.{i}")
                print(f"Load {i}")
            except Exception as error:
                print(f"the error is \n{error}")
        self.reload_extension("bot.cogs.errors")

    async def on_ready(self):
        self._setup()
        await self.change_presence(
            activity=discord.Game(name='!help - fdrbot.xyz'),
            status=discord.Status.dnd
        )
        print(f"Name: {self.user.name}\nID: {self.user.id}")

    @staticmethod
    async def _send_webhook(msg):
        re = request("POST", config.webhook_shard, data={"content": msg})
        return re.status_code

    async def on_shard_ready(self, shard_id):
        print(f'`shard {shard_id} is ready`')
        await self._send_webhook("shard %s is ready" % shard_id)

    async def on_shard_disconnect(self, shard_id):
        await self._send_webhook("Shard %s has been disconnect." % shard_id)

    async def on_shard_resumed(self, shard_id):
        await self._send_webhook("Shard %s has been resumed." % shard_id)

    async def on_guild_join(self, guild):
        x = db.Guild(guild)
        x.insert()
        embed = discord.Embed(title="add guild", color=0x46FF00)
        embed.add_field(name='name guild: ', value="%s (`%s`)" % (guild.name, guild.id), inline=False)
        embed.add_field(name='member guild: ', value=str(guild.member_count), inline=False)
        embed.add_field(name='owner guild: ', value="%s (`%s`)" % (
            await self.fetch_user(int(guild.owner_id)), guild.owner_id), inline=False)
        embed.add_field(name='bot server: ', value=f'{len(self.guilds)}', inline=False)
        embed.set_footer(text=guild.name, icon_url=guild.icon_url)
        embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)
        request(
            method="POST",
            url=config.webhook_log,
            json={
                "avatar_url": self.user.avatar.url,
                "embeds": [embed.to_dict()]
            }
        )

    async def on_guild_remove(self, guild):
        x = db.Guild(guild)
        x.insert()
        embed = discord.Embed(title="remove guild", color=0xFF0000)
        embed.add_field(name='name guild: ', value="%s (`%s`)" % (guild.name, guild.id), inline=False)
        embed.add_field(name='member guild: ', value=str(guild.member_count), inline=False)
        embed.add_field(name='owner guild: ', value="%s (`%s`)" % (
            await self.fetch_user(int(guild.owner_id)), guild.owner_id), inline=False)
        embed.add_field(name='bot server: ', value=f'{len(self.guilds)}', inline=False)
        embed.set_footer(text=guild.name, icon_url=guild.icon_url)
        embed.set_author(name=self.user.name, icon_url=self.user.avatar.url)
        request(
            method="POST",
            url=config.webhook_log,
            json={
                "avatar_url": self.user.avatar.url,
                "embeds": [embed.to_dict()]
            }
        )

    def run(self):
        super().run(config.token)
