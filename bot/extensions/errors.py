import hikari
import lightbulb
from lightbulb import Plugin, MissingRequiredPermission
from bot.utils import leave_and_stop


error_plugin = Plugin("errors")

# must edit this file to add new errors
@error_plugin.listener(lightbulb.SlashCommandErrorEvent)
async def on_slash_command_error_event(event: lightbulb.SlashCommandErrorEvent):
    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=event.context.bot.footer, icon=event.context.bot.get_me().avatar_url)
    if isinstance(event.exception, MissingRequiredPermission):
        await event.context.respond("ليس لديك الصلاحيات الكافية لتنفيذ هذا الأمر ❌", flags=hikari.MessageFlag.EPHEMERAL)
        return
    elif event.context.bot.lavalink.is_connect == False:
        await event.context.respond("يرجى إعادة كتابة الأمر من جديد", flags=hikari.MessageFlag.EPHEMERAL)
        await event.bot.create_lavalink_connection()
        await leave_and_stop(error_plugin.bot, event.context.guild_id)
        return
    embed.title = "خطأ غير معروف"
    embed.description = event.exception.__str__()
    embed.set_footer("إذ أستمرة هذا الخطأ يرجى التواصل مع الدعم الفني")
    await event.context.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)

@error_plugin.listener(lightbulb.PrefixCommandErrorEvent)
async def prefix_command_error_event(event: lightbulb.PrefixCommandErrorEvent):
    return


def load(bot):
    bot.add_plugin(error_plugin)

def unload(bot):
    bot.remove_plugin(error_plugin)
