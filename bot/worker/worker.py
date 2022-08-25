import logging
import typing as t
import hikari
import lightbulb
from bot import database
from bot.database.objects import GuildUpdateType
from datetime import datetime
from lightbulb.ext import tasks
from .task import Task
if t.TYPE_CHECKING:
    from bot.bot import Bot

_LOGGER = logging.getLogger("bot.worker.worker")


@tasks.task(s=10, max_consecutive_failures=0, pass_app=True, cls=Task)
async def worker(bot: "Bot") -> None:
    cache_guilds = filter(lambda guild: isinstance(guild, hikari.Guild), bot.cache.get_guilds_view().values())
    db_guilds = bot.db.fetch_guilds_with_datetime()
    guild_ids = [i.id for i in db_guilds]
    guilds = list(filter(lambda x: x.id in guild_ids, list(cache_guilds)))
    worker_ = Worker(bot, guilds[:3])
    await worker_.run()


class Worker:
    def __init__(self, bot: "Bot", guilds: t.List[hikari.Guild]) -> None:
        self.bot = bot
        self.rest = self.bot.rest
        self.db: database.DB = self.bot.db
        self.guilds = guilds

    async def send(self, guild: hikari.Guild):
        data = self.db.fetch_guild(guild if isinstance(guild, int) else guild.id)
        if not data:
            self.db.insert(guild.id)
            return
        next_zker = datetime.fromtimestamp(datetime.now().timestamp() + data.time)
        self.db.update_guild(data, GuildUpdateType.next_zker, next_zker)
        if not self.bot.cache.get_guild_channel(data.channel_id):
            self.db.update_guild(data, GuildUpdateType.channel_id, None)
            self.db.update_guild(data, GuildUpdateType.webhook, None)
            return
        pray = self.db.get_random_zker().content
        if data.embed:
            embed = (
                hikari.Embed(
                    description=pray,
                    color=0xffd430
                )
                .set_footer(self.bot.footer, icon=self.bot.get_me().avatar_url.url)
                .set_thumbnail(self.bot.get_me().avatar_url.url)
            )
        try:
            await self.rest.execute_webhook(
                webhook=data.webhook["id"], 
                token=data.webhook["token"],
                username="فاذكروني",
                avatar_url=self.bot.get_me().avatar_url.url,
                **{"content": f"> {pray}"} if not data.embed else {"embed": embed}
            )
        except (hikari.NotFoundError, hikari.UnauthorizedError):
            self.db.update_guild(data, GuildUpdateType.channel_id, None)
            self.db.update_guild(data, GuildUpdateType.webhook, None)
        except (hikari.RateLimitedError, hikari.RateLimitTooLongError):
            return

    async def run(self) -> None:
        for guild in self.guilds:
            await self.send(guild)


def load(bot: lightbulb.BotApp) -> None:
    _LOGGER.info("[ Worker ] worker has been starting")
    worker.start()
    
def unload(bot: lightbulb.BotApp) -> None:
    _LOGGER.info("[ Worker ] worker has been stopping")
    worker.cancel()
