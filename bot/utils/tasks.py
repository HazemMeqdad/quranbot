from __future__ import annotations
import logging
import hikari
from hikari import ForbiddenError, RateLimitedError
import asyncio
import time as ti
import tasks


async def send_for_guild(bot, guild):
    cache = bot.cache
    _guild = cache.get_available_guild(guild.id)
    if not guild:
        return 
    channel = _guild.get_channel(guild.channel_id)
    if not channel or not _guild:
        return
    try:
        webhooks = await bot.rest.fetch_channel_webhooks(guild.channel_id)
    except ForbiddenError:
        return
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
        if guild.anti_spam and channel_history[0].webhook_id == webhook.id:
            return
    random_zker = bot.db.get_random_zker()
    content = f"> {random_zker.content}"
    data = {
        "username": bot.get_me().username,
        "avatar_url": bot.get_me().avatar_url.url
    }
    if guild.embed:
        embed = hikari.Embed(
            description=random_zker.content,
            color=0xffd430
        )
        embed.set_footer(
            text="بوت فاذكروني لإحياء سنة ذكر الله", icon=bot.get_me().avatar_url)
        embed.set_thumbnail(bot.get_me().avatar_url)
        await webhook.execute(embed=embed, **data)
        return 1
    await webhook.execute(content=content, **data)
    return 1

async def create_task_send(bot, time: int):
    global is_runing
    while is_runing:
        tasks = []
        start = ti.monotonic()
        guilds = bot.db.get_all_channels_by_time(bot, time)
        for guild in guilds:
            tasks.append(asyncio.ensure_future(send_for_guild(bot, guild)))
        results = await asyncio.gather(*tasks)  # to make fast send
        send_count = len([i for i in results if i == 1])
        logging.info(
            f"Task {time} finished, has been send in {send_count} guilds timeit {ti.monotonic() - start}")
        await asyncio.sleep(float(time))


_tasks: list[tasks.Task] = []


def create_tasks(bot):
    times = [1800, 3600, 7200, 21600, 43200, 86400]      
    for time in times:
        task = tasks.Task(create_task_send, intervel=time)
        task.start(bot, time)
        _tasks.append(task)

is_runing = True

def stop_tasks():
    global is_runing
    is_runing = False
    for task in _tasks:
        task.cancel()
