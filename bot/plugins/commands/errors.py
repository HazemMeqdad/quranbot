import logging
import hikari
import lightbulb
from lightbulb.errors import (
    CheckFailure,
    CommandError,
    CommandIsOnCooldown, 
    CommandNotFound, 
    MissingRequiredPermission,
    NotOwner,
    SlashCommandInvocationError,

)
from bot import Bot


class Errors(lightbulb.Plugin):
    @lightbulb.listener(lightbulb.CommandErrorEvent)
    async def on_command_error(self, event: lightbulb.CommandErrorEvent):
        embed = hikari.Embed(color=0xE50000)
        if isinstance(event.exception, CommandIsOnCooldown):
            return
        elif isinstance(event.exception, CommandNotFound):
            return
        elif isinstance(event.exception, NotOwner):
            return
        elif isinstance(event.exception, MissingRequiredPermission):
            embed.description = "عذراً أنت لا تمتلك صلاحيات `%s`" % event.exception.permissions.name
            await event.context.respond(embed=embed)
        elif isinstance(event.exception, CheckFailure):
            return
        elif isinstance(event.exception, SlashCommandInvocationError):
            return
        logging.error(event.exception)


    @lightbulb.listener(hikari.ExceptionEvent)
    async def on_exception_event(self, event: hikari.ExceptionEvent):
        logging.warning(event.exc_info)


def load(bot: Bot):
    bot.add_plugin(Errors)


def unload(bot: Bot):
    bot.remove_plugin("Errors")
