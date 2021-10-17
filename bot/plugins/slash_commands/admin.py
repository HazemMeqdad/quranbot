from sys import flags
import time
import hikari
import asyncio
import lightbulb
from lightbulb.context import Context
from lightbulb.errors import CommandError
from bot.utils import check_permission
from lightbulb.slash_commands.context import SlashCommandContext
from lightbulb.slash_commands import SlashCommand
from lightbulb.slash_commands import Option
import typing
from bot import Bot
from bot import db
from hikari.messages import ButtonStyle


GUILD_ID = 872200812129054730

async def send_error_message(context: SlashCommandContext, permission: str = "manage_guild"):
    await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE, flags=hikari.MessageFlag.EPHEMERAL)
    error_emoji = await context.bot.emojis.error
    embed = hikari.Embed(description=f"{error_emoji} - أنت بحاجة إلى صلاحيات `{permission}`", color=0xE50000)
    await context.interaction.edit_initial_response(embed=embed)


class Prefix(SlashCommand):
    name = "prefix"
    description = "تغير البادئة الخاصة بالخادم"
    enable_guilds = (GUILD_ID,)

    new_prefix: typing.Optional[str] = Option(description="البادئة الجديدة", name="البادئة", required=True)

    async def callback(self, context: SlashCommandContext):
        if check_permission(context, hikari.Permissions.MANAGE_GUILD) is False:
            await send_error_message(context)
            return
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
    
        new_prefix = context.option_values._options.get("البادئة").value
        embed = hikari.Embed(color=0xffd430)
        x = db.Guild(context.guild_id)
        error = await self.bot.emojis.error
        if len(new_prefix) > 5:
            raise CommandError("%s لا يمكنك وضع بادئه اكثر من خمس حروف" % error)
        await x.update_where(db.GuildUpdateType.prefix, new_prefix)
        embed.description = "تم تغير البادئه الى `%s`" % new_prefix
        await context.interaction.edit_initial_response(embed=embed)


class AntiSpam(SlashCommand):
    name = "anti_spam"
    description = "عدم تكرار الرسائل, ينصح باستخدامه في الشاتات المفتوحه"
    enable_guilds = (GUILD_ID,)

    mode: bool = Option("تحديد الوضع", name="الوضع", required=True)

    async def callback(self, context: SlashCommandContext):
        if check_permission(context, hikari.Permissions.MANAGE_GUILD) is False:
            await send_error_message(context)
            return
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        x = db.Guild(context.guild_id)
        mode = context.option_values._options.get("الوضع").value
        msg = "تم تفعيل خاصية تكرار الرسائل" if mode else "تم اطفاء خاصية تكرار الرسائل"

        await x.update_where(db.GuildUpdateType.anti_spam, mode)
        embed = hikari.Embed(
            description=msg,
            color=0xffd430
        )
        await context.interaction.edit_initial_response(embed=embed)

class Embed(SlashCommand):
    name = "embed"
    description = "تغير خاصيه ارسال الاذكار الى امبد"
    enable_guilds = (GUILD_ID,)

    mode: bool = Option("تحديد الوضع", name="الوضع", required=True)

    async def callback(self, context: SlashCommandContext):
        if check_permission(context, hikari.Permissions.MANAGE_GUILD) is False:
            await send_error_message(context)
            return
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        x = db.Guild(context.guild_id)
        mode = context.option_values._options.get("الوضع").value
        msg = "تم تفعيل خاصية الأمبد" if mode else "تم اطفاء خاصية الأمبد"

        await x.update_where(db.GuildUpdateType.embed, mode)
        embed = hikari.Embed(
            description=msg,
            color=0xffd430
        )
        await context.interaction.edit_initial_response(embed=embed)

times = {
    "30 دقيقة": 1800, 
    "ساعه": 3600, 
    "ساعتين": 7200,
    "6 ساعات": 21600,
    "12 ساعه": 43200,
    "24 ساعه": 86400,
}

class Time(SlashCommand):
    name = "time"
    description = "تغير وقت ارسال الأذكار"
    enable_guilds = (GUILD_ID,)

    choice: str = Option("أختر الوقت المناسب", name="الوقت", required=True, choices=times.keys())
    async def callback(self, context: SlashCommandContext):
        if check_permission(context, hikari.Permissions.MANAGE_GUILD) is False:
            await send_error_message(context)
            return
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        x = db.Guild(context.guild_id)
        embed = hikari.Embed(color=0xffd430)
        if not x.info["channel"]:
            raise CommandError("يجب عليك تثبيت روم لاستعمال هاذ الامر")
        value = context.option_values._options.get("الوقت").value
        await x.update_where(db.GuildUpdateType.time, times.get(value))
        embed.description = "تم تغير وقت ارسال الأذكار إلى: **%s**" % value
        await context.interaction.edit_initial_response(embed=embed)

