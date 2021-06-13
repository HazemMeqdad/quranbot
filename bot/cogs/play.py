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
        embed = discord.Embed(description='اختر القارىء المناسب')
        m = await ctx.send(
            embed=embed,
            components=[
                [
                    Button(style=ButtonStyle.green, label="ماهر المعيقلي", id='maher'),
                    Button(style=ButtonStyle.green, label="ياسر الدوسري", id='yasser'),
                    Button(style=ButtonStyle.green, label="عبد الرحمن السديس", id='sudais'),
                    Button(style=ButtonStyle.green, label="عبد الباسط عبد الصمد", id='baset'),
                ],
                [
                    Button(style=ButtonStyle.green, label="اسلام صبحي", id='islam'),
                    Button(style=ButtonStyle.green, label="مشاري بن راشد العفاسي", id='sourate'),
                ]
            ]
        )

        def check(res):
            return ctx.author == res.author and res.channel == ctx.channel

        try:
            res = await self.bot.wait_for("button_click", check=check, timeout=15)
        except asyncio.TimeoutError:
            return await m.delete()
        else:
            await res.respond(
                type=InteractionType.ChannelMessageWithSource,
                content="يتم الان تشغيل القرآن الكريم بصوت الشيخ: `%s`" % res.component.label
            )
            await m.edit(
                embed=discord.Embed(
                    description="يتم الان تشغيل القرآن الكريم بصوت الشيخ: `%s`" % res.component.label,
                    color=self.color.green
                ),
                components=[
                    Button(style=ButtonStyle.green, label=res.component.label, disabled=True),
                ],
            )
            qran = discord.FFmpegPCMAudio('bot/quran/%s.m4a' % res.component.id)
            await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

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
