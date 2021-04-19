import discord
from discord.ext import commands
import db
import inspect


class Owner(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='about', aliases=['bot', 'botinfo'], hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def about(self, ctx):
        users = 0
        channels = 0
        guilds__ = 0
        _guilds = 0
        for i in self.client.guilds:
            users += i.member_count
            channels += len(i.channels)
            if i.member_count >= 100:
                guilds__ += 1
            if i.member_count >= 1000:
                _guilds += 1
        embed = discord.Embed()
        embed.add_field(name='guilds:', value=str(len(self.client.guilds)))
        embed.add_field(name='users:', value=str(users))
        embed.add_field(name='channels:', value=str(channels))
        embed.add_field(name='guilds +100:', value=str(guilds__))
        embed.add_field(name='guilds +1000:', value=str(_guilds))
        embed.add_field(name='channel in database:', value=str(len(db.get_all_channels())))
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def load_cog(self, ctx, *, cog: str=None):
        if cog is None:
            await ctx.send('يجب تحديد اسم ملف ال cog')
            return
        try:
            self.client.load_extension(cog)
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
            self.client.unload_extension(cog)
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
            self.client.reload_extension(cog)
        except Exception as e:
            await ctx.send(f'**ERROR:** {type(e).__name__} - {e}')
        else:
            await ctx.send(f'**SUCCESS** reload {cog}')

    @commands.command(name='eval', pass_context=True, hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def eval_(self, ctx, *, expression=""):
        to_eval = expression.replace("await ", "")
        try:
            result = eval(to_eval)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            result = type(e).__name__ + ": " + str(e)
        result = str(result)
        embed = discord.Embed(description="Eval Result")
        embed.add_field(name="Input 📥", value=f"```Python\n{expression}```", inline=False)
        embed.add_field(name="Output 📤", value=f"```Python\n{result}```", inline=False)

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
    async def oembed(self, ctx, *, msg):
        await ctx.message.delete()
        await ctx.send(embed=discord.Embed(
            description=msg,
            color=discord.Color.gold())
                .set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
                .set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
                .set_thumbnail(url=self.client.user.avatar_url)
                .set_image(url='https://i8.ae/sRlUh')
               )

    @commands.command(hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def owner(self, ctx):
        commands = []
        for i in self.client.commands:
            if i.hidden is True:
                commands.append(f'{db.get_prefix(ctx.guild)}{i} {i.signature}')
        embed = discord.Embed(
            description="\n".join(commands),
            color=discord.Color.gold()
        )
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        embed.set_footer(text='Requested By: {}'.format(ctx.author), icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Owner(client))


