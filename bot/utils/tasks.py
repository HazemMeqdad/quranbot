import typing as t
import hikari
import lightbulb
from bot.database.objects import Guild

cahce_webhooks: t.Dict[int, hikari.PartialWebhook] = {}

class Tasks:
    def __init__(self, bot: lightbulb.BotApp) -> None:
        self.index = 0
        self.bot = bot
        guilds = self.bot.cache.get_available_guilds_view().values()
        self.guilds = self.partition([i for i in guilds if i.member_count >= 10], 4)

    def _partition(self, lst, size):
        for i in range(0, len(lst), size):
            yield lst[i : i+size]

    def partition(self, lst, size) -> t.List[t.List[hikari.Guild]]:
        return list(self._partition(lst, size))

    @property
    def get_guilds(self) -> t.List[hikari.Guild]:
        return self.guilds[self.index]

    async def get_webhook_or_fetch(self, guild: hikari.Guild, channel: hikari.GuildChannel) -> hikari.IncomingWebhook:
        cahce_webhooks.get(guild.id, None)
        if not webhook:
            webhooks = await self.bot.rest.fetch_channel_webhooks(channel)
            webhook = [i for i in webhooks if i.name == "فاذكروني"]
            webhook = webhook[0] if webhook else None
            if not webhook:
                webhook = await self.bot.rest.create_webhook(
                    channel=channel, 
                    name="فاذكروني", 
                    avatar=self.bot.get_me().avatar_url.url
                )
            cahce_webhooks[guild.id] = webhook
        return webhook

    async def thirty_minutes(self, guilds: t.List[hikari.Guild]):
        for guild in guilds:
            data: Guild = self.bot.db.fetch_guild(guild.id)
            assert data.channel_id != None
            channel = guild.get_channel(data.channel_id)
            if not channel:
                continue
            if guild.anti_spam:
                channel_history = await self.bot.rest.fetch_messages(channel.id)
                if channel_history[0].webhook_id == webhook.id:
                    continue
            zker = self.bot.db.get_random_zker().content
            webhook = await self.get_webhook_or_fetch(guild, channel)
            if data.embed:
                embed = (
                    hikari.Embed(
                        description=zker,
                        color=0xffd430
                    )
                    .set_footer("بوت فاذكروني لإحياء سنة ذكر الله", icon=self.bot.get_me().avatar_url.url)
                    .set_thumbnail(self.bot.get_me().avatar_url.url)
                )
            await self.bot.rest.execute_webhook(
                webhook=webhook, 
                token=webhook.token,
                username="فاذكروني",
                avatar_url=self.bot.get_me().avatar_url.url,
                **{"content": f"> {zker}"} if not data.embed else {"embed": embed}
            )
