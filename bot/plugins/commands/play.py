from os import name
import hikari
import lavasnek_rs
import lightbulb
from lightbulb.context import Context
from bot.bot import Bot
from asyncio import TimeoutError
from bot.utils import al_shyke, stop, join_voice_channel


class Quran(lightbulb.Plugin):
    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__()

    @lightbulb.command(name="play")
    async def play_command(self, ctx: Context):
        raw = ctx.bot.rest.build_action_row()
        menu = raw.add_select_menu("quran")
        menu.set_placeholder("اختر القارئ المناسب")
        menu.set_max_values(1)
        menu.set_min_values(1)
        menu.set_is_disabled(False)
        menu.add_to_container()

        embed = hikari.Embed(color=0xffd430)
        options = {
            "1": "ماهر المعيقلي",
            "2": "ياسر الدوسري",
            "3": "عبدالرحمن السديس",
            "4": "عبدالباسط عبدالصمد",
            "5": "اسلام صبحي",
            "6": "مشاري بن راشد العفاسي",
            "0": "الغاء"
        }
        for value, label in options.items():
            if value == "0":
                menu.add_option(label, value).set_emoji("❌").add_to_menu()
                continue
            menu.add_option(label, value).add_to_menu()
        await join_voice_channel(ctx)
        embed.description = "اختر القارئ المناسب من القائمة في الأسفل!"
        msg = await ctx.respond(embed=embed, component=raw, reply=True, mentions_reply=False)
        menu.set_is_disabled(True)

        def check(res):
            return res.interaction.user.id == ctx.author.id and \
                res.interaction.channel_id == ctx.channel_id
        try:
            event = await ctx.bot.wait_for(hikari.InteractionCreateEvent, predicate=check, timeout=15)
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE)
        except TimeoutError:
            embed.description = "تم الغاء الامر"
            await msg.edit(embed=embed, component=raw)
            await stop(ctx)
            return
        value = event.interaction.values[0]

        if value == "0":
            embed.description = "تم الغاء الامر بسبب انتهاء الوقت الازم"
            await msg.edit(embed=embed, component=raw)
            await stop(ctx)
            return
        
        information = await self.bot.lavalink.auto_search_tracks(al_shyke.get(value))
        await self.bot.lavalink.play(ctx.guild_id, information.tracks[0]).requester(ctx.author.id).queue()
        embed.description = "تم تشغيل القرآن الكريم بصوت الشيخ: **%s**" % options.get(value)
        menu.set_placeholder("تم تشغيل القرآن الكريم: %s" % options.get(value))
        await msg.edit(embed=embed, component=raw)

    @lightbulb.command(name="live")
    async def live_quran(self, ctx: Context):
        channel_id = await join_voice_channel(ctx)
        if channel_id == 0:
            return
        embed = hikari.Embed(color=0xffd430)
        information = await self.bot.lavalink.get_tracks("https://qurango.net/radio/tarateel")
        await self.bot.lavalink.play(ctx.guild_id, information.tracks[0]).requester(ctx.author.id).queue()
        embed.description = "تم تشغيل أذاعة القران الكريم في روم <#%s>" % channel_id
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)

    @lightbulb.command(name="stop")
    async def stop_command(self, ctx: Context):
        data = await stop(ctx)
        embed = hikari.Embed(color=0xffd430)
        if not data:
            embed.description = "البوت ليس موجود في روم صوتي"
            await ctx.respond(embed=embed, reply=True, mentions_reply=False)
            return
        embed.description = "تم مغادره الروم الصوتي"
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)
        
    @lightbulb.command(name="join")
    async def join(self, ctx: Context):
        channel_id = await join_voice_channel(ctx)
        embed = hikari.Embed(color=0xffd430)
        if isinstance(channel_id, hikari.Embed):
            await ctx.respond(embed=channel_id, reply=True, mentions_reply=False)
            return
        embed.description = "تم انظمام البوت الى <#%s>" % channel_id
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)

    @lightbulb.command(name="vol")
    async def volume_command(self, ctx: Context, vol: int):
        embed = hikari.Embed(color=0xffd430)
        if vol > 100 or vol < 0:
            embed.description = "الصوت المتاح من 0 - 100"
            await ctx.respond(embed=embed, reply=True, mentions_reply=False)
            return
        self.bot.lavalink.volume(ctx.guild_id, vol)
        embed.description = f"تم تغير مستوى الصوت إلى `{vol}%`"
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)

def load(bot: Bot):
    bot.add_plugin(Quran(bot=bot))


def unload(bot: Bot):
    bot.remove_plugin("Quran")
