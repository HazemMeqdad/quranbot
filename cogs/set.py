import discord
from discord.ext import commands
import db


class Set(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='set', invoke_without_command=True, aliases=['اعداد', 'settings'], help='عرض اعدادات الخادم')
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def settings_(self, ctx):
        embed = discord.Embed(
            description='إعدادات خادم: {}'.format(ctx.guild.name),
            color=discord.Color.gold()
        )
        channel = self.client.get_channel(db.get_channel(ctx.guild))
        if channel is not None:
            embed.add_field(name='روم الاذكار', value=channel.mention, inline=False)
        embed.add_field(name='وقت ارسال الاذكار', value=db.get_time(ctx.guild), inline=False)
        embed.add_field(name='البادئه', value=db.get_prefix(ctx.guild), inline=False)
        if db.get_spam(ctx.guild) is True:
            embed.add_field(name='وضع تكرار الرسائل', value="on", inline=False)
        else:
            embed.add_field(name='وضع تكرار الرسائل', value="off", inline=False)
        if db.get_embed(ctx.guild) is True:
            embed.add_field(name='وضع الامبد', value="on", inline=False)
        else:
            embed.add_field(name='وضع الامبد', value="off", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='spam', help='عدم تكرار الرسائل, ينصح باستخدامه في الشاتات المفتوحه للجميع', usage='[on or off]')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def anti_spam(self, ctx, enable=None):
        active = ['on', 'off']
        if enable not in active:
            await ctx.send('يجب تحديد الوضع (on او off)')
            return
        if enable == 'on':
            db.anti_spam(ctx.guild, True)
            await ctx.send('تم تفعيل خاصيه عدم تكرار الاذكار في وقت عدم تفاعل الشات')
        elif enable == 'off':
            db.anti_spam(ctx.guild, False)
            await ctx.send('تم اطفاء خاصيه عدم تكرار الاذكار في وقت عدم تفاعل الشات')

    @commands.command(name='embed', help='تغير خاصيه ارسال الاذكار الى امبد', usage='[on or off]')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def embed_(self, ctx, enable=None):
        active = ['on', 'off']
        if enable not in active:
            await ctx.send('يجب تحديد الوضع (on او off)')
            return
        if enable == 'on':
            db.embed(ctx.guild, True)
            await ctx.send('تم تفعيل خاصيه الأمبد بالأذكار')
        elif enable == 'off':
            db.embed(ctx.guild, False)
            await ctx.send('تم اطفاء خاصيه الأمبد بالأذكار')


def setup(client):
    client.add_cog(Set(client))
