import hikari
import lightbulb
from lightbulb import Plugin, MissingRequiredPermission
from bot.utils import leave_and_stop
import json
import datetime
import pathlib

error_plugin = Plugin("errors")

@error_plugin.listener(lightbulb.SlashCommandErrorEvent)
async def on_slash_command_error_event(event: lightbulb.SlashCommandErrorEvent):
    embed = hikari.Embed(color=0xffd430)
    if isinstance(event.exception, MissingRequiredPermission):
        embed.description = "ليس لديك الصلاحيات الكافية لتنفيذ هذا الأمر"
        await event.context.respond(embed=embed)
        return
    elif event.context.bot.lavalink.is_connect == False:
        await event.bot.create_lavalink_connection()
        await leave_and_stop(event.context)
        await event.context.respond("يرجا إعادة كتابة الأمر مره أخره")
        return
    if pathlib.Path("errors.json").exists():
        with open("errors.json", "r") as f:
            errors = json.load(f)
        errors.append({
            "message": event.exception.__str__(),
            "traceback": event.exception.__traceback__.__str__(),
            "timestamp": str(datetime.datetime.now()),
            "channel": event.context.channel_id.__str__(),
            "guild": event.context.guild_id.__str__(),
        })
        with open("errors.json", "w") as f:
            json.dump(errors, f, indent=4)
            
    embed.description = event.exception.__str__()
    await event.context.respond(embed=embed)

@error_plugin.listener(lightbulb.PrefixCommandErrorEvent)
async def prefix_command_error_event(event: lightbulb.PrefixCommandErrorEvent):
    return


def load(bot):
    bot.add_plugin(error_plugin)

def unload(bot):
    bot.remove_plugin(error_plugin)
