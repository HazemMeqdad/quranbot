import discord
from discord.ext import commands
from discord.ext.commands import Cog
import asyncio
import bot.db as db
import bot.config as config
from requests import request
import bot.lang as lang

cooldown = []


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)

    @staticmethod
    def _send_webhook(msg):
        request(
            method="POST",
            url=config.webhook_errors,
            data={
                "content": msg
            })

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        x = db.Guild(ctx.guild)
        _ = lang.Languages(ctx.guild).get_response_errors()
        color = self.bot.color.red
        if ctx.author.id in cooldown:
            return
        # cooldown
        elif isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            await ctx.reply(
                embed=discord.Embed(
                    description=_["cooldown"] % (self.emoji.errors, round(s)),
                    color=color
                ),
                delete_after=2
            )
            cooldown.append(ctx.author.id)
            await asyncio.sleep(10)
            cooldown.remove(ctx.author.id)
            return
        # DM channel
        elif isinstance(ctx.channel, discord.channel.DMChannel):
            return
        # missing permissions
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(
                embed=discord.Embed(
                    description=_["missing_perms"] % (", ".join(error.missing_perms), self.emoji.errors),
                    color=color
                )
            )
        # command not found
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        # channel not found
        elif isinstance(error, commands.errors.ChannelNotFound):
            await ctx.reply(
                embed=discord.Embed(
                    description=_["channel_not_found"] % self.emoji.errors,
                    color=color
                )
            )
            return
        # bot missing permissions
        elif isinstance(error, commands.errors.BotMissingPermissions):
            await ctx.reply(
                embed=discord.Embed(
                    description=_["bot_missing_permissions"] % (", ".join(error.missing_perms), self.emoji.errors),
                    color=color
                )
            )
        # message not found
        elif isinstance(error, commands.errors.MessageNotFound):
            return
        # command invoke error
        elif isinstance(error, commands.errors.CommandInvokeError):
            return
        # missing required argument
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                description=f"{x.info['prefix']}{ctx.command.name} {ctx.command.signature}",
                color=color
            ).set_author(name=ctx.command.cog_name)
            await ctx.reply(embed=embed)
            return
        # bad argument
        elif isinstance(error, commands.errors.BadArgument):
            embed = discord.Embed(
                description=f"{x.info['prefix']}{ctx.command.name} {ctx.command.signature}",
                color=color
            )
            embed.set_author(name=ctx.command.cog_name)
            await ctx.reply(embed=embed)
            return
        # forbidden
        elif isinstance(error, discord.errors.Forbidden):
            return
        # blacklist
        elif isinstance(error, commands.errors.CheckFailure):
            if ctx.command.hidden:
                return
            embed = discord.Embed(
                description=_["blacklist"] % self.bot.support_url,
                color=self.bot.get_color(self.bot.color.gold)
            )
            await ctx.reply(embed=embed)
            cooldown.append(ctx.author.id)
            await asyncio.sleep(10)
            cooldown.remove(ctx.author.id)
            return
        # other error
        # await ctx.reply(embed=discord.Embed(
        #     description=_["other_error"],
        #     color=color
        # ))
        # self._send_webhook("Error from %s (`%s`)\n%s" % (ctx.guild.name, ctx.guild.id, error))
        # return


def setup(bot):
    bot.add_cog(Errors(bot))
