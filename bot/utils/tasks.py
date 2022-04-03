import asyncio
import logging
import typing as t
import hikari
from bot.database import DB

cahce_webhooks: t.Dict[int, hikari.PartialWebhook] = {}

logger = logging.getLogger(__name__)

class Tasks:
    def __init__(self, guilds: t.List[hikari.GatewayGuild], rest: hikari.api.RESTClient, bot: t.Optional[hikari.OwnUser], db: DB) -> None:
        self.index = 0
        self.rest = rest
        self.guilds = self.partition([i for i in guilds if i.member_count >= 10], 4)
        self.bot = bot
        self.db = db

    def _partition(self, lst, size):
        for i in range(0, len(lst), size):
            yield lst[i : i+size]

    def partition(self, lst, size) -> t.List[t.List[hikari.GatewayGuild]]:
        return list(self._partition(lst, size))

    @property
    def get_guilds(self) -> t.Optional[t.List[hikari.GatewayGuild]]:
        self.index += 1
        if self.index >= self.guilds.__len__():
            self.guilds = self.partition([i for i in self.guilds if i.member_count >= 10], 4)
            self.index = 0 
        if self.guilds.__len__() != 0:
            return self.guilds[self.index]
        else : 
            return []

    async def get_webhook_or_fetch(self, guild: hikari.GatewayGuild, channel: hikari.GuildChannel) -> hikari.IncomingWebhook:
        webhook = cahce_webhooks.get(guild.id, None)
        if not webhook:
            webhooks = await self.rest.fetch_channel_webhooks(channel)
            webhook = [i for i in webhooks if i.name == "فاذكروني"]
            webhook = webhook[0] if webhook else None
            if not webhook:
                webhook = await self.rest.create_webhook(
                    channel=channel, 
                    name="فاذكروني", 
                    avatar=self.bot.avatar_url.url
                )
            cahce_webhooks[guild.id] = webhook
        return webhook

    async def thirty_minutes(self, guilds: t.List[hikari.Guild]):
        for guild in guilds:
            try:
                data = self.db.fetch_guild(guild.id)
                if not data:
                    data = self.db.insert(guild.id)
                assert data.channel
                channel = guild.get_channel(data.channel)
                assert channel
                if data.anti_spam:
                    channel_history = await self.rest.fetch_messages(channel.id)
                    if channel_history[0].webhook_id == webhook.id: continue
                zker = self.db.get_random_zker().content
                webhook = await self.get_webhook_or_fetch(guild, channel)
                if data.embed:
                    embed = (
                        hikari.Embed(
                            description=zker,
                            color=0xffd430
                        )
                        .set_footer("بوت فاذكروني لإحياء سنة ذكر الله", icon=self.bot.avatar_url.url)
                        .set_thumbnail(self.bot.avatar_url.url)
                    )
                await self.rest.execute_webhook(
                    webhook=webhook, 
                    token=webhook.token,
                    username="فاذكروني",
                    avatar_url=self.bot.avatar_url.url,
                    **{"content": f"> {zker}"} if not data.embed else {"embed": embed}
                )
            except AssertionError: ...

    async def start(self) -> None:
        logger.info("[Tasks] Started")
        while self.index >= self.guilds.__len__():
            await self.thirty_minutes(self.get_guilds)
            await asyncio.sleep(60)
        logger.info("[Tasks] Dened, indexs: %s", self.index)
