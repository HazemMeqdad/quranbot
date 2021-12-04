import hikari
from hikari.messages import ButtonStyle
import lightbulb
from lightbulb.plugins import Plugin
from lightbulb.commands import PrefixCommand

commands = [
    "play",
    "live",
    "stop",
    "join",
    "vol",
    "ping",
    "support",
    "info",
    "zker",
    "azan",
    "bot",
    "prefix",
    "spam",
    "embed",
    "time",
    "setroom",
    "remove",
]


async def send_stop_message(ctx: lightbulb.context.Context):
    embed = hikari.Embed(
        description="نعتذر منك تم إيقاف جميع الأوامر التي تستعمل بادئه اصبح بأمكانك أستعمال أوامر الشرطة  المائل <:slash:892371771049771008> عوضا عن ذلك"
        "\nاذا كنت تعاني من مشاكله بالعثور على الأوامر أستعمل أمر `{}fix`".format(ctx.prefix),
        color=0xffd430
    )
    embed.set_image("https://i.imgur.com/f8gT1WR.gif")
    button_row = ctx.bot.rest.build_action_row()
    button_row = (
        button_row.add_button(
            ButtonStyle.LINK, "https://discord.gg/VX5F54YNuy")
        .set_label("الدعم الفني")
        .add_to_container()
    )
    await ctx.respond(embed=embed, component=button_row, reply=True, mentions_reply=False)


old_commands_plugin = Plugin("old_commands")

@old_commands_plugin.command()
@lightbulb.command("old", "old commands", aliases=commands)
@lightbulb.implements(PrefixCommand)
async def old_commands(ctx: lightbulb.context.Context):
    await send_stop_message(ctx)

@old_commands_plugin.command()
@lightbulb.command("fix", "fix command")
@lightbulb.implements(PrefixCommand)
async def fix(ctx: lightbulb.context.Context):
    text = (
        "**كيف اضيف أوامر الشرطة المائلة(السلاش كوماند) <:slash:892371771049771008> ؟**"
        "\n`-` يجيب عليك طرد البوت و أضافتة من جديد من خلال هاذ الرابط https://fdrbot.xyz/invite"
        "\n\n**لقد أعادة أضافه البوت من الرابط و لاكن لم يتم أضافة الأوامر 🤔؟**"
        "\n`-` التاكد من تفعيل صلاحيه `Use Application Commands` لرتبه الجميع في قناة الأوامر"
        "\n`-` التاكد من تفعيل صلاحيه `Use Application Commands` لرتبه الجميع"
    )
    embed = hikari.Embed(
        description=text,
        color=0xffd430
    )
    embed.set_image("https://i.imgur.com/f8gT1WR.gif")
    button_row = ctx.bot.rest.build_action_row()
    button_row = (
        button_row.add_button(
            ButtonStyle.LINK, "https://discord.gg/VX5F54YNuy")
        .set_label("الدعم الفني")
        .add_to_container()
    )
    await ctx.respond(embed=embed, component=button_row, reply=True, mentions_reply=False)

def load(bot):
    bot.add_plugin(old_commands_plugin)


def unload(bot):
    bot.remove_plugin(old_commands_plugin)
