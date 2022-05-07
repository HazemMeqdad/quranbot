import asyncio
import logging
import typing as t
import hikari
from bot import database


logger = logging.getLogger("bot.manger.tasks")

class Manger:
    def __init__(self, guilds: t.List[hikari.GatewayGuild], rest: hikari.api.RESTClient, bot: t.Optional[hikari.OwnUser], db: database.DB) -> None:
        self.index = 0
        self.rest = rest
        self.guilds = guilds
        self.bot = bot
        self.db: database.DB = db

    def webhook_object_to_url(self, webhook: hikari.PartialWebhook) -> str:
        return f"https://discord.com/api/webhooks/{webhook.id}/{webhook.token}"

    async def get_webhook_or_fetch(self, channel: hikari.GuildChannel, guild_data: database.Guild) -> hikari.IncomingWebhook:
        webhook = guild_data.webhook_url
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
                webhook = self.webhook_object_to_url(webhook)
            self.db.update_guild(guild_data, database.GuildUpdateType.webhook_url, webhook)
        return webhook

    async def make_task(self, guild: hikari.Guild):
        try:
            data = self.db.fetch_guild(guild.id)
            if not data:
                data = self.db.insert(guild.id)
            assert data.channel
            channel = guild.get_channel(data.channel)
            assert channel
            if data.anti_spam:
                channel_history = await self.rest.fetch_messages(channel.id)
                if channel_history[0].webhook_id == webhook.id: 
                    return
            zker = self.db.get_random_zker().content
            webhook = await self.get_webhook_or_fetch(channel, data)
            if data.embed:
                embed = (
                    hikari.Embed(
                        description=zker,
                        color=0xffd430
                    )
                    .set_footer("بوت فاذكروني لإحياء سنة ذكر الله", icon=self.bot.avatar_url.url)
                    .set_thumbnail(self.bot.avatar_url.url)
                )
            try:
                await self.rest.execute_webhook(
                    webhook=webhook, 
                    token=webhook.token,
                    username="فاذكروني",
                    avatar_url=self.bot.avatar_url.url,
                    **{"content": f"> {zker}"} if not data.embed else {"embed": embed}
                )
                return True
            except (hikari.NotFoundError, hikari.UnauthorizedError):
                return
        except AssertionError: return

    async def start(self, timer: t.Union[int, float]) -> None:
        logger.info("[Task] Started with timer: %s", timer)
        count = 0
        for guild in self.guilds:
            task = await self.make_task(guild)
            if task:
                count += 1
            await asyncio.sleep(.3)
        logger.info("[Task] Ended with timer: %s, counts: %s", timer, count)
