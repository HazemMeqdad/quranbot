import asyncio
import logging
import typing as t
import hikari
import lightbulb
from bot import database
from bot.database.objects import GuildUpdateType
from datetime import datetime


logger = logging.getLogger("bot.manger.tasks")

class Manger:
    def __init__(self, bot: lightbulb.BotApp, guilds: t.Sequence[hikari.Guild]):
        self.bot = bot
        self.rest = self.bot.rest
        self.db: database.DB = self.bot.db
        self.guilds = guilds

    async def make_task(self, guild: hikari.Guild):
        data = self.db.fetch_guild(guild if isinstance(guild, int) else guild.id)
        if data:
            self.db.insert(guild.id)
            return
        if not data.channel_id or not self.bot.cache.get_guild_channel(data.channel_id) or not data.webhook:
            self.db.update_guild(data, GuildUpdateType.channel_id, None)
            self.db.update_guild(data, GuildUpdateType.webhook, None)
            return
        zker = self.db.get_random_zker().content
        if data.embed:
            embed = (
                hikari.Embed(
                    description=zker,
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
                **{"content": f"> {zker}"} if not data.embed else {"embed": embed}
            )
        except (hikari.NotFoundError, hikari.UnauthorizedError):
            self.db.update_guild(data, GuildUpdateType.channel_id, None)
            self.db.update_guild(data, GuildUpdateType.webhook, None)
        except (hikari.RateLimitedError, hikari.RateLimitTooLongError):
            return
        
        next_zker = datetime.fromtimestamp(datetime.now().timestamp() + data.time)
        self.db.update_guild(data, GuildUpdateType.next_zker, next_zker)

    async def start(self) -> None:
        for guild in self.guilds:
            await self.make_task(guild)
