from .emojis import Emojis
from .prayer import Prayer
from .voice import EventHandler, join_voice_channel, leave_and_stop
from .tasks import stop_tasks, create_tasks
import hikari

__all__ = [Emojis, Prayer, EventHandler, join_voice_channel, leave_and_stop, stop_tasks, create_tasks]

async def command_error(ctx, message: str):
    embed = hikari.Embed(
        description=message,
        color=0xffd430
    )
    await ctx.interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE, 
        flags=hikari.MessageFlag.EPHEMERAL,
        embed=embed
    )
