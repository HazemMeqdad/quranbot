import discord
from discord.ext import commands, tasks
import json


class Shards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base = "bot/data/data.json"
        self.update_shards.start()

    async def update_data(self, shard: str, guilds_count: int):
        with open(self.base, "r") as file:
            shards = json.load(file)
        shards[str(shard)] = guilds_count
        with open(self.base, "w") as file:
            json.dump(shards, file, indent=4)

    @tasks.loop(minutes=1)
    async def update_shards(self):
        shards = {}
        for guild in self.bot.guilds:
            shard = self.bot.get_shard(guild.shard_id)
            print(shard)
            shards[str(shard.id+1)] += 1
        print(shards)
        for shard_id, guilds_count in shards.items():
            await self.update_data(shard=shard_id, guilds_count=guilds_count)

    @update_shards.before_loop
    async def before_update_shards(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Shards(bot))