class SetRoom(SlashCommand):
    name = "setroom"
    description = "تغير خاصيه ارسال الاذكار الى امبد"
    enable_guilds = (GUILD_ID,)

    channel: hikari.TextableChannel = Option("أختر القناة المناسبة", name="القناة", required=True)
    async def callback(self, context: SlashCommandContext):
        if check_permission(context, hikari.Permissions.MANAGE_GUILD) is False:
            await send_error_message(context)
            return 

        x = db.Guild(context.guild_id)
        channel_id = context.option_values._options.get("القناة").value
        channel = context.get_guild().get_channel(channel_id)
        embed = hikari.Embed(color=0xffd430)

        if channel.type != hikari.ChannelType.GUILD_TEXT:
            raise CommandError("يجب التأكد من نوع القناة المحدده من انها كتابية")
        if int(channel_id) == x.info["channel"]:
            raise CommandError("لقد قمت بتحديد هاذه الروم من قبل")
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        await x.update_where(db.GuildUpdateType.channel, channel.id)
        embed.description = "! الله يكتب اجرك راح ارسل الاذكار للروم %s" % channel.mention
        await context.interaction.edit_initial_response(embed=embed)

class Remove(SlashCommand):
    name = "remove"
    description = "توقف البوت عن إرسال الأذكار"
    enable_guilds = (GUILD_ID,)
    
    async def callback(self, context: SlashCommandContext):
        if check_permission(context, hikari.Permissions.MANAGE_GUILD) is False:
            await send_error_message(context)
            return

        x = db.Guild(context.guild_id)
        embed = hikari.Embed(color=0xffd430)
        channel = x.info["channel"]
        if not channel:
            raise CommandError("انت لم تقم بتثبيت الروم من قبل")
        await context.interaction.create_initial_response(hikari.ResponseType.DEFERRED_MESSAGE_CREATE)
        yes = await context.bot.emojis.yes
        no = await context.bot.emojis.no
        embed.description = "هل انت موافق على ايقاف ارسال الاذكار في روم <#%s>" % channel
        buttons = context.bot.rest.build_action_row()

        true = buttons.add_button(ButtonStyle.SUCCESS, "true")
        true.set_label("موافق")
        true.set_emoji(yes)
        true.add_to_container()

        false = buttons.add_button(ButtonStyle.DANGER, "false")
        false.set_label("غير موافق")
        false.set_emoji(no)
        false.add_to_container()
        
        await context.interaction.edit_initial_response(embed=embed, component=buttons)

        def check(res):
            return res.interaction.user.id == context.author.id and \
                res.interaction.channel_id == context.channel_id and \
                res.interaction.custom_id in ["true", "false"] 
        
        true.set_is_disabled(True)
        false.set_is_disabled(True)
        try:
            event = await context.bot.wait_for(hikari.InteractionCreateEvent, predicate=check, timeout=15)
            await event.interaction.create_initial_response(hikari.ResponseType.MESSAGE_UPDATE)
        except asyncio.TimeoutError:
            embed.description = "تم الغاء الأمر بسبب نفاذ الوقت"
            await context.interaction.edit_initial_response(embed=embed, component=buttons)
            return
        if event.interaction.custom_id == "true":
            await x.update_where(db.GuildUpdateType.channel, None)
            embed.description = "تم الغاء ارسال الاذكار بنجاح"
            await context.interaction.edit_initial_response(embed=embed, component=buttons)
            return
        embed.description = "تم الغاء الأمر"
        await context.interaction.edit_initial_response(embed=embed, component=buttons)

def load(bot: Bot):
    bot.add_slash_command(Prefix, True)
    bot.add_slash_command(AntiSpam, True)
    bot.add_slash_command(Embed, True)
    bot.add_slash_command(Time, True)
    bot.add_slash_command(SetRoom, True)
    bot.add_slash_command(Remove, True)


def unload(bot: Bot):
    bot.remove_slash_command("prefix")
    bot.remove_slash_command("anti_spam")
    bot.remove_slash_command("embed")
    bot.remove_slash_command("time")
    bot.remove_slash_command("setroom")
    bot.remove_slash_command("remove")
