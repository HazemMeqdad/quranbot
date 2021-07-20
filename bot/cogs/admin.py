from discord.ext import commands
import bot.db as db
import bot.config as config
import discord
import asyncio
from discord_components import Select, SelectOption, Button, ButtonStyle, InteractionType


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)

    @commands.command(name="prefix", aliases=["setprefix", "set_prefix", "set-prefix"], help='أمر تعيين البادئة.', usage='[البادئه الجديده]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def prefix_command(self, ctx, prefix=None):
        x = db.Guild(ctx.guild)
        if prefix is None:
            return await ctx.reply(embed=discord.Embed(
                description="%s الرجاء إدخال بادئة لتعيينها" % self.emoji.errors,
                color=self.bot.get_color(self.bot.color.gold)
            ))
        if len(prefix) > 5:
            await ctx.reply(embed=discord.Embed(
                description="%s لا يمكنك وضع بادئه اكثر من خمس حروف" % self.emoji.errors,
                color=self.bot.get_color(self.bot.color.gold)
            ))
            return
        x.update_where("prefix", prefix)
        embed = discord.Embed(
            description="تم تغير البادئه الى `%s`" % prefix,
            color=self.bot.get_color(self.bot.color.gold)
        )
        await ctx.reply(embed=embed)

    @commands.command(name='spam', help='عدم تكرار الرسائل, ينصح باستخدامه في الشاتات المفتوحه',
                      aliases=['anti-spam', "anti_spam"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def anti_spam(self, ctx):
        x = db.Guild(ctx.guild)
        if x.info["anti_spam"]:
            x.update_where("anti_spam", False)
            embed = discord.Embed(
                description="تم اطفاء خاصية تكرار الرسائل",
                color=self.bot.get_color(self.bot.color.gold)
            )
            await ctx.reply(embed=embed)
            return
        x.update_where("anti_spam", True)
        embed = discord.Embed(
            description="تم تفعيل خاصية تكرار الرسائل",
            color=self.bot.get_color(self.bot.color.gold)
        )
        await ctx.reply(embed=embed)

    @commands.command(name='embed', help='تغير خاصيه ارسال الاذكار الى امبد')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def embed(self, ctx):
        x = db.Guild(ctx.guild)
        if x.info["embed"]:
            x.update_where("embed", False)
            embed = discord.Embed(
                description="تم اطفاء خاصية الأمبد",
                color=self.bot.get_color(self.bot.color.gold)
            )
            await ctx.reply(embed=embed)
            return
        x.update_where("embed", True)
        embed = discord.Embed(
            description="تم تفعيل خاصية الأمبد",
            color=self.bot.get_color(self.bot.color.gold)
        )
        await ctx.reply(embed=embed)

    @commands.command(name="time", aliases=["set_time", "settime"], help='تغير وقت ارسال الاذكار')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_timer(self, ctx):
        x = db.Guild(ctx.guild)
        if not x.info["channel"]:
            await ctx.reply(embed=discord.Embed(
                description="يجب عليك تثبيت روم لاستعمال هاذ الامر",
                color=self.bot.get_color(self.bot.color.gold)
            ))
            return
        embed = discord.Embed(
            description="اختر الوقت المناسب من خلال القائمة في الأسفل",
            color=self.bot.get_color(self.bot.color.gold)
        )

        msg = await ctx.reply(
            embed=embed,
            components=[
                Select(
                    placeholder="اختر الوقت المناسب",
                    max_values=1,
                    options=[
                        SelectOption(label="30 دقيقة", value="1800"),
                        SelectOption(label="ساعه", value="3600"),
                        SelectOption(label="ساعتين", value="7200"),
                        SelectOption(label="6 ساعات", value="21600"),
                        SelectOption(label="12 ساعه", value="43200"),
                        SelectOption(label="24 ساعه", value="86400"),
                        SelectOption(label="الغاء", value="7", emoji="❌"),
                    ]
                )
            ]
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel
        try:
            res = await self.bot.wait_for("select_option", check=check, timeout=30)
            value = list(map(lambda x: x.value, res.component))[0]
            lable = list(map(lambda x: x.label, res.component))[0]
            if value == "7":
                return await msg.delete()
            x.update_where("time", int(value))
            await res.respond(
                embed=discord.Embed(
                    description="تم تغير وقت ارسال الأذكار إلى: **%s**" % lable,
                    color=self.bot.get_color(self.bot.color.gold)
                ),
                ephemeral=False
            )
            await msg.delete()
        except asyncio.TimeoutError:
            return await msg.delete()

    @commands.command(name="setroom", aliases=["channel", "setchannel", "set_room", "set_channel"],
                      help='تحديد روم ارسال الاذكار', usage='[#الروم الجديده]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_channel_command(self, ctx, channel: discord.TextChannel):
        x = db.Guild(ctx.guild)
        if channel.id == x.info["channel"]:
            embed = discord.Embed(
                description="لقد قمت بتحديد هاذه الروم من قبل",
                color=self.bot.get_color(self.bot.color.gold)
            )
            return await ctx.reply(embed=embed)
        x.update_where("channel", channel.id)
        await ctx.reply(embed=discord.Embed(
            description="! الله يكتب اجرك راح ارسل الاذكار للروم %s" % channel.mention,
            color=self.bot.get_color(self.bot.color.gold)
        ))

    @commands.command(name="remove", aliases=["removeroom"], help='توقف البوت عن إرسال الأذكار')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def remove_command(self, ctx):
        x = db.Guild(ctx.guild)
        if not x.info["channel"]:
            return await ctx.reply(embed=discord.Embed(
                description="انت لم تقم بتثبيت الروم من قبل",
                color=self.bot.get_color(self.bot.color.gold)
            ))
        embed = discord.Embed(
            description="هل انت موافق على ايقاف ارسال الاذكار في روم <#%s>" % x.info["channel"],
            color=self.bot.get_color(self.bot.color.gold)
        )
        m = await ctx.reply(
            embed=embed,
            components=[
                [
                    Button(label="موافق", style=ButtonStyle.green, emoji=self.emoji.yes, id="true"),
                    Button(label="غير موافق", style=ButtonStyle.red, emoji=self.emoji.no1, id="false")
                ]

            ]
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel
        try:
            res = await self.bot.wait_for("button_click", check=check, timeout=15)
            if res.component.id == "true":
                x.update_where("channel", None)
                embed = discord.Embed(
                    description="تم الغاء ارسال الاذكار بنجاح",
                    color=self.bot.get_color(self.bot.color.gold)
                )
                await res.respond(
                    embed=embed,
                    type=InteractionType.ChannelMessageWithSource,
                    ephemeral=False
                )
                await m.delete()
                return
            embed = discord.Embed(
                description="تم الغاء الأمر",
                color=self.bot.get_color(self.bot.color.gold)
            )
            await res.respond(
                embed=embed,
                type=InteractionType.ChannelMessageWithSource,
                ephemeral=False
            )
            await m.delete()
        except asyncio.TimeoutError:
            return await m.delete()


def setup(bot):
    bot.add_cog(Admin(bot))

