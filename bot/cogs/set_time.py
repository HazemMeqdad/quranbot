from discord.ext import commands
from bot import db


class Time(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="time", aliases=["set_time", "settime"], help='تغير وقت ارسال الاذكار', usage='[الوقت]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_timer(self, ctx, time: str = None):
        times = ['30m', '1h', '2h', '6h', '12h', '24h']
        if db.get_channel(ctx.guild) is None:
            await ctx.send("يجب عليك تثبيت روم لاستعمال هاذ الامر `setroom{}`".format(db.get_prefix(ctx.guild)))
            return
        if time is None:
            await ctx.send("يجب تحديد الوقت مثل: `time 30m{}`".format(db.get_prefix(ctx.guild)))
            return
        if time not in times:
            await ctx.send('يجب التاكد من الوحده({})'.format(', '.join(times)))
            return
        time_ = 0
        if time == '30m':
            time_ = 1800
        elif time == '1h':
            time_ = 3600
        elif time == '2h':
            time_ = 7200
        elif time == '6h':
            time_ = 21600
        elif time == '12h':
            time_ = 43200
        elif time == '24h':
            time_ = 86400
        await ctx.send('تم تغير وقت ارسال الاذكار المخصص %s' % time)
        db.set_time(ctx.guild, time_)


def setup(client):
    client.add_cog(Time(client))