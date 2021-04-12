import random
from discord.ext import commands
from discord.ext import tasks
import db
from config import all


class Send(commands.Cog):
    def __init__(self, client):
        self.client = client

    @tasks.loop(minutes=2)
    async def sender(self):
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
            new_time = db.get_timer(guild) - 120
            db.edit_time(guild, new_time)
            db.commit()
            if db.get_timer(guild) < 0:
                try:
                    await channel.send(random.choice(all))
                except:
                    continue
                else:
                    db.rev_timer(guild)

    @commands.Cog.listener()
    async def on_ready(self):
        print('`tasks has been ready`')
        self.sender.start()


def setup(client):
    client.add_cog(Send(client))
