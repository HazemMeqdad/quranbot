import discord
from discord.ext import commands
from discord.utils import get
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
import bot.config as config
import asyncio


class Quran(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)
        self.color = config.Color()

    @commands.command(name='play', help='تشغيل القران الكريم على مدار 24 ساعه', aliases=['quren'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def play_command(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("يجب عليك دخول غرفه صوتيه")
        channel = ctx.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        try:
            voice_channel = await channel.connect()
        except discord.errors.ClientException:
            voice_channel = await voice.move_to(channel)
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
        list_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '❌']
        m = await ctx.send(embed=discord.Embed(description="الرجاء الانتضار بعض الثواني %s" % self.emoji.loading))
        for i in list_emojis:
            await m.add_reaction(i)
        embed = discord.Embed(
            description="""
اختر القارئ المناسب:
> :one: - ماهر المعيقلي
> :two: - ياسر الدوسري
> :three: - عبد الرحمن السديس
> :four: - عبد الباسط عبد الصمد
> :five: - اسلام صبحي
> :six: - مشاري بن راشد العفاسي
> :x: - الغاء الامر
            """)
        await m.edit(embed=embed)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in list_emojis
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30)
        except asyncio.TimeoutError:
            return await m.delete()
        else:
            # -----------------------------------------------------------------------
            _id = {"1️⃣": "maher", "2️⃣": "yasser", "3️⃣": "sudais", "4️⃣": "baset", "5️⃣": "islam", "6️⃣": "sourate"}
            name = {
                "maher": "ماهر المعيقلي",
                "yasser": "ياسر الدوسري",
                "sudais": "عبد الرحمن السديس",
                "baset": "عبد الباسط عبد الصمد",
                "islam": "اسلام صبحي",
                "sourate": "مشاري بن راشد العفاسي"
            }
            # -----------------------------------------------------------------------
            qran = discord.FFmpegPCMAudio('bot/quran/%s.m4a' % _id.get(str(reaction.emoji)))
            embed = discord.Embed(
                description="تم تشغيل القرآن الكريم بصوت الشيخ: `%s`" % name.get(_id.get(str(reaction.emoji)))
            )
            await m.edit(embed=embed)

            def repeat(guild, voice, audio):
                voice.play(audio, after=lambda e: repeat(guild, voice, audio))
                voice.is_playing()
            voice_channel.play(qran, after=lambda e: repeat(ctx.guild, voice, qran))

    @commands.command(aliases=['disconnect', 'dc'], help='لايقاف القران الكريم')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        try:
            await voice.disconnect()
            await ctx.send('تم مغادره الروم الصوتي')
        except AttributeError:
            await ctx.send('البوت ليس موجود في روم صوتي')


def setup(bot):
    DiscordComponents(bot)
    bot.add_cog(Quran(bot))
