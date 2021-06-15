from discord.ext import commands
import bot.db as db
import bot.config as config
import discord
import asyncio


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)
        self.color = config.Color()

    @commands.command(name="prefix", aliases=["setprefix", "set_prefix", "set-prefix"], help='أمر تعيين البادئة.', usage='[البادئه الجديده]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def prefix_command(self, ctx, prefix=None):
        x = db.Guild(ctx.guild)
        if prefix is None:
            return await ctx.send("%s الرجاء إدخال بادئة لتعيينها" % self.emoji.errors)
        if len(prefix) > 5:
            await ctx.send("%s لا يمكنك وضع بادئه اكثر من خمس حروف" % self.emoji.errors)
            return
        x.update_where("prefix", prefix)
        embed = discord.Embed(
            description="تم تغير البادئه الى `%s`" % prefix
        )
        await ctx.send(embed=embed)

    @commands.command(name='spam', help='عدم تكرار الرسائل, ينصح باستخدامه في الشاتات المفتوحه',
                      aliases=['anti-spam', "anti_spam"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def anti_spam(self, ctx):
        x = db.Guild(ctx.guild)
        if bool(x.info[5]):
            x.update_where("anti_spam", False)
            embed = discord.Embed(
                description="تم اطفاء خاصية تكرار الرسائل",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        elif bool(x.info[5]) is False:
            x.update_where("anti_spam", True)
            embed = discord.Embed(
                description="تم تفعيل خاصية تكرار الرسائل",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

    @commands.command(name='embed', help='تغير خاصيه ارسال الاذكار الى امبد')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def embed(self, ctx):
        x = db.Guild(ctx.guild)
        if bool(x.info[6]):
            x.update_where("embed", False)
            embed = discord.Embed(
                description="تم اطفاء خاصية الأمبد",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        elif bool(x.info[6]) is False:
            x.update_where("embed", True)
            embed = discord.Embed(
                description="تم تفعيل خاصية الأمبد",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="time", aliases=["set_time", "settime"], help='تغير وقت ارسال الاذكار')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_timer(self, ctx):
        x = db.Guild(ctx.guild)
        if not x.info[3]:
            await ctx.send("%s يجب عليك تثبيت روم لاستعمال هاذ الامر `setroom%s`" % (self.emoji.errors, x.info[2]))
            return
        list_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '❌']
        embed = discord.Embed(description="""
اختر الوقت المناسب من خلال الضغط على الراكشن المناسب:
> :one: - 30 دقيقه
> :two: - ساعه
> :three: - ساعتين
> :four: - 6 ساعات
> :five: - 12 ساعه
> :six: - 24 ساعه
> :x: - الغاء الامر
""")

        m = await ctx.send(embed=discord.Embed(description="الرجاء الانتضار بعض الثواني %s" % self.emoji.loading))
        for i in list_emojis:
            await m.add_reaction(i)
        await m.edit(embed=embed)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in list_emojis
        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=30)
        except asyncio.TimeoutError:
            return await m.delete()
        else:
            if str(reaction.emoji) == "❌":
                return await m.delete()

            # -------------------------------------------------------------------------------------
            emojis = {"1️⃣": 1800, "2️⃣": 3600, "3️⃣": 7200, "4️⃣": 21600, "5️⃣": 43200, "6️⃣": 86400}
            times = {1800: "30m", 3600: "1h", 7200: "2h", 21600: "6h", 43200: "12h", 86400: "24h"}
            new_time = emojis.get(str(reaction.emoji))
            # -------------------------------------------------------------------------------------

            x.update_where("time", new_time)
            embed = discord.Embed(
                description="تم تغير الوقت الى `%s`" % times.get(new_time),
                color=discord.Color.green()
            )
            await m.edit(embed=embed)
            await m.clear_reactions()

    @commands.command(name="setroom", aliases=["channel", "setchannel", "set_room", "set_channel"],
                      help='تحديد روم ارسال الاذكار', usage='[#الروم الجديده]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_channel_command(self, ctx, channel: discord.TextChannel):
        x = db.Guild(ctx.guild)
        if channel.id == x.info[3]:
            embed = discord.Embed(
                description="لقد قمت بتحديد هاذه الروم من قبل"
            )
            return await ctx.send(embed=embed)
        x.update_where("channel", channel.id)
        await ctx.send(embed=discord.Embed(
            description="! الله يكتب اجرك راح ارسل الاذكار للروم %s" % channel.mention,
            color=discord.Color.green()
        ))

    @commands.command(name="remove", aliases=["removeroom"], help='توقف البوت عن إرسال الأذكار')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def remove_command(self, ctx):
        x = db.Guild(ctx.guild)
        if not x.info[2]:
            return await ctx.send(embed=discord.Embed(description="انت لم تقم بتثبيت الروم", color=discord.Colour.red()))
        info = x.info
        m = await ctx.send(embed=discord.Embed(
            description="هل انت موافق على ايقاف ارسال الاذكار في روم <#%s>" % info[3]
        ))
        await m.add_reaction("✅")
        await m.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=check)
        except asyncio.TimeoutError:
            return await m.delete()
        else:
            if str(reaction.emoji) == "✅":
                x.update_where("channel", None)
                embed = discord.Embed(
                    description="تم الغاء ارسال الاذكار بنجاح",
                    color=discord.Color.green()
                )
                await m.edit(embed=embed)
                await m.clear_reactions()
                return
            await m.delete()


def setup(bot):
    bot.add_cog(Admin(bot))

