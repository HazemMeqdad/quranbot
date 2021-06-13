import discord
from discord.ext import commands
import bot.db as db
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
import bot.config as config


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        x = db.Guild(guild)
        x.insert()
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(config.webhook_log, adapter=AsyncWebhookAdapter(session))
            embed = discord.Embed(title="add guild", color=0x46FF00)
            embed.add_field(name='name guild: ', value="%s (`%s`)" % (guild.name, guild.id), inline=False)
            embed.add_field(name='member guild: ', value=str(guild.member_count), inline=False)
            embed.add_field(name='owner guild: ', value="%s (`%s`)" % (await self.bot.fetch_user(int(guild.owner_id)), guild.owner_id), inline=False)
            embed.add_field(name='bot server: ', value=f'{len(self.bot.guilds)}', inline=False)
            embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await webhook.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        x = db.Guild(guild)
        x.insert()
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(config.webhook_log, adapter=AsyncWebhookAdapter(session))
            embed = discord.Embed(title="remove guild", color=0xFF0000)
            embed.add_field(name='name guild: ', value="%s (`%s`)" % (guild.name, guild.id), inline=False)
            embed.add_field(name='member guild: ', value=str(guild.member_count), inline=False)
            embed.add_field(name='owner guild: ', value="%s (`%s`)" % (await self.bot.fetch_user(int(guild.owner_id)), guild.owner_id), inline=False)
            embed.add_field(name='bot server: ', value=f'{len(self.bot.guilds)}', inline=False)
            embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
            await webhook.send(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))
