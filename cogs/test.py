import discord
from discord.ext import commands
import requests


class Test(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='test')
    @commands.is_owner()
    async def test_command(self, ctx, *, text: str):
        url = 'https://discord.com/api/webhooks/836307929081577592/_Gi5YrMFNprtOguWq8bHKMpGVu13GR7NPtNEhqsL6xoV11HnZiLfejGI2vKDK2QCIxAG'
        print('-----')
        data = {
            "content": text,
            "avatar_url": "https://cdn.discordapp.com/avatars/728782652454469662/af534679b0f81090ff51d68ebd8e5963.png",
            "username": "فاذكروني",
            "embeds": [
                {
                    "description": "add guild",
                    "author": {"name": str(self.client.user.name), "icon_url": str(self.client.user.avatar_url)},
                    "footer": {"text": str(ctx.guild.name), "icon_url": str(ctx.guild.avatar_url)},
                    "fields": [
                        {"name": "Name:", "value": str(ctx.guild.name), "inline": False},
                        {"name": "ID:", "value": str(ctx.guild.id), "inline": False},
                        {"name": "Owner:", "value": f"<@{ctx.guild.owner_id}>", "inline": False},
                        {"name": "Owner ID:", "value": str(ctx.guild.owner_id), "inline": False},
                        {"name": "Member Count:", "value": str(ctx.guild.member_count), "inline": False},
                        {"name": "Guilds Count:", "value": str(len(self.client.guilds)), "inline": False}
                    ]
                }
            ]
        }

        print('------')
        result = requests.post(url, json=data)
        print(result)
        print(result.raise_for_status())
        print('------')

        # try:
        #     result.raise_for_status()
        #     # except requests.exceptions.HTTPError as err:
        # except Exception as err:
        #     print(err)
        # else:
        #     print("Payload delivered successfully, code {}.".format(result.status_code))


def setup(client):
    client.add_cog(Test(client))


