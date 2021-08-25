import discord
from discord.ext import commands
from discord.utils import get
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
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        select = _["select"]
        view = discord.ui.View()
        selected = discord.ui.Select(placeholder=select["placeholder"])
        data = {
            "maher": [select["options"]["maher"], self.emoji.MaherAlmaikulai],
            "yasser": [select["options"]["yasser"], self.emoji.YasserAlDousari],
            "sudais": [select["options"]["sudais"], self.emoji.AbdullrahmanAlsudais],
            "baset": [select["options"]["baset"], self.emoji.AbdulBasitAbdulSamad],
            "islam": [select["options"]["islam"], self.emoji.IslamSobhi],
            "sourate": [select["options"]["sourate"], self.emoji.MisharyAlafasy],
            "7": [select["options"]["cancel"], "❌"]
        }
        for item, value in data.items():
            selected.append_option(discord.SelectOption(label=value[0], value=item, emoji=value[1]))
        view.add_item(item=selected)
        msg = await ctx.reply(embed=embed, view=view)

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel

        try:
            res = await self.bot.wait_for("interaction", check=check, timeout=30)
            value = res.data.get("values")[0]
            lable = data.get(value)
            if value == "7":
                return await msg.delete()
            selected.disabled = True
            await res.edit_original_message(
                embed=discord.Embed(
                    description=_["on_play"] % lable[0],
                    color=self.bot.get_color(self.bot.color.gold)
                ),
                view=view
            )
            qran = discord.FFmpegOpusAudio('bot/quran/%s.m4a' % "quren")
            if not last.get(ctx.guild.id):
                last[ctx.guild.id] = None
            last[ctx.guild.id] = value

            def repeat(guild, voice):
                if not last.get(ctx.guild.id) or voice_channel.is_connected() == False:
                    return
                x = discord.FFmpegOpusAudio(f"bot/quran/{last[ctx.guild.id]}.m4a")
                if not x:
                    return
                voice_channel.play(x, after=lambda e: repeat(guild, voice))
            voice_channel.play(qran, after=lambda e: repeat(ctx.guild, voice_channel))
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
