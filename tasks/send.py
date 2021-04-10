import random
from discord.ext import commands
from discord.ext import tasks
import db
from config import all
import time

limet = 0


class Send(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.limet = 0

    @tasks.loop(minutes=1)
    async def sender(self):
        if self.limet == 0:
            self.limet += 1
            return
        start = time.monotonic()
        for i in db.get_all_channels():
            channel_id = i[1]
            guild_id = i[0]
            if channel_id == None:
                continue
            channel = self.client.get_channel(channel_id)
            guild = self.client.get_guild(guild_id)
            if channel == None:
                continue
            if guild == None:
                continue
            try:
                message = await channel.fetch_message(channel.last_message_id)
                if db.get_spam(guild):
                    if message.author == self.client.user:
                        continue
            except:
                continue
            new_time = db.get_timer(guild) - 60
            db.edit_time(guild, new_time)
            db.commit()
            if db.get_timer(guild) < 0:
                try:
                    await channel.send(random.choice(all))
                except:
                    continue
                else:
                    db.rev_timer(guild)
        print('---------------------------')
        print(time.monotonic() - start)
        print('---------------------------')

    @commands.Cog.listener()
    async def on_ready(self):
        print('`tasks has been ready`')
        self.sender.start()


def setup(client):
    client.add_cog(Send(client))
