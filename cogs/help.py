import discord
from discord.ext import commands
from discord.ext.commands import command, cooldown, guild_only
from discord import Embed, Colour
from db.db import get_prefix


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @command(name="help", aliases=["h", "commands"])
    @cooldown(1, 10, commands.BucketType.user)
    @guild_only()
    async def help_command(self, ctx):
        embed = Embed(
            color=Colour.red(),
            description="""
__**commands**__
`{0}help` - عرض اوامر البوت
`{0}invite` - لإضافة البوت الى سيرفرك
`{0}ping` - ارسال سرعة اتصال البوت
`{0}remove` - توقف البوت عن إرسال الأذكار
`{0}setprefix` - أمر تعيين البادئة.
`{0}setroom` - [#منشن الروم] - تحديد روم ارسال الاذكار
`{0}support` - سيرفر الدعم الفني
`{0}time` - [الوقت] تغير وقت ارسال الاذكار
***[𝐒upport](https://discord.gg/Ea9SUFUQCY) & [𝑰nvite](https://discord.com/oauth2/authorize?client_id=728782652454469662&permissions=8&scope=bot)***""".format(get_prefix(ctx), self.client.get_emoji(815909429010235442))

        )
        embed.set_author(name="Help - فاذكروني", icon_url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

# __**commands**__
# `{0}help` - عرض اوامر البوت
# `{0}invite` - لإضافة البوت الى سيرفرك
# `{0}ping` - ارسال سرعة اتصال البوت
# `{0}remove` - {#منشن الروم} - توقف البوت عن إرسال الأذكار
# `{0}setprefix` - set prefix command.
# `{0}setroom` - {#منشن الروم} - تحديد روم ارسال الاذكار
# `{0}support` - سيرفر الدعم الفني


def setup(client):
    client.add_cog(Help(client))
