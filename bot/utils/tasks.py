from __future__ import annotations
import threading
import time
import hikari
from schedule import every, repeat, run_pending
from bot import Bot
from hikari import ForbiddenError


async def sender_task(bot: Bot, time: int):
    guilds = bot.db.get_all_channels_by_time(bot, time)
    cache = bot.cache

    for _guild in guilds:
        guild = cache.get_guild(_guild)
        if not guild:
            continue
        channel = guild.get_channel(_guild.channel_id)
        if not channel:
            continue
        try:
            webhooks = await bot.rest.fetch_channel_webhooks(_guild.channel_id)
        except ForbiddenError:
            continue
        webhooks = [i for i in webhooks if i.name == bot.get_me().username and i.avatar_url == bot.get_me().avatar_url]
        webhook = webhooks[0] if webhooks else None
        if not webhook:
            webhook = await bot.rest.create_webhook(channel.id, bot.username, avatar=bot.avatar_url)
        channel_history = await bot.rest.fetch_messages(channel.id)
        if _guild.anti_spam and channel_history[-1].webhook_id == webhook.id:
            return
        random_zker = bot.db.get_random_zker()
        content = f"> {random_zker.content}"
        if _guild.embed:
            embed = hikari.Embed(
                description=random_zker.content,
                color=0xffd430
            )
            embed.set_footer(text="بوت فاذكروني لإحياء سنة ذكر الله", icon=bot.avatar_url)
            embed.set_thumbnail(bot.avatar_url)
            await webhook.execute(embed=embed, username=bot.username, avatar_url=bot.avatar_url)
            continue
        await webhook.execute(content=content, username=bot.username, avatar_url=bot.avatar_url)


def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

@repeat(every(1).seconds, "hello")
def lol(text):
    print(text)


@repeat(every(3).seconds)
def hi():
    print("lololol")


x = run_continuously()