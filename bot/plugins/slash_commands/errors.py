import hikari
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import MessageFlag
from lightbulb import SlashCommandErrorEvent
import lightbulb
from lightbulb.errors import (
    CommandError, 
    MissingRequiredPermission
)
from bot.bot import Bot


class SlashErrors(lightbulb.Plugin):
    @lightbulb.listener(SlashCommandErrorEvent)
    async def on_slash_command_error_event(self, event: SlashCommandErrorEvent):
        await event.context.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_CREATE, flags=MessageFlag.EPHEMERAL)
        embed = hikari.Embed(color=0xffd430)
        print(type(event.exception))
        if isinstance(event.exception, MissingRequiredPermission):
            embed.description = "> :rolling_eyes: | ليس لديك الصلاحيات الكافية"
            await event.context.edit_response(embed=embed)
            return
        elif isinstance(event.exception, CommandError):
            embed.description = event.exception.args[0].replace("CommandError: ", "")
            await event.context.edit_response(embed=embed)
            return
        embed.description = event.exception.args[0]
        await event.context.edit_response(embed=embed)


def load(bot: Bot):
    bot.add_plugin(SlashErrors)

