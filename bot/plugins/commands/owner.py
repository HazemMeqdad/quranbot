import logging
import hikari
import lightbulb
from bot import Bot


class Owner(lightbulb.Plugin):
    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command(name="reload", hidden=True)
    async def reload_command(self, ctx: lightbulb.Context, extension):
        try:
            ctx.bot.reload_extension(f"bot.plugins.{extension}")
            logging.info(f"extension '{extension}' unloaded")
            await ctx.respond(f"Reloaded {extension} extension")
        except Exception as error:
            await ctx.respond(error)

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command(name="load", hidden=True)
    async def load_command(self, ctx: lightbulb.Context, extension: str):
        try:
            ctx.bot.unload_extension(f"bot.plugins.{extension}")
            logging.info(f"extension '{extension}' unloaded")
            await ctx.respond(f"loaded {extension} extension")
        except Exception as error:
            await ctx.respond(error.__str__)

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command(name="unload", hidden=True)
    async def unload_command(self, ctx: lightbulb.Context, extension: str):
        try:
            ctx.bot.unload_extension(f"bot.plugins.{extension}")
            logging.info(f"extension '{extension}' unloaded")
            await ctx.respond(f"Unloaded {extension} extension")
        except Exception as error:
            await ctx.respond(error.__str__)

        


def load(bot: Bot):
    bot.add_plugin(Owner)


def unload(bot: Bot):
    bot.remove_plugin("Owner")

