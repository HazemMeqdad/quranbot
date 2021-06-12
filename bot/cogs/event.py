import discord
from discord.ext import commands
from bot import db
import requests
import bot.config as config
from discord import Webhook, AsyncWebhookAdapter
import aiohttp


class Event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _send_webhook(msg):
        re = requests.post(config.webhook, data={"content": msg})
        return re.status_code

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        x = db.Guild(guild)
        x.insert()
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(config.webhook, adapter=AsyncWebhookAdapter(session))
            embed = discord.Embed(title="add guild", color=0x46FF00)
            embed.add_field(name='name guild: ', value=guild.name, inline=False)
            embed.add_field(name='id guild: ', value=guild.id, inline=False)
            embed.add_field(name='owner guild: ', value=f"<@{guild.owner_id}> ", inline=False)
            embed.add_field(name='owner id: ', value=str(guild.owner_id), inline=False)
            embed.add_field(name='member guild: ', value=guild.member_count, inline=False)
            embed.add_field(name='bot server: ', value=f'{len(self.bot.guilds)}', inline=False)
            embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        x = db.Guild(guild)
        x.insert()
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(config.webhook, adapter=AsyncWebhookAdapter(session))
            embed = discord.Embed(title="remove guild", color=0xFF0000)
            embed.add_field(name='name guild: ', value=guild.name, inline=False)
            embed.add_field(name='id guild: ', value=guild.id, inline=False)
            embed.add_field(name='owner guild: ', value=f"<@{guild.owner_id}>", inline=False)
            embed.add_field(name='owner id: ', value=str(guild.owner_id), inline=False)
            embed.add_field(name='member guild: ', value=guild.member_count, inline=False)
            embed.add_field(name='bot server: ', value=f'{len(self.bot.guilds)}', inline=False)
            embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await webhook.send(embed=embed)


def setup(client):
    client.add_cog(Event(client))

