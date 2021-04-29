import discord
from discord.ext import commands
import db


class Event(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        db.add_guild(guild)
        channel = self.client.get_channel(815926277965873173)
        try:
            embed = discord.Embed(title="add guild", color=0x46FF00)
            embed.add_field(name='name guild: ', value=guild.name, inline=False)
            embed.add_field(name='id guild: ', value=guild.id, inline=False)
            embed.add_field(name='owner guild: ', value=f"<@{guild.owner_id}> ", inline=False)
            embed.add_field(name='owner id: ', value=str(guild.owner_id), inline=False)
            embed.add_field(name='member guild: ', value=guild.member_count, inline=False)
            embed.add_field(name='bot server: ', value=f'{len(self.client.guilds)}', inline=False)
            embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
            await channel.send(embed=embed)
        except Exception as error:
            print(error)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        db.delete_guild(guild.id)
        channel = self.client.get_channel(815926277965873173)
        try:
            embed = discord.Embed(title="remove guild", color=0xFF0000)
            embed.add_field(name='name guild: ', value=guild.name, inline=False)
            embed.add_field(name='id guild: ', value=guild.id, inline=False)
            embed.add_field(name='owner guild: ', value=f"<@{guild.owner_id}>", inline=False)
            embed.add_field(name='owner id: ', value=str(guild.owner_id), inline=False)
            embed.add_field(name='member guild: ', value=guild.member_count, inline=False)
            embed.add_field(name='bot server: ', value=f'{len(self.client.guilds)}', inline=False)
            embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
            await channel.send(embed=embed)
        except Exception as r:
            print(r)

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.guild is None:
            return
        # if ctx.guild.member_count >= 10000:
        #     print(ctx.guild)
        db.add_guild(ctx.guild)


def setup(client):
    client.add_cog(Event(client))

