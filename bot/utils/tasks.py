from __future__ import annotations
import logging
import hikari
import asyncio
import time as ti
from lightbulb.app import BotApp
import tasks
from requests import request
from bot.database import Guild


webhook_cache = {}


async def send_for_guild(bot: BotApp, guild: Guild, cache_guild):

    channel = cache_guild.get_channel(guild.channel_id)

    if not channel:
        return
    
    webhook = webhook_cache.get(guild.id)

    if not webhook:
        channel_webhooks = await bot.rest.fetch_channel_webhooks(channel.id)
        webhooks = [i for i in channel_webhooks if i.name ==  bot.get_me().username]
        webhook = webhooks[0] if webhooks else None
        webhook_cache[guild.id] == webhook

    if not webhook:
        webhook = await bot.rest.create_webhook(channel.id, bot.get_me().username)
        webhook_cache[guild.id] == webhook    

    if guild.anti_spam:
        channel_history = await bot.rest.fetch_messages(channel.id)
        if channel_history[0].webhook_id == webhook.id:
            return

    random_zker = bot.db.get_random_zker()

    if guild.embed:
        embed = (
            hikari.Embed( description=random_zker.content, color=0xffd430)
            .set_footer("بوت فاذكروني لإحياء سنة ذكر الله", icon=bot.get_me().avatar_url.url)
            .set_thumbnail(bot.get_me().avatar_url)
        )
        return await webhook.execute(embed=embed)

    return await webhook.execute(
        f"> {random_zker.content}", 
        username=bot.get_me().username, 
        avatar_url=bot.get_me().avatar_url.url
    )

async def create_task_send(bot: BotApp, time: int):
    global is_runing
    while is_runing:

        start = ti.monotonic()
        guilds: list[Guild] = bot.db.get_all_channels_by_time(bot, time)
        counter = 0

        logging.info(f"Task {time} has been started, sender planning in {len(guilds)}")

        for guild in guilds:

            cache_guild = bot.cache.get_available_guild(guild.id)

            if cache_guild:

                x = await send_for_guild(bot, guild, cache_guild)
                print(x)
                counter += 1 if x else ...

        logging.info(
            f"Task {time} finished, has been send in {counter} guilds timeit {ti.monotonic() - start}")
        await asyncio.sleep(float(time))


_tasks: list[tasks.Task] = []


async def create_tasks(bot: BotApp):
    times = [1800, 3600, 7200, 21600, 43200, 86400]
    # await bot.wait_for(hikari.InteractionCreateEvent, timeout=None)
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
