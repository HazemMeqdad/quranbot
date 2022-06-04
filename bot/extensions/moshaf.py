import logging
import hikari
from hikari import ButtonStyle, InteractionType, MessageFlag, CommandChoice, ResponseType
import lightbulb
from lightbulb import commands
from lightbulb.app import BotApp
from lightbulb.context.slash import SlashContext
from lightbulb.utils import nav, pag
import json
import aiohttp
from requests import request
from PIL import Image
import io
from bot.utils import voice

moshaf_plugin = lightbulb.Plugin("المصحف الشريف")

BASE = "https://cdn.fdrbot.com/moshaf"

pages = [f"{BASE}/{i+1}.png" for i in range(604)]
quran_surahs = json.load(open("bot/json/quran_surahs.json", "r", encoding="utf-8"))
cloud_surahs = []

async def fetch_surahs():
    global cloud_surahs
    async with aiohttp.ClientSession() as session:
        async with session.get("http://api.alquran.cloud/v1/quran/ar.alafasy") as resp:
            res = await resp.json()
            cloud_surahs = res["data"]["surahs"]
            logging.info(f"Loaded {len(cloud_surahs)} surahs from cloud")

def image_bytes(url: str) -> bytes:
    res = request("GET", url)
    file = io.BytesIO(res.content)

    img = Image.open(file)
    background = Image.new(mode="RGB", size=(img.width, img.height))
    background.paste(img.copy(), (0, 0, img.width, img.height))
    buf = io.BytesIO()
    background.save(buf, format='JPEG')
    return buf.getvalue()


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
        color=0xffd430)
        .set_image(s)
        .set_footer(text=f"صفحه {i}/{len(pages)}")
    )

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
    embed.set_image(image_bytes(pages[page]))
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


@moshaf.child()
@lightbulb.option(
    name="surah",
    description="السورة المطلوبة",
    autocomplete=True,
    required=True
)
@lightbulb.option(
    name="ayah",
    description="الآية المطلوبة",
    type=int,
    required=True
)
@lightbulb.command("ayah", "عرض آية محددة القرآن الكريم")
@lightbulb.implements(commands.SlashSubCommand, commands.PrefixSubCommand)
async def moshaf_ayah(ctx: SlashContext):
    embed = hikari.Embed(color=0xffd430)
    surah = ctx.options.surah
    ayah = ctx.options.ayah

    if not surah.isdigit() or int(surah) > 114 or int(surah) < 0:
        embed.description = "خطأ في رقم السوره مع العلم أن عدد سور القرآن الكريم 114 سوره"
        await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)
        return

    surah_name = quran_surahs.get(surah)
    cloud_data = cloud_surahs[int(surah) - 1]

    if int(ayah) > len(cloud_data["ayahs"]) or int(ayah) < 0:
        embed.description = f"خطأ في رقم الآية مع العلم أن عدد آيات سورة {surah_name} {len(cloud_data['ayahs'])} آية"
        await ctx.respond(embed=embed, flags=MessageFlag.EPHEMERAL)
        return

    embed.set_image(image_bytes(f"http://cdn.islamic.network/quran/images/{surah}_{ayah}.png"))
    embed.set_footer(f"الآية {ayah}/{quran_surahs[surah]}")

    component = ctx.bot.rest.build_action_row()
    (
        component.add_button(ButtonStyle.PRIMARY, f"{surah}_{ayah}")
        .set_label("تشغيل")
        .set_emoji("▶️")
        .add_to_container()
    )
    await ctx.respond(embed=embed, components=[component])

@moshaf_ayah.autocomplete("surah")
async def quran_autocomplete(ctx: SlashContext, query: hikari.AutocompleteInteraction):
    option = query.options[0].options[1].value
    if not option:
        return [CommandChoice(name=i[1], value=str(i[0])) for i in quran_surahs.items()][:25]
    return [CommandChoice(name=i[1], value=str(i[0])) for i in quran_surahs.items() if option in i[1]][:25]


@moshaf_plugin.listener(hikari.InteractionCreateEvent)
async def moshaf_interaction_create(event: hikari.InteractionCreateEvent):
    embed = hikari.Embed(color=0xffd430)
    if event.interaction.type == InteractionType.MESSAGE_COMPONENT and event.interaction.get_parent_message().components[0].components[0].label == "تشغيل":
        embed = hikari.Embed(color=0xffd430)
        voice_state = await voice.join_voice_channel(moshaf_plugin.bot, event.interaction.guild_id, event.interaction.user)
        if not voice_state:
            embed.description = "يجب عليك دخول قناة صوتيه"
            await event.app.rest.create_interaction_response(
                interaction=event.interaction, 
                token=event.interaction.token, 
                response_type=ResponseType.MESSAGE_CREATE,
                embed=embed,
                flags=MessageFlag.EPHEMERAL
            )
            return
        surah = event.interaction.custom_id.split("_")[0]
        ayah = event.interaction.custom_id.split("_")[1]
        audio = cloud_surahs[int(surah) - 1]["ayahs"][int(ayah) - 1]["audio"]
        embed.description = f"تم تشغيل الآية رقم {ayah} من سورة {quran_surahs[surah]} بصوت القارئ **ياسر الدوسري**"
        await event.app.rest.create_interaction_response(
            interaction=event.interaction, 
            token=event.interaction.token, 
            response_type=ResponseType.MESSAGE_CREATE,
            embed=embed,
        )
        await voice.play_lavalink_source(
            lavalink=moshaf_plugin.bot.lavalink,
            guild=event.interaction.guild_id,
            source=audio,
            user=event.interaction.user
        )




def load(bot: BotApp):
    bot.loop.create_task(fetch_surahs())
    bot.add_plugin(moshaf_plugin)

def unload(bot: BotApp):
    bot.remove_plugin(moshaf_plugin)

