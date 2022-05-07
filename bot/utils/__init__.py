from .emojis import Emojis
from .prayer import Prayer
from .voice import join_voice_channel, leave_and_stop
import hikari

__all__ = [Emojis, Prayer, join_voice_channel, leave_and_stop]

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
