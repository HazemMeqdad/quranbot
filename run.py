import logging
import os
import discord
from discord.app_commands import CommandTree
from discord.ext import commands
import redis.asyncio as aioredis
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    ...
from cogs.general import ZkaatView
from utlits.views import OpenMoshafView
import lavalink
from database import Database

import logging

FMT = "[{levelname:^9}] {name}: {message}"

FORMATS = {
    logging.DEBUG: f"\33[93m{FMT}\33[0m",
    logging.INFO: f"\33[32m{FMT}\33[0m",
    logging.WARNING: f"\33[33m{FMT}\33[0m",
    logging.ERROR: f"\33[31m{FMT}\33[0m",
    logging.CRITICAL: "\33[35m{message}\33[0m",
}

class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_fmt = FORMATS[record.levelno]
        formatter = logging.Formatter(log_fmt, style="{")
        return formatter.format(record)

def setup_logger() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
    )    

cogs = [
    "cogs.general",
    "cogs.voice",
    "cogs.owner",
    "cogs.hadith",
    "cogs.admin",
    "cogs.moshaf",
    "cogs.errors",
    "cogs.hijri",
    "cogs.tafsir",
    "cogs.tasks",
    "cogs.premium",
    "cogs.pray"
]

class Bot(commands.Bot):
    def __init__(self):
        Database.initialize()  # initialize database connection
        super().__init__(
            command_prefix=None,
            owner_ids=[int(i) for i in os.getenv("OWNER_IDS", "").split(",")],
            tree_cls=CommandTree,
            intents=discord.Intents.default(),
            status=discord.Status.dnd,
            activity=discord.Activity(type=discord.ActivityType.playing, name="/help - fdrbot.com"),
            enable_debug_events=True
        )
        
    async def setup_hook(self) -> None:
        self.lavalink = lavalink.Client(self.user.id)
        self.lavalink.add_node(
            os.environ["LAVALINK_NODE_IP"],
            os.environ["LAVALINK_NODE_PORT"],
            os.environ["LAVALINK_NODE_PASSWORD"],
            "us",
            "default-node"
        )
        self.add_view(OpenMoshafView())
        self.add_view(ZkaatView())
        if os.getenv("REDIS_URL"):
            self.redis = aioredis.from_url(os.getenv("REDIS_URL"))
        for cog in cogs:
            await self.load_extension(cog)
        if os.getenv("DEBUG_GUILD"):
            self.tree.copy_global_to(guild=discord.Object(id=int(os.environ["DEBUG_GUILD"])))
            await self.tree.sync(guild=discord.Object(id=int(os.environ["DEBUG_GUILD"])))
        else:
            self.app_commands = await self.tree.sync()

    async def on_ready(self):
        logging.info(f"Bot is ready - {self.user}")
    
    def run(self):
        super().run(
            os.getenv("TOKEN"), 
            log_handler=logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w'),
        )


if __name__ == "__main__":
    setup_logger()
    bot = Bot()
    bot.run()
