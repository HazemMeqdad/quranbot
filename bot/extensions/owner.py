import lightbulb
import hikari
from lightbulb import Plugin, commands
from lightbulb.context import SlashContext
import inspect
import logging

owner_plugin = Plugin("owner")
guild_id = [843710915861545000]

@owner_plugin.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option(
    name="code", 
    description="أدخل الكود المراد تشغيله",
    required=True
)
@lightbulb.command("eval", "eval command", guilds=guild_id)
@lightbulb.implements(commands.SlashCommand)
async def _eval(ctx: SlashContext):
    code = ctx.options.code
    to_eval = code.replace("await ", "")
    try:
        result = eval(to_eval)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        result = "%s: %s" % (type(e).__name__, str(e))
    result = str(result)
    embed = hikari.Embed(description="Eval Result")
    embed.add_field(name="Input 📥", value=f"```py\n{code}```", inline=False)
    embed.add_field(name="Output 📤", value=f"```py\n{result}```", inline=False)
    await ctx.respond(embed=embed, reply=True, mentions_reply=False)


@owner_plugin.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option(
    name="extension",
    description="None",
    required=True
)
@lightbulb.command("load", "load command", guilds=guild_id)
@lightbulb.implements(commands.SlashCommand)
async def load_extension(ctx: SlashContext):
    extension = ctx.options.extension
    try:
        ctx.bot.load_extensions(f"bot.extensions.{extension}")
        logging.info(f"extension '{extension}' loaded")
        await ctx.respond(f"loaded {extension} extension")
    except Exception as error:
        await ctx.respond(error.__str__)


@owner_plugin.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option(
    name="extension",
    description="None",
    required=True
)
@lightbulb.command("unload", "unload command", guilds=guild_id)
@lightbulb.implements(commands.SlashCommand)
async def load_extension(ctx: SlashContext):
    extension = ctx.options.extension
    try:
        ctx.bot.unload_extensions(f"bot.extensions.{extension}")
        logging.info(f"extension '{extension}' unloaded")
        await ctx.respond(f"unloaded {extension} extension")
    except Exception as error:
        await ctx.respond(error.__str__)


@owner_plugin.command()
@lightbulb.add_checks(lightbulb.owner_only)
@lightbulb.option(
    name="extension",
    description="None",
    required=True
)
@lightbulb.command("reload", "reload command", guilds=guild_id)
@lightbulb.implements(commands.SlashCommand)
async def load_extension(ctx: SlashContext):
    extension = ctx.options.extension
    try:
        ctx.bot.reload_extensions(f"bot.extensions.{extension}")
        logging.info(f"extension '{extension}' reloaded")
        await ctx.respond(f"reloaded {extension} extension")
    except Exception as error:
        await ctx.respond(error.__str__)


def load(bot):
    bot.add_plugin(owner_plugin)


def unload(bot):
    bot.remove_plugin(owner_plugin)
