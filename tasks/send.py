import random
from discord.ext import commands, tasks
import db
from config import all
import discord


class Send(commands.Cog):
    def __init__(self, client):
        self.client = client

    @tasks.loop(minutes=30)
    async def send_30m(self):
        for i in db.get_all_channels():
            guild_id = i[0]
            channel_id = i[1]
            time = i[2]
            guild = self.client.get_guild(guild_id)
            channel = self.client.get_channel(channel_id)
            if guild is None:
                continue
            if channel is None:
                continue
            if time == 1800:
                if db.get_spam(guild):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.client.user:
                            continue
                    except:
                        continue
                try:
                    if db.get_embed(guild):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.client.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(all))
                except:
                    continue

    @tasks.loop(hours=1)
    async def send_1h(self):
        for i in db.get_all_channels():
            guild_id = i[0]
            channel_id = i[1]
            time = i[2]
            guild = self.client.get_guild(guild_id)
            channel = self.client.get_channel(channel_id)
            if guild is None:
                continue
            if channel is None:
                continue
            if time == 3600:
                if db.get_spam(guild):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.client.user:
                            continue
                    except:
                        continue
                try:
                    if db.get_embed(guild):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.client.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(all))
                except:
                    continue

    @tasks.loop(hours=2)
    async def send_2h(self):
        for i in db.get_all_channels():
            guild_id = i[0]
            channel_id = i[1]
            time = i[2]
            guild = self.client.get_guild(guild_id)
            channel = self.client.get_channel(channel_id)
            if guild is None:
                continue
            if channel is None:
                continue
            if time == 7200:
                if db.get_spam(guild):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.client.user:
                            continue
                    except:
                        continue
                try:
                    if db.get_embed(guild):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.client.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(all))
                except:
                    continue

    @tasks.loop(hours=6)
    async def send_6h(self):
        for i in db.get_all_channels():
            guild_id = i[0]
            channel_id = i[1]
            time = i[2]
            guild = self.client.get_guild(guild_id)
            channel = self.client.get_channel(channel_id)
            if guild is None:
                continue
            if channel is None:
                continue
            if time == 21600:
                if db.get_spam(guild):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.client.user:
                            continue
                    except:
                        continue
                try:
                    if db.get_embed(guild):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.client.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(all))
                except:
                    continue

    @tasks.loop(hours=12)
    async def send_12h(self):
        for i in db.get_all_channels():
            guild_id = i[0]
            channel_id = i[1]
            time = i[2]
            guild = self.client.get_guild(guild_id)
            channel = self.client.get_channel(channel_id)
            if guild is None:
                continue
            if channel is None:
                continue
            if time == 43200:
                if db.get_spam(guild):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.client.user:
                            continue
                    except:
                        continue
                try:
                    if db.get_embed(guild):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.client.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(all))
                except:
                    continue

    @tasks.loop(hours=24)
    async def send_24h(self):
        for i in db.get_all_channels():
            guild_id = i[0]
            channel_id = i[1]
            time = i[2]
            guild = self.client.get_guild(guild_id)
            channel = self.client.get_channel(channel_id)
            if guild is None:
                continue
            if channel is None:
                continue
            if time == 86400:
                if db.get_spam(guild):
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author == self.client.user:
                            continue
                    except:
                        continue
                try:
                    if db.get_embed(guild):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.client.user.name, icon_url=guild.icon_url))
                        continue
                    await channel.send(random.choice(all))
                except:
                    continue

    @commands.Cog.listener()
    async def on_ready(self):
        print('`tasks has been ready`')
        self.send_30m.start()
        self.send_1h.start()
        self.send_2h.start()
        self.send_6h.start()
        self.send_12h.start()
        self.send_24h.start()


def setup(client):
    client.add_cog(Send(client))
