import discord
from discord.ext import commands, tasks
from bot import db
from datetime import datetime


class Shards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_shards.start()

    def unload(self):
        self.update_shards.cancel()

    @tasks.loop(minutes=1)
    async def update_shards(self):
        # https://github.com/Xenon-Bot/xenon/blob/master/xenon/cogs/sharding.py#L12
        latencies = self.bot.latencies
        if len(self.bot.shards) == 0:
            return
        shards = {id: {
            "latency": round(latency * 1000),
            "guilds": 0,
            "users": 0,
            "seen": datetime.now().timestamp()
        } for id, latency in latencies}
        for guild in self.bot.guilds:
            try:
                shards[guild.shard_id]["guilds"] += 1
                shards[guild.shard_id]["users"] += guild.member_count
            except:
                pass
        for id, shard in shards.items():
            db.Shards(id, data=shard).update()

    @update_shards.before_loop
    async def before_update_shards(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Shards(bot))

