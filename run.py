import os
import discord
from discord.app_commands import CommandTree
from discord.ext import commands
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    ...
from cogs.utlits.views import OpenMoshafView, ZkaatView
import lavalink


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
    "cogs.tasks"
]

class Bot(commands.Bot):
    def __init__(self):
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
        for cog in cogs:
            await self.load_extension(cog)
        if os.getenv("DEBUG_GUILD"):
            self.tree.copy_global_to(guild=discord.Object(id=int(os.environ["DEBUG_GUILD"])))
            await self.tree.sync(guild=discord.Object(id=int(os.environ["DEBUG_GUILD"])))

    async def on_ready(self):

        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
    
    def run(self):
        super().run(os.getenv("TOKEN"))


bot = Bot()
bot.run()
