import discord
from discord.ext import commands, tasks
from db.db import *
from config import *


def get_prefix(bot, message):
    prefix = cr.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (message.guild.id,))
    return commands.when_mentioned_or(prefix.fetchone()[0])(bot, message)


client = commands.AutoShardedBot(
    command_prefix=get_prefix,
    case_insensitive=True,
    description="بوت فذكروني",
    shard_count=3
)

client.token = token
client.prefix = prefix
client.remove_command("help")

cogs = [
    "prefix",
    "help",
    "commands",
    "setroom",
    "time"
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
            "INSERT OR IGNORE INTO guilds(guild_id, guild_name, prefix) VALUES(?, ?, ?)",
            (i.id, i.name, "!"))
    db.commit()
    await client.change_presence(activity=discord.Game(name="!help | فَاذْكُرونِي"))
    print(f"Name: {client.user.name}\nID: {client.user.id}")


@client.event
async def on_guild_join(guild):
    cr.execute(
        "INSERT OR IGNORE INTO guilds(guild_id, guild_name, prefix) VALUES(?, ?, ?)",
        (guild.id, guild.name, "!"))
    db.commit()
    try:
        channel = client.get_channel(815926277965873173)
        embed = discord.Embed(title="add guild", color=0x46FF00)
        embed.add_field(name='name guild: ', value=guild.name, inline=False)
        embed.add_field(name='id guild: ', value=guild.id, inline=False)
        embed.add_field(name='owner guild: ', value='<@' + str(guild.owner_id) + ">", inline=False)
        embed.add_field(name='owner id: ', value=str(guild.owner_id), inline=False)
        embed.add_field(name='member guild: ', value=guild.member_count, inline=False)
        embed.add_field(name='bot server: ', value=f'{len(client.guilds)}', inline=False)
        embed.set_footer(text=guild.name, icon_url=guild.icon_url)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        await channel.send(embed=embed)
    except Exception as Error:
        print(Error)


@client.event
async def on_guild_remove(guild):
    try:
        channel = client.get_channel(815926277965873173)
        embed = discord.Embed(title="remove guild", color=0xFF0000)
        embed.add_field(name='name guild: ', value=guild.name, inline=False)
        embed.add_field(name='id guild: ', value=guild.id, inline=False)
        embed.add_field(name='owner guild: ', value='<@' + str(guild.owner_id) + ">", inline=False)
        embed.add_field(name='owner id: ', value=str(guild.owner_id), inline=False)
        embed.add_field(name='member guild: ', value=guild.member_count, inline=False)
        embed.add_field(name='bot server: ', value=f"{len(client.guilds)}", inline=False)
        embed.set_footer(text=guild.name, icon_url=guild.icon_url)
        embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        await channel.send(embed=embed)
    except Exception as Error:
        print(Error)

client.run(client.token)
