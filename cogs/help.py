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
            list_commands.append(f"**`{db.get_prefix(ctx.guild)}{i.name} {i.signature}`** - {i.help}")
        return "\n".join(list_commands)

    @commands.command(name="help", description='قائمه الأوامر', help="عرض اوامر البوت")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def help_command(self, ctx, *, command=None):
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
**<:fdr50:845022052482023495> - help:** {command.help}\n\
**<:fdr50:845022052482023495> - usage:** {db.get_prefix(ctx.guild)}{command.name} {command.signature}\n\
**<:fdr50:845022052482023495> - aliases:** {aliases}\n",
                color=0xEFD881
            ).set_author(name=command.cog_name)
            await ctx.send(embed=embed)
            return
        embed = Embed(
            description="<:111:846484560120250389><:115:846484554126196766><:112:846484559645638697><:113:846484558235828255><:114:846484555782684742><:115:846484554126196766><:116:846484554213752872>\n\n%s\n\n<:001:846485195884593263><:005:846485185271824495><:002:846485195016110100><:003:846485193380462662><:004:846485186476900402><:005:846485185271824495><:006:846485183070339072>" % self.get_all_commands(ctx),
            color=0xEFD881
        )\
            .set_footer(text="بطلب من: {}".format(ctx.author), icon_url=ctx.author.avatar_url)\
            .set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)\
            .add_field(name="معلومات اكثر:", value="***[Support](https://discord.gg/EpZJwpSgka) & [Invite](https://fdrbot.xyz/) & [Donation تبرع](https://fdrbot.xyz/paypal)***")\
            .set_image(url='https://i8.ae/IjVZC')
        await ctx.send(embed=embed)
        return


def setup(client):
    client.add_cog(Help(client))
