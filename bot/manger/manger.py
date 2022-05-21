import asyncio
import logging
import typing as t
import hikari
import lightbulb
from bot import database


logger = logging.getLogger("bot.manger.tasks")

class Manger:
    def __init__(self, timer: t.Union[float, int]) -> None:
        self.index = 0
        self.timer = timer

    async def make_task(self, guild: hikari.Guild):
        try:
            data = self.db.fetch_guild(guild if isinstance(guild, int) else guild.id)
            if not data:
                self.db.insert(guild.id)
                return
            assert data.channel_id
            assert self.bot.cache.get_guild_channel(data.channel_id)
            assert data.webhook
            webhook = await self.bot.rest.fetch_webhook(data.webhook["id"], token=data.webhook["token"])
            assert webhook.channel_id == data.channel_id
            zker = self.db.get_random_zker().content
            if data.embed:
                embed = (
                    hikari.Embed(
                        description=zker,
                        color=0xffd430
                    )
                    .set_footer("بوت فاذكروني لإحياء سنة ذكر الله", icon=self.bot.get_me().avatar_url.url)
                    .set_thumbnail(self.bot.get_me().avatar_url.url)
                )
            await self.rest.execute_webhook(
                webhook=data.webhook["id"], 
                token=data.webhook["token"],
                username="فاذكروني",
                avatar_url=self.bot.get_me().avatar_url.url,
                **{"content": f"> {zker}"} if not data.embed else {"embed": embed}
            )
            return True
        except AssertionError: 
            return

    async def start(self, bot: lightbulb.BotApp) -> None:
        self.bot = bot
        self.rest = self.bot.rest
        self.db: database.DB = self.bot.db
        logger.info("[Task] Started with timer: %s", self.timer)
        count = 0
        cache_guilds = filter(lambda guild: isinstance(guild, hikari.Guild), self.bot.cache.get_guilds_view().values())
        db_guilds = self.db.fetch_guilds_by_time(self.timer)
        guilds = filter(lambda x: x.id in [i.id for i in db_guilds], list(cache_guilds))
        for guild in list(guilds):
            task = await self.make_task(guild)
            if task:
                count += 1
            await asyncio.sleep(.3)
        logger.info("[Task] Ended with timer: %s, counts: %s", self.timer, count)
