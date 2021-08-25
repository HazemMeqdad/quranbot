from discord.ext import commands
import bot.db as db
import bot.config as config
import discord
import asyncio
import bot.lang as lang


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
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        if prefix is None:
            return await ctx.reply(embed=discord.Embed(
                description=_["if_not_prefix"] % self.emoji.errors,
                color=self.bot.get_color(self.bot.color.gold)
            ))
        if len(prefix) > 5:
            await ctx.reply(embed=discord.Embed(
                description=_["if_len_larger_5"] % self.emoji.errors,
                color=self.bot.get_color(self.bot.color.gold)
            ))
            return
        x.update_where("prefix", prefix)
        embed = discord.Embed(
            description=_["set_prefix"] % prefix,
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
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        if x.info["anti_spam"]:
            x.update_where("anti_spam", False)
            embed = discord.Embed(
                description=_["off"],
                color=self.bot.get_color(self.bot.color.gold)
            )
            await ctx.reply(embed=embed)
            return
        x.update_where("anti_spam", True)
        embed = discord.Embed(
            description=_["on"],
            color=self.bot.get_color(self.bot.color.gold)
        )
        await ctx.reply(embed=embed)

    @commands.command(name='embed', help='تغير خاصيه ارسال الاذكار الى امبد')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def embed(self, ctx):
        x = db.Guild(ctx.guild)
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        if x.info["embed"]:
            x.update_where("embed", False)
            embed = discord.Embed(
                description=_["off"],
                color=self.bot.get_color(self.bot.color.gold)
            )
            await ctx.reply(embed=embed)
            return
        x.update_where("embed", True)
        embed = discord.Embed(
            description=_["on"],
            color=self.bot.get_color(self.bot.color.gold)
        )
        await ctx.reply(embed=embed)

    @commands.command(name="time", aliases=["set_time", "settime"], help='تغير وقت ارسال الاذكار')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_timer(self, ctx):
        x = db.Guild(ctx.guild)
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        if not x.info["channel"]:
            await ctx.reply(embed=discord.Embed(
                description=_["if_not_channel"],
                color=self.bot.get_color(self.bot.color.gold)
            ))
            return
        embed = discord.Embed(
            description=_["select_time"],
            color=self.bot.get_color(self.bot.color.gold)
        )
        view = discord.ui.View()
        select = discord.ui.Select(placeholder=_["select_time_placeholder"])
        data = {
            "1800": _["time"]["30m"],
            "3600": _["time"]["1h"],
            "7200": _["time"]["2h"],
            "21600": _["time"]["6h"],
            "43200": _["time"]["12h"],
            "86400": _["time"]["24h"]
        }
        for value, lable in data.items():
            select.append_option(discord.SelectOption(label=lable, value=value))
        select.append_option(discord.SelectOption(label=_["time"]["cancel"], value="0", emoji="❌"))
        view.add_item(item=select)
        msg = await ctx.reply(embed=embed, view=view)

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel
        try:
            res = await self.bot.wait_for("interaction", check=check, timeout=30)
            value = res.data.get("values")[0]
            lable = data.get(value)
            if value == "0":
                return await msg.delete()
            x.update_where("time", int(value))
            select.disabled = True
            await res.edit_original_message(
                embed=discord.Embed(
                    description=_["set_time"] % lable,
                    color=self.bot.get_color(self.bot.color.gold)
                ),
                view=view
            )
        except asyncio.TimeoutError:
            return await msg.delete()

    @commands.command(name="setroom", aliases=["channel", "setchannel", "set_room", "set_channel"],
                      help='تحديد روم ارسال الاذكار', usage='[#الروم الجديده]')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def set_channel_command(self, ctx, channel: discord.TextChannel):
        x = db.Guild(ctx.guild)
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        if channel.id == x.info["channel"]:
            embed = discord.Embed(
                description=_["if_new_channel_is_old_channel"],
                color=self.bot.get_color(self.bot.color.gold)
            )
            return await ctx.reply(embed=embed)
        x.update_where("channel", channel.id)
        await ctx.reply(embed=discord.Embed(
            description=_["set_channel"] % channel.mention,
            color=self.bot.get_color(self.bot.color.gold)
        ))

    @commands.command(name="remove", aliases=["removeroom"], help='توقف البوت عن إرسال الأذكار')
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.guild_only()
    async def remove_command(self, ctx):
        x = db.Guild(ctx.guild)
        _ = lang.Languages(ctx.guild).get_response(ctx.command)
        if not x.info["channel"]:
            return await ctx.reply(embed=discord.Embed(
                description=_["if_not_channel"],
                color=self.bot.get_color(self.bot.color.gold)
            ))
        embed = discord.Embed(
            description=_["check"]["msg"] % x.info["channel"],
            color=self.bot.get_color(self.bot.color.gold)
        )
        view = discord.ui.View()
        true = discord.ui.Button(
            label=_["check"]["true"],
            style=discord.ButtonStyle.green,
            emoji=self.emoji.yes,
            custom_id="true"
        )
        false = discord.ui.Button(
            label=_["check"]["false"],
            style=discord.ButtonStyle.red,
            emoji=self.emoji.no1,
            custom_id="false"
        )
        view.add_item(item=true)
        view.add_item(item=false)
        m = await ctx.reply(embed=embed, view=view)

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel
        try:
            res = await self.bot.wait_for("interaction", check=check, timeout=15)
            true.disabled = True
            false.disabled = True
            if res.data["custom_id"] == "true":
                x.update_where("channel", None)
                embed = discord.Embed(
                    description=_["done"],
                    color=self.bot.get_color(self.bot.color.gold)
                )
                await res.edit_original_message(
                    embed=embed,
                    view=view
                )
                return
            embed = discord.Embed(
                description=_["cancel"],
                color=self.bot.get_color(self.bot.color.gold)
            )
            await res.edit_original_message(
                embed=embed,
                view=view
            )
        except asyncio.TimeoutError:
            return await m.delete()


def setup(bot):
    bot.add_cog(Admin(bot))
