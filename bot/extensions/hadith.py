import asyncio
import hikari
import lightbulb
import random
from dataclasses import dataclass
import aiohttp

hadith_plugin = lightbulb.Plugin("hadith")

@dataclass
class Hadith:
    book_id: int
    chapter_id: int
    hadith_id: int    
    text: str
    sanad: str

    def __repr__(self) -> str:
        return self.text

hadiths = []
books = []
chapters = []

async def fetch_data():
    global hadiths, books, chapters
    async with aiohttp.ClientSession() as session:
        
        async with session.get("https://ahadith-api.herokuapp.com/api/ahadith/all/ar-tashkeel") as response:
            data = await response.json()
            hadiths = [Hadith(book_id=i["Book_ID"], chapter_id=i["Chapter_ID"], hadith_id=i["Hadith_ID"], text=i["Ar_Text"], sanad=i["Ar_Sanad_1"]) for i in data["AllChapters"]]
        
        async with session.get("https://ahadith-api.herokuapp.com/api/books/ar") as response:
            data = await response.json()
            books = {x["Book_ID"]: x["Book_Name"] for x in data["Books"]}

        async with session.get("https://ahadith-api.herokuapp.com/api/chapter/all/ar") as response:
            data = await response.json()
            chapters = [x for x in data["AllChapters"]]

@hadith_plugin.command()
@lightbulb.command("hadith", "الأحاديث")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def hadith(ctx: lightbulb.SlashContext):
    ...


@hadith.child()
@lightbulb.command("random", "البحث عن حديث بشكل عشوائي")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def random_command(ctx: lightbulb.SlashContext):
    hadith = random.choice(hadiths)
    embed = hikari.Embed(
        title=books[hadith.book_id],
        description="%s %s" % (hadith.sanad, hadith.text),
        color=0xffd430
    )
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    await ctx.respond(embed=embed)


@hadith.child()
@lightbulb.option("book", "السورة", autocomplete=True, required=True)
@lightbulb.command("book", "البحث عن حديث بشكل عشوائي")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def book_command(ctx: lightbulb.SlashContext):
    book = ctx.options.book
    try:
        chapter = [x for x in chapters if x["Book_ID"] == int(book)][0]
    except IndexError:
        embed = hikari.Embed(
            title="خطأ",
            description="عذراً هذا الكتاب غير موجود",
            color=0xff0000
        )
        embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
        await ctx.respond(embed=embed)
        return
    embed = hikari.Embed(
        title=chapter["Chapter_Name"].replace("1 - ", ""),
        description=chapter["Chapter_Intro"],
        color=0xffd430
    )
    embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
    await ctx.respond(embed=embed)

@book_command.autocomplete("book")
async def autocomplete_book(ctx: lightbulb.SlashContext, query: hikari.AutocompleteInteraction):
    option = query.options[0].options[0].value
    if not option:
        return [hikari.CommandChoice(name=i[1], value=str(i[0])) for i in books.items()]
    return [hikari.CommandChoice(name=i[1], value=str(i[0])) for i in list(books.items()) if option in i[1]]

@hadith.child()
@lightbulb.option("query", "البحث عن حديث", required=True, autocomplete=True)
@lightbulb.command("search", "البحث عن حديث")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def search_command(ctx: lightbulb.SlashContext):
    query = ctx.options.query
    result = [x for x in hadiths if query.lower() in x.text.lower()][0]
    if not result:
        embed = hikari.Embed(
            description="لا يوجد نتائج",
            color=0xffd430
        )
        embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
        await ctx.respond(embed=embed)
    else:
        embed = hikari.Embed(
            title="نتائج البحث",
            description=("%s %s" % (result.sanad, result.text))[:2087],
            color=0xffd430
        )
        embed.set_footer(text=ctx.bot.footer, icon=ctx.bot.get_me().avatar_url)
        await ctx.respond(embed=embed)

@search_command.autocomplete("query")
async def autocomplete_query(ctx: lightbulb.SlashContext, query: hikari.AutocompleteInteraction):
    option = query.options[0].options[0].value
    if not option:
        return [hikari.CommandChoice(name=i.text[:99], value=str(i.hadith_id)) for i in hadiths][:24]
    return [hikari.CommandChoice(name=i.text[:99], value=str(i.hadith_id)) for i in hadiths if option in i.text][:24]


def load(bot: lightbulb.BotApp):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.create_task(fetch_data())
    bot.add_plugin(hadith_plugin)

def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(hadith_plugin)