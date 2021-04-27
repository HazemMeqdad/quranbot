import random
from discord.ext import commands
import db
from config import all
import discord
import time
import asyncio

t = True


def send(status: bool):
    if status:
        t = True
        return
    t = False


class Send(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def send(self):
        start = time.monotonic()
        while t:
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
                            if message.author.id == 728782652454469662:
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
            end = time.monotonic()
            timer = end - start
            if timer >= 0:
                continue
            await asyncio.sleep(120 - int(timer))

    @commands.command(name='status')
    @commands.is_owner()
    async def status(self, ctx, status=None):
        if status is None:
            await ctx.send(t)
            return
        if status == 'off':
            send(False)
            await ctx.send('تم ايقاف الاذكار')
            return
        elif status == "on":
            send(True)
            await ctx.send('تم تفعل ارسال الاذكار')
            return
        elif status == "restart":
            send(True)
            send(False)
            await ctx.send('تم اعاده تشغيل الاذكار')
            return
        elif status == 'start':
            await self.send()
            await ctx.send('تم بدء ارسال الاذكار')
        else:
            await ctx.send('يجب اختيار احد الخيارات التاليه [on, off, restart]')
            return

    @commands.Cog.listener()
    async def on_ready(self):
        print('`tasks has been ready`')


def setup(client):
    client.add_cog(Send(client))
