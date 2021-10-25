import logging
import hikari
import lightbulb
from bot.bot import Bot
import inspect


class Owner(lightbulb.Plugin):
    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command(name="reload", hidden=True)
    async def reload_command(self, ctx: lightbulb.Context, extension):
        try:
            ctx.bot.reload_extension(f"bot.plugins.{extension}")
            logging.info(f"extension '{extension}' unloaded")
            await ctx.respond(f"Reloaded {extension} extension", reply=True, mentions_reply=False)
        except Exception as error:
            await ctx.respond(error, reply=True, mentions_reply=False)

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command(name="load", hidden=True)
    async def load_command(self, ctx: lightbulb.Context, extension: str):
        try:
            ctx.bot.unload_extension(f"bot.plugins.{extension}")
            logging.info(f"extension '{extension}' unloaded")
            await ctx.respond(f"loaded {extension} extension", reply=True, mentions_reply=False)
        except Exception as error:
            await ctx.respond(error.__str__, reply=True, mentions_reply=False)

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command(name="unload", hidden=True)
    async def unload_command(self, ctx: lightbulb.Context, extension: str):
        try:
            ctx.bot.unload_extension(f"bot.plugins.{extension}")
            logging.info(f"extension '{extension}' unloaded")
            await ctx.respond(f"Unloaded {extension} extension", reply=True, mentions_reply=False)
        except Exception as error:
            await ctx.respond(error.__str__, reply=True, mentions_reply=False)

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command(name="eval", hidden=True)
    async def eval_command(self, ctx: lightbulb.Context, expression: str = ""):
        to_eval = expression.replace("await ", "")
        try:
            result = eval(to_eval)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            result = "%s: %s" % (type(e).__name__, str(e))
        result = str(result)
        embed = hikari.Embed(description="Eval Result")
        embed.add_field(name="Input 📥", value=f"```py\n{expression}```", inline=False)
        embed.add_field(name="Output 📤", value=f"```py\n{result}```", inline=False)
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)

def load(bot: Bot):
    bot.add_plugin(Owner)


def unload(bot: Bot):
    bot.remove_plugin("Owner")

