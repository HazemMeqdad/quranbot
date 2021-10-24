from __future__ import annotations
from typing import Any
from discord.ext import tasks
import hikari
from hikari.api.rest import RESTClient
# from bot.db.db import get_all_channels_by_time, Azkar


async def sender_task(rest: RESTClient, time: int | float):
    guilds = get_all_channels_by_time(time)
    
    for _ in guilds:
        try:
            guild = await rest.fetch_guild(_["_id"])
        except hikari.NotFoundError:
            continue
        channel = guild.get_channel(_["channel"])
        if not channel:
            continue
        try:
            webhooks = await rest.fetch_channel_webhooks(_["channel"])
        except hikari.errors.ForbiddenError:
            continue
        bot = await rest.fetch_my_user()
        webhooks = [i for i in webhooks if i.name == bot.username and i.avatar_url == bot.avatar_url]
        webhook = webhooks[0] if webhooks else None
        if not webhook:
            webhook = await rest.create_webhook(channel.id, bot.username, avatar=bot.avatar_url)
        channel_history = await rest.fetch_messages(channel.id)
        if _["anti_spam"] and channel_history[-1].webhook_id == webhook.id:
            return
        random_zker = Azkar().random["msg"]
        content = f"> {random_zker}"
        embed = None
        if _["embed"]:
            embed = hikari.Embed(
                description=random_zker,
                color=0xffd430
            )
            embed.set_footer(text="بوت فاذكروني لإحياء سنة ذكر الله", icon=bot.avatar_url)
            embed.set_thumbnail(bot.avatar_url)
        if embed:
            await webhook.execute(embed=embed, username=bot.username, avatar_url=bot.avatar_url)
            continue
        await webhook.execute(content=content, username=bot.username, avatar_url=bot.avatar_url)

class Loop(tasks.Loop):
    def __init__(
            self, 
            coro, 
            seconds: int | float = 0, 
            hours: int | float = 0, 
            minutes: int | float = 0, 
            count: Any = None, 
            reconnect: bool = True, 
        ):
        super().__init__(coro, seconds, hours, minutes, count, reconnect, True)




