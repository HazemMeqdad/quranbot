import discord
from discord.ext import commands
import bot.db as db
import datetime
import inspect


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='about', aliases=['bot', 'botinfo'], hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_guild_permissions(embed_links=True)
    async def about(self, ctx):
        _all = db.All().get_all_channels()
        users = 0
        channels = 0
        guilds__ = 0
        _guilds = 0
        for i in self.bot.guilds:
            users += i.member_count
            channels += len(i.channels)
            if i.member_count >= 100:
                guilds__ += 1
            if i.member_count >= 1000:
                _guilds += 1
        embed = discord.Embed()
        embed.add_field(name='guilds:', value=str(len(self.bot.guilds)))
        embed.add_field(name='users:', value=str(users))
        embed.add_field(name='channels:', value=str(channels))
        embed.add_field(name='guilds +100:', value=str(guilds__))
        embed.add_field(name='guilds +1000:', value=str(_guilds))
        embed.add_field(name='channel in database:', value=str(len(_all)))
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_guild_permissions(embed_links=True)
    async def load_cog(self, ctx, *, cog: str = None):
        if cog is None:
            await ctx.send('يجب تحديد اسم ملف ال cog')
            return
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**SUCCESS** load {cog}')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unload_cog(self, ctx, *, cog: str = None):
        if cog is None:
            await ctx.send('يجب تحديد اسم ملف ال cog')
            return
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**SUCCESS** unload {cog}')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def reload_cog(self, ctx, *, cog: str = None):
        if cog is None:
            await ctx.send('يجب تحديد اسم ملف ال cog')
            return
        try:
            self.bot.reload_extension(cog)
        except Exception as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**SUCCESS** reload {cog}')

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


def setup(client):
    client.add_cog(Owner(client))


