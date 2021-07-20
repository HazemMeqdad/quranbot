from discord.ext import commands
import bot.db as db
import discord
import bot.config as config


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)

    def get_all_commands(self, ctx):
        m = db.Guild(ctx.guild)
        embed = discord.Embed(color=self.bot.get_color(self.bot.color.gold))
        embed.set_footer(text="بطلب من: {}".format(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_image(url='https://i8.ae/IjVZC')
        cogs = ["General", "Admin", "Quran"]
        for i in cogs:
            _ = ""
            for x in self.bot.get_cog(i).walk_commands():
                if x.hidden:
                    continue
                _ += f"`{m.info['prefix']}{x.name}{' %s' % x.signature if x.signature else ''}` - {x.short_doc}\n"
            embed.add_field(name=str(i), value=_.strip(), inline=False)
        embed.add_field(name="معلومات اكثر:", value="***[Support](https://discord.gg/EpZJwpSgka) & [Invite](https://fdrbot.xyz/) & [Donation تبرع](https://fdrbot.xyz/paypal)***")
        return embed

    @commands.command(name="help", description='قائمه الأوامر', help="عرض اوامر البوت", hidden=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def help_command(self, ctx, *, command=None):
        x = db.Guild(ctx.guild)
        if command is not None:
            command = self.bot.get_command(command)
            if command is None:
                await ctx.send(embed=discord.Embed(
                    description="لم استطع العثور على هاذ الأمر.",
                    color=self.bot.get_color(self.bot.color.gold)
                ))
                return
            if not command.aliases:
                aliases = "لا يوجد"
            else:
                aliases = ", ".join(command.aliases)
            embed = discord.Embed(
                description=f"**الأمر:** {command.name}\n\
**{self.emoji.fdr_50} - الوصف:** {command.help}\n\
**{self.emoji.fdr_50} - الاستعمال:** {x.info['prefix']}{command.name} {command.signature}\n\
**{self.emoji.fdr_50} - الأختصارات:** {aliases}\n",
                color=self.bot.get_color(self.bot.color.gold)
            )
            embed.set_author(name=command.cog_name)
            return await ctx.reply(embed=embed)
        await ctx.reply(embed=self.get_all_commands(ctx))


def setup(client):
    client.add_cog(Help(client))
