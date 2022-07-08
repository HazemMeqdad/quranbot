import hikari
import lightbulb
from bot.utils import voice

takbeerat = lightbulb.Plugin(__name__)


@takbeerat.command
@lightbulb.command("takbeerat", "تشغيل تكبيرات العيد بالروم الصوتية")
@lightbulb.implements(lightbulb.commands.SlashCommand)
async def takbeerat_command(ctx: lightbulb.SlashContext):
    await ctx.respond(response_type=hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    channel_id = await voice.join_voice_channel(ctx.bot, ctx.guild_id, ctx.author)
    embed = hikari.Embed(color=0xffd430)
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)

    if not channel_id:
        embed.description = "يجب عليك دخول قناة صوتية"
        await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)
        return

    await voice.play_lavalink_source(ctx.bot.lavalink, ctx.guild_id, "https://youtu.be/IrfImfO4Pes", ctx.author)
    await ctx.bot.lavalink.repeat(ctx.guild_id, True)
    embed.description = "تم تشغيل تكبيرات العيد في روم <#%s>" % channel_id
    await ctx.respond(embed=embed)


def load(bot: lightbulb.BotApp):
    bot.add_plugin(takbeerat)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(takbeerat)
