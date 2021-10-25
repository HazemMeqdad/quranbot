from __future__ import annotations
import logging
import hikari
import threading
from hikari import ForbiddenError
import asyncio
from lightbulb import Bot


async def _sender_task(bot: Bot, time: int):
    guilds = bot.db.get_all_channels_by_time(bot, time)
    cache = bot.cache
    global stop_threads
    while stop_threads:
        await asyncio.sleep(time)
        send_count = 0
        for _guild in guilds:
            guild = cache.get_guild(_guild.id)
            if not guild:
                continue
            channel = guild.get_channel(_guild.channel_id)
            if not channel:
                continue
            try:
                webhooks = await bot.rest.fetch_channel_webhooks(_guild.channel_id)
            except ForbiddenError:
                continue
            webhooks = [i for i in webhooks if i.name == bot.get_me().username]
            webhook = webhooks[0] if webhooks else None
            if not webhook:
                webhook = await bot.rest.create_webhook(
                    channel=channel.id, 
                    name=bot.get_me().username, 
                    avatar=bot.get_me().avatar_url
                )
            channel_history = await bot.rest.fetch_messages(channel.id)
            if _guild.anti_spam and channel_history[-1].webhook_id == webhook.id:
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
        logging.info(f"Task {time} finished, send in {send_count} guilds")

_tasks: list[threading.Thread] = []


async def create_tasks(bot: Bot):
    times = [1800, 3600, 7200, 21600, 43200, 86400]    
    for time in times:        
        x = threading.Thread(target=asyncio.run, args=(_sender_task(bot, time),))
        x.start()
        _tasks.append(x)

stop_threads = False

def stop_tasks():
    stop_threads = True
    for task in _tasks:
        task.join()
