import discord
from discord.ext import commands
from discord.utils import get
from discord_components import Select, SelectOption
import bot.config as config
import asyncio
import bot.lang as lang

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
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        if not ctx.author.voice:
            return await ctx.reply(embed=discord.Embed(
                description=_["if_not_voice_channel"],
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
            title=_["title"],
            description=_["description"],
            color=self.bot.get_color(self.bot.color.gold)
        )
        embed.set_footer(text=self.bot.footer)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        select = _["select"]
        msg = await ctx.reply(
            embed=embed,
            components=[
                Select(
                    placeholder=select["placeholder"],
                    max_values=1,
                    options=[
                        SelectOption(
                            label=select["options"]["maher"], value="maher", emoji=self.emoji.MaherAlmaikulai),
                        SelectOption(
                            label=select["options"]["yasser"], value="yasser", emoji=self.emoji.YasserAlDousari),
                        SelectOption(
                            label=select["options"]["sudais"], value="sudais", emoji=self.emoji.AbdullrahmanAlsudais),
                        SelectOption(
                            label=select["options"]["baset"], value="baset", emoji=self.emoji.AbdulBasitAbdulSamad),
                        SelectOption(
                            label=select["options"]["islam"], value="islam", emoji=self.emoji.IslamSobhi),
                        SelectOption(
                            label=select["options"]["sourate"], value="sourate", emoji=self.emoji.MisharyAlafasy),
                        SelectOption(
                            label=select["options"]["cancel"], value="7", emoji="❌"),
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
                    description=_["on_play"] % reader,
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
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        try:
            await voice.disconnect()
            await ctx.reply(embed=discord.Embed(
                description=_["disconnect"],
                color=self.bot.get_color(self.bot.color.gold)
            ))
        except AttributeError:
            await ctx.reply(embed=discord.Embed(
                description=_["if_bot_connect"],
                color=self.bot.get_color(self.bot.color.gold)
            ))


def setup(bot):
    bot.add_cog(Quran(bot))
