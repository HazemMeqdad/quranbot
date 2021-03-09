import random, time
from discord.ext import commands
from discord.ext import tasks
from db.db import *
from config import all
import datetime


class Send(commands.Cog):
    def __init__(self, client):
        self.client = client

    @tasks.loop(minutes=30.0)
    async def half_an_hour(self):
        date = cr.execute("SELECT channel FROM channels").fetchall()
        # print(date)
        for i in date:
            if i is None:
                continue
            guild_time = cr.execute("SELECT date_time FROM channels WHERE channel = ?", (i[0],))
            if guild_time != "0.5":
                continue
            _channel = self.client.get_channel(i[0])
            try:
                if _channel is None:
                    continue
                await _channel.send(random.choice(all))
            except:
                pass

    @tasks.loop(hours=1.0)
    async def one_hour(self):
        date = cr.execute("SELECT channel FROM channels").fetchall()
        for i in date:
            if i is None:
                continue
            guild_time = cr.execute("SELECT date_time FROM channels WHERE channel = ?", (i[0],))
            if guild_time != "1":
                continue
            _channel = self.client.get_channel(i[0])
            try:
                if _channel is None:
                    continue
                await _channel.send(random.choice(all))
            except:
                pass

    @tasks.loop(hours=2.0)
    async def two_hour(self):
        date = cr.execute("SELECT channel FROM channels").fetchall()
        for i in date:
            if i is None:
                continue
            guild_time = cr.execute("SELECT date_time FROM channels WHERE channel = ?", (i[0],))
            if guild_time != "2":
                continue
            _channel = self.client.get_channel(i[0])
            try:
                if _channel is None:
                    continue
                await _channel.send(random.choice(all))
            except:
                pass

    @tasks.loop(hours=6.0)
    async def six_hour(self):
        date = cr.execute("SELECT channel FROM channels").fetchall()
        for i in date:
            if i is None:
                continue
            guild_time = cr.execute("SELECT date_time FROM channels WHERE channel = ?", (i[0],))
            if guild_time != "6":
                continue
            _channel = self.client.get_channel(i[0])
            try:
                if _channel is None:
                    continue
                await _channel.send(random.choice(all))
            except:
                pass

    @tasks.loop(hours=12.0)
    async def twelve_hour(self):
        date = cr.execute("SELECT channel FROM channels").fetchall()
        for i in date:
            if i is None:
                continue
            guild_time = cr.execute("SELECT date_time FROM channels WHERE channel = ?", (i[0],))
            if guild_time != "12":
                continue
            _channel = self.client.get_channel(i[0])
            try:
                if _channel is None:
                    continue
                await _channel.send(random.choice(all))
            except:
                pass

    @tasks.loop(hours=24.0)
    async def day(self):
        date = cr.execute("SELECT channel FROM channels").fetchall()
        for i in date:
            if i is None:
                continue
            guild_time = cr.execute("SELECT date_time FROM channels WHERE channel = ?", (i[0],))
            if guild_time != "24":
                continue
            _channel = self.client.get_channel(i[0])
            try:
                if _channel is None:
                    continue
                await _channel.send(random.choice(all))
            except:
                pass

    @tasks.loop(seconds=10)
    async def del_cooldown(self):
        if get_cooldown() == []:
            return
        cr.execute("DELETE FROM cooldown")
        commit()

    @commands.Cog.listener()
    async def on_ready(self):
        self.half_an_hour.start()

        self.one_hour.start()
        self.two_hour.start()
        self.six_hour.start()
        self.twelve_hour.start()
        self.day.start()

        self.del_cooldown.start()
        # self.restart_program.start()
        print("The Tasks is online")


def setup(client):
    client.add_cog(Send(client))
