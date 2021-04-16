import random
from discord.ext import commands
from discord.ext import tasks
import db
from config import all
import discord
import time


class Send(commands.Cog):
    def __init__(self, client):
        self.client = client

    @tasks.loop(minutes=2)
    async def sender(self):
        for i in db.get_all_channels():
            channel_id = i[1]
            guild_id = i[0]
            channel = self.client.get_channel(channel_id)
            guild = self.client.get_guild(guild_id)
            if guild is None:
                db.delete_guild(guild_id)
                continue
            if channel is None:
                db.remove_channel(guild)
                continue
            new_time = db.get_timer(guild) - 120
            db.edit_time(guild, new_time)

    @tasks.loop(minutes=2)
    async def sender2(self):
        for i in db.get_all_channels():
            channel_id = i[1]
            guild_id = i[0]
            timer = i[2]
            channel = self.client.get_channel(channel_id)
            guild = self.client.get_guild(guild_id)

            if timer <= 0:
                try:
                    message = await channel.fetch_message(channel.last_message_id)
                    if db.get_spam(guild):
                        if message.author == self.client.user:
                            continue
                except discord.NotFound:
                    pass
                except discord.HTTPException:
                    pass
                try:
                    if db.get_embed(guild):
                        await channel.send(embed=discord.Embed(
                            description=random.choice(all),
                            color=discord.Color.gold()
                        ).set_footer(text=self.client.user.name, icon_url=guild.icon_url))
                        db.rev_timer(guild)
                        continue
                    await channel.send(random.choice(all))
                    db.rev_timer(guild)
                    continue
                except:
                    db.remove_channel(guild)
                    continue

    @commands.Cog.listener()
    async def on_ready(self):
        print('`tasks has been ready`')
        self.sender.start()
        self.sender2.start()


def setup(client):
    client.add_cog(Send(client))
