import discord
from discord.ext import commands, tasks
from db.db import *
from config import all
import random
import time


def get_prefix(bot, message):
    prefix = cr.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (message.guild.id,))
    return commands.when_mentioned_or(prefix.fetchone()[0])(bot, message)


client = commands.AutoShardedBot(
    command_prefix=get_prefix,
    case_insensitive=True,
    description="بوت فذكروني",
    shard_count=2
)

client.remove_command("help")

cogs = [
    "prefix",
    "help",
    "commands",
    "setroom"
]

for i in cogs:
    try:
        client.load_extension(f"cogs.{i}")
        print(f"load: {i}")
    except Exception as error:
        print(f"the error is \n{error}")

client.load_extension("errors.error")
client.load_extension("tasks.send")


@client.event
async def on_ready():
    for i in client.guilds:
        cr.execute(
            "INSERT OR IGNORE INTO guilds(guild_id, guild_name, prefix, channel) VALUES(?, ?, ?, ?)",
            (i.id, i.name, "!", None))
    db.commit()
    await client.change_presence(activity=discord.Game(name="!help | فَاذْكُرونِي"))
    print(f"Name: {client.user.name}\nID: {client.user.id}")


@client.event
async def on_guild_join(guild):
    cr.execute(
        "INSERT OR IGNORE INTO guilds(guild_id, guild_name, prefix, channel) VALUES(?, ?, ?, ?)",
        (guild.id, guild.name, "!", None))
    db.commit()


@client.event
async def on_guild_remove(guild):
    cr.execute(
        "INSERT OR IGNORE INTO guilds(guild_id, guild_name, prefix, channel) VALUES(?, ?, ?, ?)",
        (guild.id, guild.name, "!", None))
    db.commit()

client.run("NzI4NzgyNjUyNDU0NDY5NjYy.Xv_ZvA.mYlu3RbabV_0T1-Dym-YtsKZaNM")