import discord
from discord.ext import commands
import bot.db as db
import bot.config
import datetime
import inspect
from functools import reduce
import backup


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='about', aliases=['bot', 'botinfo'], hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_guild_permissions(embed_links=True)
    async def about(self, ctx):
        fun = lambda x, y: x + y
        embed = discord.Embed()
        embed.add_field(name='guilds:', value=str(len(self.bot.guilds)))
        embed.add_field(name='users:', value=str(reduce(fun, [i.member_count for i in self.bot.guilds])))
        embed.add_field(name='channels:', value=str(reduce(fun, [len(i.channels) for i in self.bot.guilds])))
        embed.add_field(name='guilds +100:', value=str(len([i for i in self.bot.guilds if i.member_count >= 100])))
        embed.add_field(name='guilds +1000:', value=str(len([i for i in self.bot.guilds if i.member_count >= 1000])))
        embed.add_field(name='channel in database:', value=str(len(db.get_all_channels())))
        embed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.reply(embed=embed)

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
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

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
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

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
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

    @commands.command(name='eval', pass_context=True, hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
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

        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def osay(self, ctx, *, msg):
        await ctx.message.delete()
        await ctx.send(msg)

    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_guild_permissions(embed_links=True)
    async def oembed(self, ctx, *, msg):
        await ctx.message.delete()
        await ctx.send(embed=discord.Embed(
            description=msg,
            color=discord.Color.gold())
                .set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
                .set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                # .set_thumbnail(url=self.client.user.avatar_url)
                .set_image(url='https://i8.ae/IjVZC')
               )

    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_guild_permissions(embed_links=True)
    async def owner(self, ctx):
        x = db.Guild(ctx.guild).info
        commands = []
        for i in self.bot.commands:
            if i.hidden is True:
                commands.append(f'{x[2]}{i} {i.signature}')
        embed = discord.Embed(
            description="\n".join(commands),
            color=discord.Color.gold()
        )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_footer(text='Requested By: {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='blacklist', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_guild_permissions(embed_links=True)
    async def blacklist(self, ctx, user: discord.User, *, reason=None):
        x = db.BlackList(user)
        if user.id in self.bot.owner_ids:
            return await ctx.send("هاذ المستخدم من مسؤولين البوت")
        if x.check is False:
            embed = discord.Embed(
                description="**user:** %s\n**by:** %s\n**reason:** %s\n**data:** %s" % (
                    user, await self.bot.fetch_user(x.info[1]), x.info[2], datetime.datetime.fromtimestamp(x.info[3]))
            )
            return await ctx.send("هاذ المستخدم موجود بالقائمه السوداء بالفعل", embed=embed)
        x.insert(ctx.author.id, reason)
        await ctx.send("تم اضافه هاذ المستخدم الى القائمه السوداء")

    @commands.command(name='unblacklist', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_guild_permissions(embed_links=True)
    async def unblacklist(self, ctx, user: discord.User):
        x = db.BlackList(user)
        if user.id in self.bot.owner_ids:
            return await ctx.send("هاذ المستخدم من مسؤولين البوت")
        if x.check:
            return await ctx.send("هاذ المستخدم غير موجود بالقائمه السوداء")
        x.delete()
        await ctx.send("تم ازالة هاذ المستخدم من القائمه السوداء")

    @commands.command(name='backup', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_guild_permissions(attach_files=True)
    async def backup_database(self, ctx):
        backup_file = backup.backup("fdr")
        print(backup_file)
        file = discord.File(backup_file)
        await ctx.send(file=file)


def setup(client):
    client.add_cog(Owner(client))


