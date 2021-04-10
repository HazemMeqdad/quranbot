import discord
from discord.ext import commands
from discord.utils import get


class Play(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['c', 'connect'], help='لانضمام البوت الى الروم الصوتي')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("يجب عليك دخول غرفه صوتيه")
            return
        channel = ctx.author.voice.channel
        voice = get(self.client.voice_clients, guild=ctx.guild)

        try:
            await channel.connect()
        except discord.errors.ClientException:
            await voice.move_to(channel)
        except discord.Forbidden:
            await ctx.send('البوت لا يمتلك الصلاحيات الكافيه لدخول الغرقه الصوتيه')
            return
        await ctx.send("تم الاتصال في `{}`".format(channel))

    @commands.command(name='play', help='تشغيل القران الكريم على مدار 24 ساعه', aliases=['quren'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def play_command(self, ctx):
        if not ctx.author.voice:
            await ctx.send("يجب عليك دخول غرفه صوتيه")
            return

        channel = ctx.author.voice.channel
        voice = get(self.client.voice_clients, guild=ctx.guild)
        try:
            try:
                voice_channel = await channel.connect()
            except discord.errors.ClientException:
                voice_channel = await voice.move_to(channel)
            else:
                await ctx.send('القران الكريم يعمل الان في `{}`'.format(channel))
        except discord.Forbidden:
            await ctx.send('البوت لا يمتلك الصلاحيات الكافيه لدخول الغرقه الصوتيه')
            return
        except discord.ClientException:
            await ctx.send('القران الكريم يعمل الان')
            return
        qran = discord.FFmpegPCMAudio('quren.m4a')
        try:
            voice_channel.play(qran)
            voice.loop()
            await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
        except AttributeError:
            await ctx.send('القران الكريم قيد العمل الان')

    @commands.command(aliases=['disconnect', 'dc'], help='لايقاف القران الكريم')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(self, ctx):
        voice = get(self.client.voice_clients, guild=ctx.guild)
        try:
            await voice.disconnect()
            await ctx.send('تم مغادره الروم الصوتي')
        except AttributeError:
            await ctx.send('البوت ليس موجود في روم صوتي')


def setup(client):
    client.add_cog(Play(client))
