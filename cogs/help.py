import discord
from discord.ext import commands
from discord import Embed, Colour
import db


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_all_commands(self, ctx):
        list_commands = []
        for i in self.client.commands:
            if i.hidden:
                continue
            if i.usage is not None:
                list_commands.append(f"**`{db.get_prefix(ctx.guild)}{i.usage}`** - {i.help}")
                continue
            list_commands.append(f"**`{db.get_prefix(ctx.guild)}{i.name}`** - {i.help}")
        return "\n".join(list_commands)

    @commands.command(name="help", description='قائمه الأوامر', help="عرض اوامر البوت")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def help_command(self, ctx, *, command=None):
        # for i in self.client.commands:
        #     print(i.name)
        if command is not None:
            command = self.client.get_command(command)
            if command is None:
                await ctx.send("لم استطع العثور على هاذ الأمر.")
                return
            aliases = []
            if command.aliases == []:
                aliases = None
            else:
                aliases = ", ".join(command.aliases)
            embed = Embed(
                description=f"**command:** {command.name}\n\
**help:** {command.help}\n\
**usage:** {db.get_prefix(ctx.guild)}{command.usage}\n\
**aliases:** {aliases}\n",
                color=Colour.red()
            ).set_author(name=command.cog_name)
            await ctx.send(embed=embed)
            return
        embed = Embed(
            description=self.get_all_commands(ctx),
            color=Colour.red()
        )\
            .set_thumbnail(url=self.client.user.avatar_url)\
            .set_footer(text="بطلب من: {}".format(ctx.author), icon_url=ctx.author.avatar_url)\
            .set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)\
            .add_field(name="معلومات اكثر:", value="***[Support](https://discord.gg/Ea9SUFUQCY) & [Invite](https://discord.com/oauth2/authorize?client_id=728782652454469662&permissions=8&scope=bot) & [Vote](https://top.gg/bot/728782652454469662/vote)***")\
            .set_image(url='https://i8.ae/sRlUh')
        await ctx.send(embed=embed)
        return


def setup(client):
    client.add_cog(Help(client))
