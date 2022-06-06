import hikari
import lightbulb
from lightbulb import Plugin, MissingRequiredPermission
from bot.utils import leave_and_stop
import json
import datetime
import pathlib

error_plugin = Plugin("errors")

# must edit this file to add new errors
@error_plugin.listener(lightbulb.SlashCommandErrorEvent)
async def on_slash_command_error_event(event: lightbulb.SlashCommandErrorEvent):
    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=event.context.bot.footer, icon=event.context.bot.get_me().avatar_url)
    if isinstance(event.exception, MissingRequiredPermission):
        embed.description = "ليس لديك الصلاحيات الكافية لتنفيذ هذا الأمر"
        await event.context.respond(embed=embed)
        return
    elif event.context.bot.lavalink.is_connect == False:
        embed.description = "يرجى إعادة كتابة الأمر من جديد"
        await event.context.respond(embed=embed)
        await event.bot.create_lavalink_connection()
        await leave_and_stop(error_plugin.bot, event.context.guild_id)
        return   
    embed.description = event.exception.__str__()
    await event.context.respond(embed=embed)

@error_plugin.listener(lightbulb.PrefixCommandErrorEvent)
async def prefix_command_error_event(event: lightbulb.PrefixCommandErrorEvent):
    return


def load(bot):
    bot.add_plugin(error_plugin)

def unload(bot):
    bot.remove_plugin(error_plugin)
