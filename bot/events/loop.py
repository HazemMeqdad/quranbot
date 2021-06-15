import random
from discord.ext import tasks
import bot.db as db
import bot.config as config
import discord


class Loop:
    def __init__(self, bot):
        self.bot = bot

    async def start(self):
        print('`events has been ready`')

        self._send_30m.start()
        self._send_1h.start()
        self._send_2h.start()
        self._send_6h.start()
        self._send_12h.start()
        self._send_24h.start()

    @tasks.loop(minutes=30)
    async def _send_30m(self):
        _all = db.All
        for i in _all.get_all_channels():
            guild = self.bot.get_guild(i[0])
            if guild is None:
                continue
            channel = self.bot.get_channel(i[3])
            if channel is None:
                continue
            if i[4] == 1800:
                if bool(i[5]):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.bot.user:
                            continue
                    except:
                        continue
                try:
                    if bool(i[6]):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(config.all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.bot.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(config.all))
                except:
                    continue

    @tasks.loop(hours=1)
    async def _send_1h(self):
        _all = db.All
        for i in _all.get_all_channels():
            guild = self.bot.get_guild(i[0])
            if guild is None:
                continue
            channel = self.bot.get_channel(i[3])
            if channel is None:
                continue
            if i[4] == 3600:
                if bool(i[5]):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.bot.user:
                            continue
                    except:
                        continue
                try:
                    if bool(i[6]):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(config.all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.bot.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(config.all))
                except:
                    continue

    @tasks.loop(hours=2)
    async def _send_2h(self):
        _all = db.All
        for i in _all.get_all_channels():
            guild = self.bot.get_guild(i[0])
            if guild is None:
                continue
            channel = self.bot.get_channel(i[3])
            if channel is None:
                continue
            if i[4] == 7200:
                if bool(i[5]):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.bot.user:
                            continue
                    except:
                        continue
                try:
                    if bool(i[6]):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(config.all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.bot.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(config.all))
                except:
                    continue

    @tasks.loop(hours=6)
    async def _send_6h(self):
        _all = db.All
        for i in _all.get_all_channels():
            guild = self.bot.get_guild(i[0])
            if guild is None:
                continue
            channel = self.bot.get_channel(i[3])
            if channel is None:
                continue
            if i[4] == 21600:
                if bool(i[5]):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.bot.user:
                            continue
                    except:
                        continue
                try:
                    if bool(i[6]):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(config.all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.bot.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(config.all))
                except:
                    continue

    @tasks.loop(hours=12)
    async def _send_12h(self):
        _all = db.All
        for i in _all.get_all_channels():
            guild = self.bot.get_guild(i[0])
            if guild is None:
                continue
            channel = self.bot.get_channel(i[3])
            if channel is None:
                continue
            if i[4] == 43200:
                if bool(i[5]):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.bot.user:
                            continue
                    except:
                        continue
                try:
                    if bool(i[6]):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(config.all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.bot.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(config.all))
                except:
                    continue

    @tasks.loop(hours=24)
    async def _send_24h(self):
        _all = db.All
        for i in _all.get_all_channels():
            guild = self.bot.get_guild(i[0])
            if guild is None:
                continue
            channel = self.bot.get_channel(i[3])
            if channel is None:
                continue
            if i[4] == 86400:
                if bool(i[5]):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.bot.user:
                            continue
                    except:
                        continue
                try:
                    if bool(i[6]):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(config.all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.bot.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(config.all))
                except:
                    continue





