import hikari
from hikari.interactions.base_interactions import ResponseType
from hikari.messages import MessageFlag
import lightbulb
from lightbulb import Plugin, MissingRequiredPermission
from bot.utils import leave_and_stop

error_plugin = Plugin("errors")

@error_plugin.listener(lightbulb.SlashCommandErrorEvent)
async def on_slash_command_error_event(event: lightbulb.SlashCommandErrorEvent):
    await event.context.interaction.create_initial_response(ResponseType.DEFERRED_MESSAGE_CREATE, flags=MessageFlag.EPHEMERAL)
    embed = hikari.Embed(color=0xffd430)
    if isinstance(event.exception, MissingRequiredPermission):
        embed.description = "ليس لديك الصلاحيات الكافية لتنفيذ هذا الأمر"
        await event.context.interaction.edit_initial_response(embed=embed)
        return
    elif event.context.bot.lavalink.is_connect == False:
        await event.bot.create_lavalink_connection()
        await leave_and_stop(event.context)
        await event.context.interaction.edit_initial_response("يرجا إعادة كتابة الأمر مره أخره")
        return
    print(event.exception)
    embed.description = event.exception.args[0]
    await event.context.interaction.edit_initial_response(embed=embed)

@error_plugin.listener(lightbulb.PrefixCommandErrorEvent)
async def prefix_command_error_event(event: lightbulb.PrefixCommandErrorEvent):
    return


def load(bot):
    bot.add_plugin(error_plugin)

