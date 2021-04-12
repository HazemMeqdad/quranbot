from discord.ext import commands
import db


def convert(timer):
    pos = ["m", "h"]
    time_dict = {"m": 60, "h": 60 * 60}
    unit = timer[-1]
    if unit not in pos:
        return -1
    try:
        val = int(timer[:-1])
    except:
        return -2
    return val * time_dict[unit]


class Time(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="time", aliases=["set_time", "settime"], help='تغير وقت ارسال الاذكار', usage='time [الوقت]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_timer(self, ctx, time: str = None):
        if db.get_channel(ctx.guild) is None:
            await ctx.send("يجب عليك تثبيت روم لاستعمال هاذ الامر `setroom{}`".format(db.get_prefix(ctx.guild)))
            return
        if time is None:
            await ctx.send("يجب تحديد الوقت مثل: `time 30m{}`".format(db.get_prefix(ctx.guild)))
            return
        time_ = convert(time)
        if time_ == -1:
            await ctx.send('يجب التاكد من الوحده(m او h)')
            return
        elif time_ == -2:
            await ctx.send('يجب أن يكون الوقت عدد صحيح')
            return
        if time_ < 1800:
            await ctx.send('اقل وقت يمكنك تحديده هو 30 دقيقه')
            return
        elif time_ > 86400:
            await ctx.send('اكثر وقت يمكنك تحديده هو 24 ساعه')
        db.set_time(ctx.guild, time_)
        await ctx.send('تم تغير وقت ارسال الاذكار المخصص {}'.format(time))


def setup(client):
    client.add_cog(Time(client))
