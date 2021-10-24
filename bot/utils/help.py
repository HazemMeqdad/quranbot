from bot.utils import play
from sys import prefix
import hikari
from lightbulb.help import HelpCommand, get_command_signature
from lightbulb import Context
from lightbulb import Plugin
from lightbulb.commands import Command, Group



commands_map = {
    # General
    "ping": "ارسال سرعة اتصال البوت",
    "support": "طلب الدعم الفني",
    "info": "طلب معلومات الخادم",
    "azan": "معرفة وقت الاذان في المدينة الخاصه بك",
    "bot": "جلب معلومات البوت",

    # Admin
    "prefix": "تغير البادئة الخاصة بالخادم",
    "anti_spam": "عدم تكرار الرسائل, ينصح باستخدامه في الشاتات المفتوحه",
    "embed": "تغير خاصيه ارسال الاذكار الى امبد",
    "time": "تغير وقت ارسال الأذكار",
    "setroom": "تغير خاصيه ارسال الاذكار الى امبد",
    "remove": "توقف البوت عن إرسال الأذكار",

    # Quran
    "play": "تشغيل القران الكريم",
    "live": "تشغيل اذاعه القران الكريم",
    "stop": "ايقاف تشغيل القران الكريم",
    "join": "انظمام البوت الى روم صوتي",
    "vol": "تغير مستوى الصوت للقران الكريم"
}
footer = "بوت فاذكروني لإحياء سنة ذكر الله"
image_url = "https://cdn.discordapp.com/attachments/827646785769177127/828712034430484541/9da927c7367fb968.png"


class CustomHelp(HelpCommand):
    async def object_not_found(self, context: Context, name: str) -> None:
        await context.respond("لم استتطع العثور على %s" % name, reply=True, mentions_reply=False)

    async def send_plugin_help(self, context: Context, plugin: Plugin) -> None:
        description = ""
        for command in plugin.walk_commands():
            comm = commands_map.get(command.name)
            if not comm:
                continue
            description += f"`{context.clean_prefix}{command.name}` - {comm}\n"
        embed = hikari.Embed(
            title="قائمة المساعدة الخاصة بي `%s`" % plugin.name,
            description=description,
            color=0xffd430
        )
        embed.set_author(name=context.bot.get_me().username, icon=context.bot.get_me().avatar_url)
        embed.set_footer(text=footer, icon=context.bot.get_me().avatar_url)
        embed.add_field(name="معلومات اكثر:", value="***[Support](https://discord.gg/EpZJwpSgka) & "
                                                    "[Invite](https://fdrbot.xyz/) & "
                                                    "[Donation](https://fdrbot.xyz/paypal)***"
        )
        embed.set_image(image_url)
        await context.respond(embed=embed, reply=True, mentions_reply=False)

    async def send_command_help(self, context: Context, command: Command) -> None:        
        embed = hikari.Embed(
            title="قائمة المساعدة الخاصة بالأمر `%s`" % command.name,
            description=f"```\n{context.clean_prefix}{get_command_signature(command)}\n```",
            color=0xffd430
        )
        embed.set_author(name=context.bot.get_me().username, icon=context.bot.get_me().avatar_url)
        embed.set_footer(text=footer, icon=context.bot.get_me().avatar_url)
        embed.add_field(name="معلومات اكثر:", value="***[Support](https://discord.gg/EpZJwpSgka) & "
                                                    "[Invite](https://fdrbot.xyz/) & "
                                                    "[Donation](https://fdrbot.xyz/paypal)***"
        )
        await context.respond(embed=embed, reply=True, mentions_reply=False)

    async def send_help_overview(self, context: Context) -> None:
        embed = hikari.Embed(
            title="قائمة المساعدة",
            color=0xffd430
        )
        for plugin in context.bot.plugins.values():
            _ = ""
            for command in plugin.walk_commands():
                comm = commands_map.get(command.name)
                if not comm or command.hidden:
                    continue
                _ += f"`{context.clean_prefix}{command.name}` - {comm}\n"
            if len(_) == 0:
                continue
            embed.add_field(name=plugin.name.lower(), value=_)

        embed.set_author(name=context.bot.get_me().username, icon=context.bot.get_me().avatar_url)
        embed.set_footer(text=footer, icon=context.bot.get_me().avatar_url)
        embed.add_field(name="معلومات اكثر:", value="***[Support](https://discord.gg/EpZJwpSgka) & "
                                                    "[Invite](https://fdrbot.xyz/) & "
                                                    "[Donation](https://fdrbot.xyz/paypal)***"
        )
        embed.set_image(image_url)
        await context.respond(embed=embed, reply=True, mentions_reply=False)

    async def send_group_help(self, context: Context, group: Group) -> None:
        pass


