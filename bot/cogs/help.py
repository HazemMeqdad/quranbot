from discord.ext import commands
import bot.db as db
import discord
import bot.config as config
import bot.lang as lang


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)

    def get_all_commands(self, ctx, _):
        m = db.Guild(ctx.guild)
        embed = discord.Embed(color=self.bot.get_color(self.bot.color.gold))
        embed.set_footer(text=_["request_by"].format(ctx.author), icon_url=ctx.author.avatar.url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.set_image(url='https://i8.ae/IjVZC')
        cogs = ["General", "Admin", "Quran"]
        for i in cogs:
            o = ""
            for x in self.bot.get_cog(i).walk_commands():
                if x.hidden:
                    continue
                o += f"`{m.info['prefix']}{x.name}{' %s' % x.signature if x.signature else ''}` - {x.short_doc}\n"
            embed.add_field(name=str(i), value=o.strip(), inline=False)
        embed.add_field(name=_["other_info"], value="***[Support](https://discord.gg/EpZJwpSgka) & "
                                                    "[Invite](https://fdrbot.xyz/) & "
                                                    "[Donation](https://fdrbot.xyz/paypal)***")
        return embed

    @commands.command(name="help", description='قائمه الأوامر', help="عرض اوامر البوت", hidden=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def help_command(self, ctx, *, command=None):
        x = db.Guild(ctx.guild)
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        if command is not None:
            command = self.bot.get_command(command)
            if command is None:
                await ctx.reply(embed=discord.Embed(
                    description=_["if_not_find_command"],
                    color=self.bot.get_color(self.bot.color.gold)
                ))
                return
            if not command.aliases:
                aliases = _["not_find"]
            else:
                aliases = ", ".join(command.aliases)
            embed = discord.Embed(
                description=f"""
{_["command"]} {command.name}
**{self.emoji.fdr_50} - {_["description"]}:** {command.help}
**{self.emoji.fdr_50} - {_["usage"]} {x.info['prefix']}{command.name} {command.signature}
**{self.emoji.fdr_50} - {_["aliases"]}:** {aliases}
""",
                color=self.bot.get_color(self.bot.color.gold)
            )
            embed.set_author(name=command.cog_name)
            return await ctx.reply(embed=embed)
        await ctx.reply(embed=self.get_all_commands(ctx, _))


def setup(client):
    client.add_cog(Help(client))
