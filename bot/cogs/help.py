from discord.ext import commands
import bot.db as db
import discord
import bot.config as config


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)

    def get_all_commands(self, ctx):
        list_commands = []
        x = db.Guild(ctx.guild)
        for i in self.bot.commands:
            if i.hidden:
                continue
            list_commands.append(f"**`{x.info[2]}{i.name} {i.signature}`** - {i.help}")
        return "\n".join(list_commands)

    @commands.command(name="help", description='قائمه الأوامر', help="عرض اوامر البوت")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def help_command(self, ctx, *, command=None):
        x = db.Guild(ctx.guild)
        if command is not None:
            command = self.bot.get_command(command)
            if command is None:
                await ctx.send("لم استطع العثور على هاذ الأمر.")
                return
            if not command.aliases:
                aliases = "لا يوجد"
            else:
                aliases = ", ".join(command.aliases)
            embed = discord.Embed(
                description=f"**الأمر:** {command.name}\n\
**{self.emoji.fdr_50} - الوصف:** {command.help}\n\
**{self.emoji.fdr_50} - الاستعمال:** {x.info[2]}{command.name} {command.signature}\n\
**{self.emoji.fdr_50} - الأختصارات:** {aliases}\n",
                color=0xEFD881
            )
            embed.set_author(name=command.cog_name)
            return await ctx.send(embed=embed)
        embed = discord.Embed(
            description=self.get_all_commands(ctx),
            color=0xEFD881
        )
        embed.set_footer(text="بطلب من: {}".format(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.add_field(name="معلومات اكثر:", value="***[Support](https://discord.gg/EpZJwpSgka) & [Invite](https://fdrbot.xyz/) & [Donation تبرع](https://fdrbot.xyz/paypal)***")
        embed.set_image(url='https://i8.ae/IjVZC')
        return await ctx.send(embed=embed)



def setup(client):
    client.add_cog(Help(client))
