import hikari
from hikari.messages import MessageFlag
import lightbulb
from lightbulb import commands
from lightbulb.app import BotApp
from lightbulb.context.slash import SlashContext
from lightbulb.utils import nav, pag
import json

moshaf_plugin = lightbulb.Plugin("المصحف الشريف")

BASE = "http://quran.ksu.edu.sa/ayat/safahat1"

pages = [f"{BASE}/{i}.png" for i in range(604)]
quran_surahs = json.load(open("bot/json/quran_surahs.json", "r", encoding="utf-8"))


@moshaf_plugin.command()
@lightbulb.command("moshaf", "القرآن الكريم")
@lightbulb.implements(commands.SlashCommandGroup, commands.SlashSubGroup)
async def moshaf(ctx: SlashContext):
    ...


@moshaf.child()
@lightbulb.command("pages", "عرض صفحات القرآن الكريم")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def moshaf_pages(ctx: SlashContext):    
    paginated = pag.EmbedPaginator(
        max_lines=None,
        max_chars=50,
        prefix="",
        suffix="",
        line_separator="/n",
    )

    paginated.set_embed_factory(lambda i, s: hikari.Embed(
        color=0xffd430).set_image(s).set_footer(text=f"صفحه {i}/{len(pages)}"))

    for l in pages:
        paginated._add_one_line(l)
    navigator = nav.ButtonNavigator(paginated.build_pages(page_number_start=1))
    await navigator.run(ctx)


@moshaf.child()
@lightbulb.option(
    name="page_number",
    description="رقم الصفحة",
    type=int,
    required=True
)
@lightbulb.command("page", "عرض صفحه محدده من القرآن الكريم")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def moshaf_page(ctx: SlashContext):
    embed = hikari.Embed(color=0xffd430)
    page = ctx.options.page_number

    if page > 604 or page < 0:
        embed.description = "خطأ في رقم الصفحه مع العلم أن عدد صفحات القرآن الكريم 604 صفحه"
        await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)
        return
    
    embed.set_image(pages[page])
    embed.set_footer(f"صفحه {page}/{len(pages)}")
    await ctx.respond(embed=embed)

@moshaf.child()
@lightbulb.command("surahs", "عرض جميع سور القرآن الكريم")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def moshaf_surahs(ctx: SlashContext):
    paginated = pag.EmbedPaginator(max_lines=25)

    for surah, line in quran_surahs.items():
        paginated.add_line(f"{surah}- {line}")

    paginated.set_embed_factory(lambda i, s: (
        hikari.Embed(color=0xffd430, description=s)
        .set_thumbnail(ctx.bot.get_me().avatar_url.url)
        .set_footer(f"الصفحة رقم {i}/{len(paginated._pages)}")
    ))

    navigator = nav.ButtonNavigator(paginated.build_pages())
    await navigator.run(ctx)


def load(bot: BotApp):
    bot.add_plugin(moshaf_plugin)

def unload(bot: BotApp):
    bot.remove_plugin(moshaf_plugin)

