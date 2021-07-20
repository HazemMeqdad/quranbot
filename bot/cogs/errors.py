import discord
from discord.ext import commands
from discord.ext.commands import Cog
import asyncio
import bot.db as db
import bot.config as config
import requests


cooldown = []


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)

    @staticmethod
    def _send_webhook(msg):
        re = requests.post(config.webhook_errors, data={"content": msg})
        return re.status_code

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        x = db.Guild(ctx.guild)

        def embed(description) -> discord.Embed:
            _embed = discord.Embed(
                description=description,
                color=self.bot.get_color(self.bot.color.gold)
            )
            return _embed
        if ctx.author.id in cooldown:
            return
        elif isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            await ctx.send(
                embed=embed("%s يجب عليك الانتظار `%s` ثواني" % (self.emoji.errors, round(s))),
                delete_after=2
            )
            cooldown.append(ctx.author.id)
            await asyncio.sleep(10)
            cooldown.remove(ctx.author.id)
            return
        elif isinstance(ctx.channel, discord.channel.DMChannel):
            return
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(
                embed=embed("أنت بحاجة إلى صلاحيات `%s` %s" % (", ".join(error.missing_perms), self.emoji.errors))
            )
        elif isinstance(error, commands.errors.CommandNotFound):
            return
        elif isinstance(error, commands.errors.ChannelNotFound):
            await ctx.send(
                embed=embed("يجب التحقق من نوع الروم المحدده %s" % self.emoji.errors)
            )
            return
        elif isinstance(error, commands.errors.BotMissingPermissions):
            await ctx.send(
                embed=embed("البوت لا يمتلك صلاحيات `%s` %s" % (", ".join(error.missing_perms), self.emoji.errors))
            )
        elif isinstance(error, commands.errors.MessageNotFound):
            return
        elif isinstance(error, commands.errors.CommandInvokeError):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                description=f"{x.info[2]}{ctx.command.name} {ctx.command.signature}",
                color=self.bot.get_color(self.bot.color.gold)
            ).set_author(name=ctx.command.cog_name)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, commands.errors.BadArgument):
            embed = discord.Embed(
                description=f"{x.info[2]}{ctx.command.name} {ctx.command.signature}",
                color=self.bot.get_color(self.bot.color.gold)
            ).set_author(name=ctx.command.cog_name)
            await ctx.send(embed=embed)
            return
        elif isinstance(error, discord.errors.Forbidden):
            return
        elif isinstance(error, commands.errors.CheckFailure):
            embed = discord.Embed(
                description="انت ضمن القائمه السوداء لمعلومات اكثر تواصل مع [الدعم الفني](https://discord.gg/q3E6WCSThX)",
                color=self.bot.get_color(self.bot.color.gold)
            )
            await ctx.send(embed=embed)
            cooldown.append(ctx.author.id)
            await asyncio.sleep(10)
            cooldown.remove(ctx.author.id)
            return
        else:
            await ctx.send(embed=embed("يبدو ان هنالك خطأ غير متوقع تم ارسال بلاغ للمطورين تلقائياً"))
            self._send_webhook("Error from %s (`%s`)\n%s" % (ctx.guild.name, ctx.guild.id, error))
            return


def setup(bot):
    bot.add_cog(Errors(bot))
