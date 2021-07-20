import discord
from discord.ext import commands
from discord.utils import get
from discord_components import Select, SelectOption
import bot.config as config
import asyncio

last = {}


class Quran(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)

    @commands.command(name='play', help='تشغيل القران الكريم على مدار 24 ساعه', aliases=['quren'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def play_command(self, ctx):
        if not ctx.author.voice:
            return await ctx.send(embed=discord.Embed(
                description="يجب عليك دخول غرفه صوتيه",
                color=self.bot.get_color(self.bot.color.gold)
            ))
        channel = ctx.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        try:
            voice_channel = await channel.connect()
        except discord.errors.ClientException:
            voice_channel = await voice.move_to(channel)
        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
        embed = discord.Embed(
            title="تشغيل القرآن الكريم",
            description="اختر القارئ المناسب من القائمة في الأسفل!",
            color=self.bot.get_color(self.bot.color.gold)
        )
        embed.set_footer(text=self.bot.footer)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        msg = await ctx.send(
            embed=embed,
            components=[
                Select(
                    placeholder="اختر القارئ المناسب",
                    max_values=1,
                    options=[
                        SelectOption(label="ماهر المعيقلي", value="maher", emoji=self.emoji.MaherAlmaikulai),
                        SelectOption(label="ياسر الدوسري", value="yasser", emoji=self.emoji.YasserAlDousari),
                        SelectOption(label="عبد الرحمن السديس", value="sudais", emoji=self.emoji.AbdullrahmanAlsudais),
                        SelectOption(label="عبد الباسط عبد الصمد", value="baset", emoji=self.emoji.AbdulBasitAbdulSamad),
                        SelectOption(label="اسلام صبحي", value="islam", emoji=self.emoji.IslamSobhi),
                        SelectOption(label="مشاري بن راشد العفاسي", value="sourate", emoji=self.emoji.MisharyAlafasy),
                        SelectOption(label="الغاء", value="7", emoji="❌"),
                    ],
                ),
            ],
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel

        try:
            res = await self.bot.wait_for("select_option", check=check, timeout=30)
            value = list(map(lambda x: x.value, res.component))[0]
            reader = list(map(lambda x: x.label, res.component))[0]
            if value == "7":
                return await msg.delete()
            await res.respond(
                embed=discord.Embed(
                    description="تم تشغيل القرآن الكريم بصوت الشيخ: **%s**" % reader,
                    color=self.bot.get_color(self.bot.color.gold)
                ),
                ephemeral=False
            )
            await msg.delete()
            qran = discord.FFmpegOpusAudio('bot/quran/%s.m4a' % value)
            if not last.get(ctx.guild.id):
                last[ctx.guild.id] = None
            last[ctx.guild.id] = value

            def repeat(guild, voice):
                x = discord.FFmpegOpusAudio(f"bot/quran/{last[ctx.guild.id]}.m4a")
                if not x:
                    return
                voice.play(x, after=lambda e: repeat(guild, voice))
            voice_channel.play(qran, after=lambda e: repeat(ctx.guild, voice))
        except asyncio.TimeoutError:
            await msg.delete()

    @commands.command(aliases=['disconnect', 'dc'], help='لايقاف القران الكريم')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        try:
            await voice.disconnect()
            await ctx.send(embed=discord.Embed(
                description="تم مغادره الروم الصوتي",
                color=self.bot.get_color(self.bot.color.gold)
            ))
        except AttributeError:
            await ctx.send(embed=discord.Embed(
                description='البوت ليس موجود في روم صوتي',
                color=self.bot.get_color(self.bot.color.gold)
            ))


def setup(bot):
    bot.add_cog(Quran(bot))
