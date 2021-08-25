import discord
from discord.ext import commands
import bot.db as db
from datetime import datetime
import inspect
from functools import reduce


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='about', hidden=True, help="جلب معلومات و أحصائيات البوت")
    @commands.is_owner()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(embed_links=True)
    async def about(self, ctx):
        lam = lambda x, y: x + y
        embed = discord.Embed()
        embed.add_field(name='guilds:', value=str(len(self.bot.guilds)))
        embed.add_field(name='users:', value=str(reduce(lam, [i.member_count for i in self.bot.guilds])))
        embed.add_field(name='channels:', value=str(reduce(lam, [len(i.channels) for i in self.bot.guilds])))
        embed.add_field(name='guilds +100:', value=str(len([i for i in self.bot.guilds if i.member_count >= 100])))
        embed.add_field(name='guilds +1000:', value=str(len([i for i in self.bot.guilds if i.member_count >= 1000])))
        embed.add_field(name='channel in database:', value=str(len(db.get_all_channels())))
        embed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(name='load', hidden=True, help="أضافه ملف cog")
    @commands.is_owner()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(embed_links=True)
    async def load_cog(self, ctx, *, cog: str = None):
        if cog is None:
            await ctx.reply('يجب تحديد اسم ملف الـ cog')
            return
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            embed = discord.Embed(
                title="ERROR %s" % type(e).__name__,
                description="```bf\n%s\n```" % e
            )
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Load {cog}",
                description=f"```diff\n+ Load: {cog}\n```"
            )
            await ctx.reply(embed=embed)

    @commands.command(name='unload', hidden=True, help="الغاء أضافه ملف cog")
    @commands.is_owner()
    @commands.guild_only()
    async def unload_cog(self, ctx, *, cog: str = None):
        if cog is None:
            await ctx.reply('يجب تحديد اسم ملف الـ cog')
            return
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            embed = discord.Embed(
                title="ERROR %s" % type(e).__name__,
                description="```bf\n%s\n```" % e
            )
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Unload {cog}",
                description=f"```diff\n- Unload: {cog}\n```"
            )
            await ctx.reply(embed=embed)

    @commands.command(name='reload', hidden=True, help="أعاده أضافه ملف cog")
    @commands.is_owner()
    @commands.guild_only()
    async def reload_cog(self, ctx, *, cog: str = None):
        if cog is None:
            await ctx.reply('يجب تحديد اسم ملف الـ cog')
            return
        try:
            self.bot.reload_extension(cog)
        except Exception as e:
            embed = discord.Embed(
                title="ERROR %s" % type(e).__name__,
                description="```bf\n%s\n```" % e
            )
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Reload {cog}",
                description=f"```fix\nReload: {cog}\n```"
            )
            await ctx.reply(embed=embed)

    @commands.command(name='eval', hidden=True, help="تنفيذ أمر بايثون")
    @commands.is_owner()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(embed_links=True)
    async def eval_(self, ctx, *, expression=""):
        to_eval = expression.replace("await ", "")
        try:
            result = eval(to_eval)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            result = "%s: %s" % (type(e).__name__, str(e))
        result = str(result)
        embed = discord.Embed(description="Eval Result")
        embed.add_field(name="Input 📥", value=f"```py\n{expression}```", inline=False)
        embed.add_field(name="Output 📤", value=f"```py\n{result}```", inline=False)

        await ctx.reply(embed=embed)

    @commands.command(hidden=True, help="أعاد كتابه النص")
    @commands.is_owner()
    @commands.guild_only()
    async def osay(self, ctx, *, msg):
        await ctx.message.delete()
        await ctx.reply(msg)

    @commands.command(hidden=True, help="رؤيه هاذه الرساله")
    @commands.is_owner()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(embed_links=True)
    async def owner(self, ctx):
        x = db.Guild(ctx.guild).info
        commands = []
        for i in self.bot.commands:
            if i.hidden is True:
                commands.append(f'{x.get("prefix")}{i} {i.signature} - {i.help}')
        embed = discord.Embed(
            description="\n".join(commands),
            color=discord.Color.gold()
        )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text='Requested By: {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.group(name='blacklist', hidden=True, invoke_without_command=True, help="القائمة السوداء")
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def blacklist(self, ctx):
        prefix = db.Guild(ctx.guild).info.get("prefix")
        embed = discord.Embed(
            description="""
`{0}blacklist -u` - أضافة مستخدم الى القائمه السوداء
`{0}blacklist -s` - أضافة خادم الى القائمه السوداء
""".format(prefix)
        )
        await ctx.reply(embed=embed)

    @blacklist.group(name="-u", aliases=["user"], invoke_without_command=True)
    async def blacklist_user(self, ctx):
        prefix = db.Guild(ctx.guild).info.get("prefix")
        embed = discord.Embed(
            description="""
`{0}blacklist -u add <user_id>` - اضافه مستخدم
`{0}blacklist -u remove <user_id>` - حذف مستخدم
`{0}blacklist -u info <user_id>` - معلومات المستخدم
""".format(prefix)
        )
        await ctx.reply(embed=embed)

    @blacklist.group(name="-s", aliases=["server", "guild"], invoke_without_command=True)
    async def blacklist_server(self, ctx):
        prefix = db.Guild(ctx.guild).info.get("prefix")
        embed = discord.Embed(
            description="""
`{0}blacklist -s add <user_id>` - اضافه خادم
`{0}blacklist -s remove <user_id>` - حذف خادم
`{0}blacklist -s info <user_id>` - معلومات خادم
""".format(prefix)
        )
        await ctx.reply(embed=embed)

    @blacklist_user.command(name="-d", aliases=["add"])
    async def _blacklist_user(self, ctx, user: discord.User, reason: str = None):
        x = db.BlackListUser(user)
        if user.id in self.bot.owner_ids:
            return await ctx.reply("هاذ المستخدم من مسؤولين البوت")
        if x.check is False:
            embed = discord.Embed(
                description="**user:** %s\n**by:** %s\n**reason:** %s\n**data:** %s" % (
                    user,
                    await self.bot.fetch_user(x.info.get("_id")),
                    x.info.get("reason"),
                    datetime.fromtimestamp(x.info.get("timestamp"))
                )
            )
            return await ctx.reply("هاذ المستخدم موجود بالقائمه السوداء بالفعل", embed=embed)
        x.insert(ctx.author.id, reason)
        await ctx.reply("تم اضافه هاذ المستخدم الى القائمه السوداء")

    @blacklist_user.command(name="-r", aliases=["remove"])
    async def _unblacklist_user(self, ctx, user: discord.User):
        x = db.BlackListUser(user)
        if user.id in self.bot.owner_ids:
            return await ctx.reply("هاذ المستخدم من مسؤولين البوت")
        if x.check:
            return await ctx.reply("هاذ المستخدم غير موجود بالقائمه السوداء")
        x.delete()
        await ctx.reply("تم ازالة هاذ المستخدم من القائمه السوداء")

    @blacklist_user.command(name="-i", aliases=["info"])
    async def info_blacklist_user(self, ctx, user: discord.User):
        x = db.BlackListUser(user)
        if x.check is False:
            embed = discord.Embed(
                description="**user:** %s\n**by:** %s\n**reason:** %s\n**data:** %s" % (
                    user,
                    await self.bot.fetch_user(x.info.get("_id")),
                    x.info.get("reason"),
                    datetime.fromtimestamp(x.info.get("timestamp"))
                )
            )
            return await ctx.reply("هاذ المستخدم موجود بالقائمه السوداء بالفعل", embed=embed)
        await ctx.reply("لا يوجد بيانات")

    @blacklist_server.command(name="-d", aliases=["add"])
    async def _blacklist_server(self, ctx, guild: discord.Guild, reason: str = None):
        x = db.BlackListGuild(guild)
        if x.check is False:
            embed = discord.Embed(
                description="**server:** %s\n**server id:** %d\n**by:** %s\n**reason:** %s\n**data:** %s" % (
                    guild.name,
                    guild.id,
                    await self.bot.fetch_user(x.info["_id"]),
                    x.info["reason"],
                    datetime.fromtimestamp(x.info["timestamp"])
                )
            )
            return await ctx.reply("هاذ الخادم موجود بالقائمه السوداء بالفعل", embed=embed)
        x.insert(ctx.author.id, reason)
        await ctx.reply("تم اضافه هاذ الخادم الى القائمه السوداء")

    @blacklist_server.command(name="-r", aliases=["remove"])
    async def _unblacklist_server(self, ctx, guild: discord.Guild):
        x = db.BlackListGuild(guild)
        if x.check:
            return await ctx.reply("هاذ الخادم غير موجود بالقائمه السوداء")
        x.delete()
        await ctx.reply("تم ازالة هاذ الخادم من القائمه السوداء")

    @blacklist_server.command(name="-i", aliases=["info"])
    async def info_blacklist_server(self, ctx, guild: discord.Guild):
        x = db.BlackListGuild(guild)
        if x.check is False:
            embed = discord.Embed(
                description="**server:** %s\n**server id:** %d\n**by:** %s\n**reason:** %s\n**data:** %s" % (
                    guild.name,
                    guild.id,
                    await self.bot.fetch_user(x.info["_id"]),
                    x.info["reason"],
                    datetime.fromtimestamp(x.info["timestamp"])
                )
            )
            return await ctx.reply("هاذ الخادم موجود بالقائمه السوداء بالفعل", embed=embed)
        await ctx.reply("لا يوجد بيانات")


def setup(client):
    client.add_cog(Owner(client))
