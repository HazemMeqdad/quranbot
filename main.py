import discord
from discord.ext import commands
import db
import config


def get_prefix(bot, msg):
    prefix = commands.when_mentioned_or('!')(bot, msg)
    try:
        prefix = commands.when_mentioned_or(db.get_prefix(msg.guild))(bot, msg)
    except AttributeError:
        prefix = commands.when_mentioned_or('!')(bot, msg)
    finally:
        return prefix


client = commands.AutoShardedBot(
    command_prefix=get_prefix,
    case_insensitive=True,
    description="بوت فذكروني",
    Intents=discord.Intents.default(),
    shard_count=5
)


client.remove_command("help")

cogs = [
    "prefix",
    "help",
    "commands",
    "setroom",
    "set_time",
    "play",
    'errors',
    # 'test',
    'event',
    'set',
    'owner'
]

for i in cogs:
    try:
        client.load_extension(f"cogs.{i}")
        print(f"load: {i}")
    except Exception as error:
        print(f"the error is \n{error}")

client.load_extension("tasks.send")

client.owner_ids = config.owners


# !help - رمضان كريم 🌙
@client.event
async def on_ready():
    for i in client.guilds:
        db.add_guild(i)
    await client.change_presence(activity=discord.Game(type=discord.ActivityType.listening, name='صيانه... 🌙'),
                                 status=discord.Status.idle)
    print(f"Name: {client.user.name}\nID: {client.user.id}")


@client.event
async def on_shard_ready(shard_id):
    print(f'`shard {shard_id} is ready`')


@client.event
async def on_shard_disconnect(shard_id):
    channel = client.get_channel(837105079093821470)
    await channel.send(f'Shard {shard_id} has been disconnect.')


@client.event
async def on_shard_resumed(shard_id):
    channel = client.get_channel(837105079093821470)
    await channel.send(f'Shard {shard_id} has been resumed.')


client.run(config.token)
