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
    command_prefix='!',
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


@client.event
async def on_ready():
    users = 0
    channels = 0
    guilds_plus_100 = 0
    guilds_plus_1000 = 0
    for i in client.guilds:
        db.add_guild(i)
        users += i.member_count
        channels += len(i.channels)
        if i.member_count >= 100:
            guilds_plus_100 += 1
        if i.member_count >= 1000:
            guilds_plus_1000 += 1
    print('--------')
    print(f'guilds: {len(client.guilds)}')
    print(f'Users: {users}')
    print(f'channels: {channels}')
    print(f'guilds +100: {guilds_plus_100}')
    print(f'guilds +1000: {guilds_plus_1000}')
    print('--------')
    await client.change_presence(activity=discord.Game(type=discord.ActivityType.listening, name='!help | رمضان كريم'),
                                 status=discord.Status.idle)
    print(f"Name: {client.user.name}\nID: {client.user.id}")


@client.event
async def on_shard_ready(shard_id):
    print(f'`shard {shard_id} is ready`')


client.run(config.token)
