import hikari
import lightbulb
from lightbulb.context import Context
from bot.bot import Bot
from bot.database import DB, GuildUpdateType
from hikari.messages import ButtonStyle
import asyncio




class Admin(lightbulb.Plugin):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db: DB = bot.db
        super().__init__()

    @lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @lightbulb.command(name="prefix", aliases=["setprefix", "set_prefix", "set-prefix"])
    async def prefix_command(self, ctx: lightbulb.Context, new_prefix: str):
        guild = self.db.get_guild(ctx.guild_id)
        error = await self.bot.emojis.error
        embed = hikari.Embed(color=0xffd430)
        if len(new_prefix) > 5:
            embed.description = "%s لا يمكنك وضع بادئه اكثر من خمس حروف" % error
            await ctx.respond(embed=embed, reply=True, mentions_reply=False)
            return
        self.db.update_guild(guild, GuildUpdateType.prefix, new_prefix)
        embed.description = "تم تغير البادئه الى `%s`" % new_prefix
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)

    @lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @lightbulb.command(name='spam', aliases=['anti-spam', "anti_spam"])
    async def anti_spam(self, ctx: Context):
        guild = self.db.get_guild(ctx.guild_id)
        embed = hikari.Embed(color=0xffd430)
        if guild.anti_spam:
            self.db.update_guild(guild, GuildUpdateType.anti_spam, False)
            embed.description = "تم اطفاء خاصية تكرار الرسائل"
            await ctx.respond(embed=embed, reply=True, mentions_reply=False)
            return
        self.db.update_guild(guild, GuildUpdateType.anti_spam, True)
        embed.description = "تم تفعيل خاصية تكرار الرسائل"
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)

    @lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @lightbulb.command(name='embed')
    async def embed(self, ctx: Context):
        guild = self.db.get_guild(ctx.guild_id)
        embed = hikari.Embed(color=0xffd430)
        if guild.embed:
            self.db.update_guild(guild, GuildUpdateType.embed, False)
            embed.description = "تم اطفاء خاصية الأمبد"
            await ctx.respond(embed=embed, reply=True, mentions_reply=False)
            return
        self.db.update_guild(guild, GuildUpdateType.embed, True)
        embed.description = "تم تفعيل خاصية الأمبد"
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)

    @lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @lightbulb.command(name="time", aliases=["set_time", "settime"], help='تغير وقت ارسال الاذكار')
    async def set_timer(self, ctx: Context):
        guild = self.db.get_guild(ctx.guild_id)
        embed = hikari.Embed(color=0xffd430) 
        if not guild.channel_id:
            embed.description = "يجب عليك تثبيت روم لاستعمال هاذ الامر"
            await ctx.respond(embed=embed, reply=True, mentions_reply=False)
            return
        embed.description = "اختر الوقت المناسب من خلال القائمة في الأسفل"
        menu = ctx.bot.rest.build_action_row()
        times = {
            "1800": "30 دقيقة",
            "3600": "ساعه",
            "7200": "ساعتين",
            "21600": "6 ساعات",
            "43200": "12 ساعه",
            "86400": "24 ساعه",
            "7": "الغاء"
        }
        select = menu.add_select_menu("timer")
        for value, label in times.items():
            if value == "7":
                select.add_option(label, value).set_emoji("❌").add_to_menu()
                continue
            select.add_option(label, value).add_to_menu()
        select.set_placeholder("اختر الوقت المناسب")
        select.set_max_values(1)
        select.set_min_values(1)
        select.set_is_disabled(False)
        select.add_to_container()

        msg = await ctx.respond(embed=embed, component=menu, reply=True, mentions_reply=False)
        def check(res):
            return res.interaction.user.id == ctx.author.id and \
                res.interaction.channel_id == ctx.channel_id
        select.set_is_disabled(True)
        try:
            event = await ctx.bot.wait_for(hikari.InteractionCreateEvent, predicate=check, timeout=15)
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE)
        except asyncio.TimeoutError:
            embed.description = "تم الغاء الامر بسبب انتهاء الوقت الازم"
            await msg.edit(embed=embed, component=menu)
            return
        value = event.interaction.values[0]
        label = times.get(value)
        if value == "7":
            embed.description = "تم الغاء الامر"
            await msg.edit(embed=embed, component=menu)
            return
        self.db.update_guild(guild, GuildUpdateType.time, int(value))
        select.set_is_disabled(True)
        select.set_placeholder("تم اختيار %s" % label)
        embed.description = "تم تغير وقت ارسال الأذكار إلى: **%s**" % label
        await msg.edit(embed=embed, component=menu)

    @lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @lightbulb.command(name="setroom", aliases=["channel", "setchannel", "set_room", "set_channel"])
    async def set_channel_command(self, ctx: Context, channel: lightbulb.text_channel_converter):
        guild = self.db.get_guild(ctx.guild_id)
        embed = hikari.Embed(color=0xffd430)
        if channel.id == guild.channel_id:
            embed.description = "لقد قمت بتحديد هاذه الروم من قبل"
            await ctx.respond(embed=embed, reply=True, mentions_reply=False)
            return 
        self.db.update_guild(guild, GuildUpdateType.channel, channel.id)
        embed.description = "! الله يكتب اجرك راح ارسل الاذكار للروم %s" % channel.mention
        await ctx.respond(embed=embed, reply=True, mentions_reply=False)


    @lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    @lightbulb.command(name="remove", aliases=["removeroom"])
    async def remove_command(self, ctx: Context):
        guild = self.db.get_guild(ctx.guild_id)
        embed = hikari.Embed(color=0xffd430)
        channel = guild.channel_id
        yes = await ctx.bot.emojis.yes
        no = await ctx.bot.emojis.no

        if not channel:
            embed.description = "انت لم تقم بتثبيت الروم من قبل"
            await ctx.respond(embed=embed, reply=True, mentions_reply=False)
            return 
        embed.description = "هل انت موافق على ايقاف ارسال الاذكار في روم <#%s>" % channel
        buttons = ctx.bot.rest.build_action_row()

        true = buttons.add_button(ButtonStyle.SUCCESS, "true")
        true.set_label("موافق")
        true.set_emoji(yes)
        true.add_to_container()

        false = buttons.add_button(ButtonStyle.DANGER, "false")
        false.set_label("غير موافق")
        false.set_emoji(no)
        false.add_to_container()
        
        msg = await ctx.respond(embed=embed, component=buttons, reply=True, mentions_reply=False)

        def check(res):
            return res.interaction.user.id == ctx.author.id and \
                res.interaction.channel_id == ctx.channel_id and \
                res.interaction.custom_id in ["true", "false"] 
        
        true.set_is_disabled(True)
        false.set_is_disabled(True)
        try:
            event = await ctx.bot.wait_for(hikari.InteractionCreateEvent, predicate=check, timeout=15)
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE)
        except asyncio.TimeoutError:
            embed.description = "تم الغاء الأمر بسبب نفاذ الوقت"
            await msg.edit(embed=embed, component=buttons)
            return
        if event.interaction.custom_id == "true":
            self.db.update_guild(guild, GuildUpdateType.channel, None)
            embed.description = "تم الغاء ارسال الاذكار بنجاح"
            await msg.edit(embed=embed, component=buttons)
            return
        embed.description = "تم الغاء الأمر"
        await msg.edit(embed=embed, component=buttons)


def load(bot: Bot):
    bot.add_plugin(Admin(bot=bot))


def unload(bot: Bot):
    bot.remove_plugin("Admin")
