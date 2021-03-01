import random, time
from discord.ext import commands
from discord.ext import tasks
from db.db import *
from config import all


class Send(commands.Cog):
    def __init__(self, client):
        self.client = client

    @tasks.loop(minutes=15)
    async def set_message(self):
        channels = []
        date = cr.execute("SELECT channel FROM guilds").fetchall()
        for i in date:
            if i is None:
                continue
            server = i[0]
            channels.append(server)
        else:
            for channel in channels:
                _channel = self.client.get_channel(channel)
                if channel == None:
                    continue
                await _channel.send(random.choice(all))
                # m += 1

                time.sleep(10)
        # print(channels)

    @tasks.loop(seconds=10)
    async def del_cooldown(self):
        if get_cooldown() == []:
            return
        cr.execute("DELETE FROM cooldown")
        commit()

    @commands.Cog.listener()
    async def on_ready(self):
        self.set_message.start()
        self.del_cooldown.start()
        print("The Tasks is online")


def setup(client):
    client.add_cog(Send(client))
