import discord
import typing as t
import lavalink


def get_quran_embed(player: lavalink.DefaultPlayer, audio_track: t.Optional[lavalink.AudioTrack] = None, *, reader: t.Optional[str] = None, user_id: int) -> discord.Embed:
    track = player.current or audio_track
    embed = discord.Embed(
        title="القرآن الكريم",
        color=0xffd430
    )
    embed.add_field(name="القارئ:", value=reader or track.author)
    if not track.title.lower().startswith("http"):
        embed.add_field(name="السورة:", value=track.title)
    embed.add_field(name="المستوى:", value=player.volume)
    embed.add_field(name="الحالة:", value="متوقف" if player.paused else "مشغل")
    if len(player.queue) > 1:
        embed.add_field(name="القادم:", value=f"{player.queue[1].title}")
        embed.add_field(name="عدد السور المتبقية بالقراءة:", value=f"{len(player.queue)}")
    if track:
        embed.add_field(name="مشغل من:", value="اذاعة القرآن الكريم" if track.uri.lower().startswith("https://qurango.net/radio") else "القرآن الكريم")
    embed.add_field(name="المستخدم:", value=f"<@{user_id}>")
    loop = ["غير مفعل", "السورة فقط", "القرآن الكريم كامل"]
    embed.add_field(name="حالة التكرار", value=loop[player.loop])
    return embed

def prosses_pray_embed(pray: t.Dict[str, t.Any], user_avatar: str) -> discord.Embed:
    embed = discord.Embed(
        title=pray["category"],
        description=pray["zekr"],
        color=0xffd430,
    )
    embed.set_thumbnail(url=user_avatar)
    embed.set_footer(text="بوت فاذكروني لإحياء سنة ذِكر الله", icon_url=user_avatar)
    if pray.get("description") and pray.get("description").get("arabic"):
        embed.add_field(name="وصف", value=pray["description"]["arabic"], inline=False)
    if pray.get("reference") != False:
        embed.add_field(name="المرجعي", value=pray["reference"])
    if pray.get("number") != False:
        embed.add_field(name="تكرار", value=pray["number"])
    return embed