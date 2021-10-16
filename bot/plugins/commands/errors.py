import logging
import hikari
import lightbulb
from lightbulb.errors import (
    CheckFailure,
    CommandIsOnCooldown, 
    CommandNotFound, 
    MissingRequiredPermission,
    NotOwner,
    TooManyArguments,

)
from bot import Bot


class Errors(lightbulb.Plugin):
    pass
    # @lightbulb.listener(hikari.ExceptionEvent)
    # async def on_command_error(self, event: hikari.ExceptionEvent):
    #     embed = hikari.Embed(color=0xE50000)
    #     print(event.exception)
    #     if isinstance(event.exception, CommandIsOnCooldown):
    #         pass
    #     elif isinstance(event.exception, MissingRequiredPermission):
    #         pass
    #     elif isinstance(event.exception, CommandNotFound):
    #         pass
    #     elif isinstance(event.exception, NotOwner):
    #         return
    #     elif isinstance(event.exception, TooManyArguments):
    #         pass
    #     elif isinstance(event.exception, CheckFailure):
    #         await event.app.rest.trigger_typing(event.context.channel_id)
    #         return
    #     # elif isinstance()
    #     logging.error(event.exception)


def load(bot: Bot):
    bot.add_plugin(Errors)


def unload(bot: Bot):
    bot.remove_plugin("Errors")
