from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
from .utlits.database import Database, DbGuild
import aiohttp
import discord
from io import BytesIO

class Tasks(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    async def cog_load(self) -> None:
        self.pray_checker.start()
        self.azan_checker.start()

    async def get_pray(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cdn.fdrbot.com/pray/random") as resp:
                data = await resp.json()
                return data

    async def get_avatar_bot_bytes(self) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.bot.user.avatar.url) as resp:
                data = BytesIO(await resp.read())
                return data

    async def process_guild(self, data: DbGuild):
        db = Database()
        channel = self.bot.get_channel(data.channel_id)
        guild = self.bot.get_guild(data._id)
        pray = await self.get_pray()
        if not channel or not guild or not guild.me.guild_permissions.manage_webhooks:
            db.update_guild(data._id, channel_id=None, webhook=None)
            return
        try:
            hooks = await channel.webhooks()
            hook = discord.utils.get(hooks, name="فاذكروني")
        except (discord.HTTPException, discord.NotFound, discord.Forbidden):
            db.update_guild(data._id, channel_id=None, webhook=None)
        embed = discord.Embed(
            title=pray["id"],
            description=pray["text"],
            color=0xffd430
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="بوت فاذكروني لإحياء سنة ذِكر الله", icon_url=self.bot.user.avatar.url)
        new_datetime = datetime.now().timestamp() + data.time
        db.update_guild(data._id, new_zker=datetime.fromtimestamp(new_datetime))
        if data.embed:
            await hook.send(
                embed=embed, 
                username=self.bot.user.name,
                avatar_url=self.bot.user.avatar.url
            )
            return  
        await hook.send(
            f"> {pray['text']}", 
            username=self.bot.user.name,
            avatar_url=self.bot.user.avatar.url
        )
        
    @tasks.loop(seconds=24)
    async def pray_checker(self):
        await self.bot.wait_until_ready()
        db = Database()
        guilds = db.fetch_guilds_with_datetime()
        for guild in guilds:
            await self.process_guild(guild)

    @tasks.loop(minutes=4)
    async def azan_checker(self):
        ...

async def setup(bot: commands.Bot):
    await bot.add_cog(Tasks(bot))
