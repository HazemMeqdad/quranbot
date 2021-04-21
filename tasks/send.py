import random
from discord.ext import commands
from discord.ext import tasks
import db
from config import all
import discord
import time
import asyncio


class Send(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def send(self):
        start = time.monotonic()
        while True:
            for i in db.get_all_channels():
                guild_id = i[0]
                channel_id = i[1]
                timer = i[2]
                guild = self.client.get_guild(guild_id)
                channel = self.client.get_channel(channel_id)
                if guild is None:
                    db.delete_guild(guild_id)
                    continue
                if channel is None:
                    db.remove_channel(guild)
                    continue
                new_time = timer - 120
                db.edit_time(guild, new_time)
                if new_time >= 0:
                    if db.get_spam(guild):
                        try:
                            message = await channel.fetch_message(channel.last_message_id)
                            if message.author.id == self.client.user.id:
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
                        db.remove_channel(guild)
            await asyncio.sleep(120)

    # @tasks.loop(minutes=2)
    # async def sender(self):
    #     for i in db.get_all_channels():
    #         channel_id = i[1]
    #         guild_id = i[0]
    #         channel = self.client.get_channel(channel_id)
    #         guild = self.client.get_guild(guild_id)
    #         if guild is None:
    #             db.delete_guild(guild_id)
    #             continue
    #         if channel is None:
    #             db.remove_channel(guild)
    #             continue
    #         new_time = db.get_timer(guild) - 120
    #         db.edit_time(guild, new_time)

    # @tasks.loop(minutes=2)
    # async def sender2(self):
    #     for i in db.get_all_channels():
    #         channel_id = i[1]
    #         guild_id = i[0]
    #         timer = i[2]
    #         channel = self.client.get_channel(channel_id)
    #         guild = self.client.get_guild(guild_id)
    #         if timer <= 0:
    #             try:
    #                 message = await channel.fetch_message(channel.last_message_id)
    #                 if db.get_spam(guild):
    #                     if message.author == self.client.user:
    #                         continue
    #             except:
    #                 continue
    #             try:
    #                 if db.get_embed(guild):
    #                     await channel.send(embed=discord.Embed(
    #                         description=random.choice(all),
    #                         color=discord.Color.gold()
    #                     ).set_footer(text=self.client.user.name, icon_url=guild.icon_url))
    #                     db.rev_timer(guild)
    #                     continue
    #                 await channel.send(random.choice(all))
    #                 db.rev_timer(guild)
    #                 continue
    #             except:
    #                 db.remove_channel(guild)
    #                 continue

    @commands.Cog.listener()
    async def on_ready(self):
        # await self.sender.start()
        # await self.sender2.start()
        print('`tasks has been ready`')
        await self.send()


def setup(client):
    client.add_cog(Send(client))
