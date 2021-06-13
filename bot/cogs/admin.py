from discord.ext import commands
import bot.db as db
import bot.config as config
import discord
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
import asyncio


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = config.Emoji(self.bot)
        self.color = config.Color()

    async def saving_changes(self, res, message):
        await res.respond(
            type=InteractionType.ChannelMessageWithSource,
            content="تم حفظ التعديلات بنجاح"
        )
        await message.edit(
            embed=discord.Embed(description="تم حفظ التعديلات بنجاح", color=self.color.green),
            components=[
                Button(style=ButtonStyle.green, emoji=self.emoji.yes, disabled=True),
            ],
        )

    async def do_not_save_changes(self, res, message):
        await res.respond(
            type=InteractionType.ChannelMessageWithSource,
            content="تم الغاء الأمر"
        )
        await message.edit(
            embed=discord.Embed(description="تم الغاء الأمر", color=self.color.red),
            components=[
                Button(style=ButtonStyle.red, emoji=self.emoji.no1, disabled=True)
            ],
        )

    async def send_embed(self, ctx, embed: discord.Embed):
        m = await ctx.send(
            embed=embed,
            components=[[Button(style=ButtonStyle.green, emoji=self.emoji.yes, id='yes1'),
                         Button(style=ButtonStyle.red, emoji=self.emoji.no1, id='no1')]],
        )
        return m

    @commands.command(name="prefix", aliases=["setprefix", "set_prefix", "set-prefix"], help='أمر تعيين البادئة.', usage='[البادئه الجديده]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def prefix_command(self, ctx, prefix=None):
        x = db.Guild(ctx.guild)
        print(self.emoji.fdr_50)
        if prefix is None:
            return await ctx.send("%s الرجاء إدخال بادئة لتعيينها" % self.emoji.errors)
        if len(prefix) > 5:
            await ctx.send("%s لا يمكنك وضع بادئه اكثر من خمس حروف" % self.emoji.errors)
            return
        embed = discord.Embed(
            description="هل انت موافق على تغير البادئه الى `%s`" % prefix
        )
        m = await self.send_embed(ctx, embed)

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel

        try:
            res = await self.bot.wait_for("button_click", check=check, timeout=15)
        except asyncio.TimeoutError:
            return await m.delete()
        else:
            if res.component.id == "yes1":
                x.update_where("prefix", prefix)
                await self.saving_changes(res, m)
            elif res.component.id == "no1":
                await self.do_not_save_changes(res, m)

    @commands.command(name='spam', help='عدم تكرار الرسائل, ينصح باستخدامه في الشاتات المفتوحه', aliases=['anti-spam', "anti_spam"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def anti_spam(self, ctx):
        x = db.Guild(ctx.guild)
        if bool(x.info[5]):
            embed = discord.Embed(description="هل انت موافق على اطفاء خاصيه عدم تكرار الرسائل")
            m = await self.send_embed(ctx, embed)

            def check(res):
                return ctx.author == res.user and res.channel == ctx.channel

            try:
                res = await self.bot.wait_for("button_click", check=check, timeout=15)
            except asyncio.TimeoutError:
                return await m.delete()
            else:
                if res.component.id == "yes1":
                    x.update_where("anti_spam", False)
                    await self.saving_changes(res, m)
                elif res.component.id == "no1":
                    await self.do_not_save_changes(res, m)
            return
        embed = discord.Embed(description="هل انت موافق على تفعيل خاصيه عدم تكرار الرسائل")
        m = await self.send_embed(ctx, embed)

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel

        try:
            res = await self.bot.wait_for("button_click", check=check, timeout=15)
        except asyncio.TimeoutError:
            return await m.delete()
        else:
            if res.component.id == "yes1":
                x.update_where("anti_spam", True)
                await self.saving_changes(res, m)
            elif res.component.id == "no1":
                await self.do_not_save_changes(res, m)

    @commands.command(name='embed', help='تغير خاصيه ارسال الاذكار الى امبد')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def embed(self, ctx):
        x = db.Guild(ctx.guild)
        if bool(x.info[6]):
            embed = discord.Embed(description="هل انت موافق على اطفاء خاصيه الأمبد")
            m = await self.send_embed(ctx, embed)

            def check(res):
                return ctx.author == res.user and res.channel == ctx.channel

            try:
                res = await self.bot.wait_for("button_click", check=check, timeout=15)
            except asyncio.TimeoutError:
                return await m.delete()
            else:
                if res.component.id == "yes1":
                    x.update_where("embed", False)
                    await self.saving_changes(res, m)
                elif res.component.id == "no1":
                    await self.do_not_save_changes(res, m)
            return
        embed = discord.Embed(description="هل انت موافق على تفعيل خاصيه الأمبد")
        m = await self.send_embed(ctx, embed)

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel

        try:
            res = await self.bot.wait_for("button_click", check=check, timeout=15)
        except asyncio.TimeoutError:
            return await m.delete()
        else:
            if res.component.id == "yes1":
                x.update_where("embed", True)
                await self.saving_changes(res, m)
            elif res.component.id == "no1":
                await self.do_not_save_changes(res, m)

    @commands.command(name="time", aliases=["set_time", "settime"], help='تغير وقت ارسال الاذكار')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_timer(self, ctx):
        x = db.Guild(ctx.guild)
        if not x.info[3]:
            await ctx.send("%s يجب عليك تثبيت روم لاستعمال هاذ الامر `setroom%s`" % (self.emoji.errors, x.info[2]))
            return
        embed = discord.Embed(description="اختر الوقت المناسب من خلال الضغط على الزر المناسب")
        m = await ctx.send(
            embed=embed,
            components=[
                [
                    Button(style=ButtonStyle.green, label="30m", id="1800"),
                    Button(style=ButtonStyle.green, label="1h", id="3600"),
                    Button(style=ButtonStyle.green, label="2h", id="7200"),
                    Button(style=ButtonStyle.green, label="6h", id="21600")
                ],
                [
                    Button(style=ButtonStyle.green, label="12h", id="43200"),
                    Button(style=ButtonStyle.green, label="24h", id="86400"),
                    Button(style=ButtonStyle.red, emoji=self.emoji.no1, id="no")
                ]
            ]

        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel
        try:
            res = await self.bot.wait_for("button_click", check=check, timeout=15)
        except asyncio.TimeoutError:
            return await m.delete()
        else:
            if res.component.id == "no":
                return await self.do_not_save_changes(res, m)
            x.update_where("time", int(res.component.id))
            label = res.component.label
            await res.respond(
                type=InteractionType.ChannelMessageWithSource,
                content="تم حفظ التعديلات بنجاح"
            )
            await m.edit(
                embed=discord.Embed(description="تم حفظ التعديلات بنجاح", color=self.color.green),
                components=[
                    Button(style=ButtonStyle.green, label=label, disabled=True),
                ]
            )

    @commands.command(name="setroom", aliases=["channel", "setchannel", "set_room", "set_channel"],
                      help='تحديد روم ارسال الاذكار', usage='[#الروم الجديده]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_channel_command(self, ctx, channel: discord.TextChannel = None):
        x = db.Guild(ctx.guild)
        if channel is None:
            return await ctx.send("%s يرجى منشن الروم الكتابيه" % self.emoji.errors)
        m = await ctx.send(
            embed=discord.Embed(
                description="هل انت موافق على تغير روم الاذكار"
            ),
            components=[
                [
                    Button(style=ButtonStyle.green, emoji=self.emoji.yes, id='yap'),
                    Button(style=ButtonStyle.red, emoji=self.emoji.no1, id='nop')
                ]],
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel

        try:
            res = await self.bot.wait_for("button_click", check=check, timeout=15)
        except asyncio.TimeoutError:
            return await m.delete()
        else:
            if res.component.id == "yap":
                x.update_where("channel", channel.id)
                await m.edit(embed=discord.Embed(
                    description="! الله يكتب اجرك راح ارسل الاذكار للروم %s" % channel.mention
                ),
                    components=[[Button(style=ButtonStyle.green, emoji=self.emoji.yes, disabled=True)]])
                await res.respond(
                    type=InteractionType.ChannelMessageWithSource,
                    content="! الله يكتب اجرك راح ارسل الاذكار للروم %s" % channel.mention
                )
            elif res.component.id == "nop":
                await self.do_not_save_changes(res, m)

    @commands.command(name="remove", aliases=["removeroom"], help='توقف البوت عن إرسال الأذكار')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def remove_command(self, ctx):
        x = db.Guild(ctx.guild)
        if not x.info[2]:
            return await ctx.send("انت لم تقم بتثبيت الروم")
        info = x.info
        channel = self.bot.get_channel(info[3])
        m = await self.send_embed(ctx, embed=discord.Embed(
            description="هل انت موافق على ايقاف ارسال الاذكار في روم `%s`" % channel if channel else "لا يوجد بيانات"
        ))

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel

        try:
            res = await self.bot.wait_for("button_click", check=check, timeout=15)
        except asyncio.TimeoutError:
            return await m.delete()
        else:
            if res.component.id == "yes1":
                x.update_where("channel", None)
                await self.saving_changes(res, m)
            elif res.component.id == "no1":
                await self.do_not_save_changes(res, m)


def setup(bot):
    bot.add_cog(Admin(bot))
    DiscordComponents(bot)

