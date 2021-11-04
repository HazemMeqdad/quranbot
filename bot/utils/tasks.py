from __future__ import annotations
import logging
import hikari
from hikari import ForbiddenError, RateLimitedError
import asyncio
from lightbulb import Bot
import time as ti
import tasks


async def _sender_task(bot: Bot, time: int):
    global is_runing
    while is_runing:
        start = ti.monotonic()
        guilds = bot.db.get_all_channels_by_time(bot, time)
        cache = bot.cache
        send_count = 0
        for _guild in guilds:
            guild = cache.get_available_guild(_guild.id)
            if not guild:
                continue
            channel = guild.get_channel(_guild.channel_id)
            if not channel:
                continue
            try:
                webhooks = await bot.rest.fetch_channel_webhooks(_guild.channel_id)
            except ForbiddenError:
                continue
            except RateLimitedError as rate_limit:
                asyncio.sleep(float(rate_limit.retry_after))
            webhooks = [i for i in webhooks if i.name == bot.get_me().username]
            webhook = webhooks[0] if webhooks else None
            if not webhook:
                webhook = await bot.rest.create_webhook(
                    channel=channel.id, 
                    name=bot.get_me().username, 
                    avatar=bot.get_me().avatar_url
                )
            channel_history = await bot.rest.fetch_messages(channel.id)
            if channel_history:
                if _guild.anti_spam and channel_history[0].webhook_id == webhook.id:
                    continue
            random_zker = bot.db.get_random_zker()
            content = f"> {random_zker.content}"
            data = {
                "username": bot.get_me().username,
                "avatar_url": bot.get_me().avatar_url.url
            }
            if _guild.embed:
                embed = hikari.Embed(
                    description=random_zker.content,
                    color=0xffd430
                )
                embed.set_footer(text="بوت فاذكروني لإحياء سنة ذكر الله", icon=bot.get_me().avatar_url)
                embed.set_thumbnail(bot.get_me().avatar_url)
                await webhook.execute(embed=embed, **data)
                send_count += 1
                continue
            await webhook.execute(content=content, **data)
            send_count += 1
        logging.info(f"Task {time} finished, send in {send_count} guilds timeit {ti.monotonic() - start}")
        await asyncio.sleep(float(time))


_tasks: list[tasks.Task] = []


def create_tasks(bot: Bot):
    times = [1800, 3600, 7200, 21600, 43200, 86400]      
    for time in times:
        task = tasks.Task(_sender_task, intervel=time)
        _tasks.append(task)

is_runing = True

def stop_tasks():
    global is_runing
    is_runing = False
    for task in _tasks:
        task.cancel()
