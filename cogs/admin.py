import io
import discord
from discord.ext import commands
from discord import app_commands
from .utlits.db import AzanDatabase, Database
from .utlits import times
import aiohttp
from datetime import datetime
import typing as t


class Admin(commands.GroupCog, name="set"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="embed", description="تغير خاصية أرسال الأذكار و الأدعية إلى أمبد 📋")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(mode="تحديد الوضع True(تفعيل)/False(إيقاف)")
    async def set_embed_command(self, interaction: discord.Interaction, mode: bool) -> None:
        db = Database()
        data = db.find_guild(interaction.guild.id)
        if not data:
            db.insert_guild(interaction.guild.id)
            data = db.find_guild(interaction.guild.id)
        db.update_guild(interaction.guild.id, embed=mode)
        if data.embed:
            await interaction.response.send_message("تم تفعيل خاصية الأمبد بنجاح ✅")
        else:
            await interaction.response.send_message("تم إيقاف خاصية الأمبد بنجاح ✅")

    @app_commands.command(name="time", description="تغير وقت الأذكار و الأدعية 🕒")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(time="وقت الأذكار و الأدعية")
    @app_commands.choices(
        time=[app_commands.Choice(name=times.get(i), value=i) for i in list(times.keys())]
    )
    async def set_time_command(self, interaction: discord.Interaction, *, time: int):
        db = Database()
        data = db.find_guild(interaction.guild.id)
        if not data:
            db.insert_guild(interaction.guild.id)
            data = db.find_guild(interaction.guild.id)
        if not data.channel_id:
            return await interaction.response.send_message("يجب تحديد قناة أولاً, أستخدم أمر `set pray` 📌", ephemeral=True)

        db.update_guild(interaction.guild.id, time=time)

        await interaction.response.send_message(f"تم تغير وقت الأذكار و الأدعية إلى {times.get(time)} بنجاح ✅")

    @app_commands.command(name="azan", description="تعين قناة أرسال الصلاة 📌")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(
        channel="القناة التي سيتم أرسال الصلاة فيها", 
        address="العنوان الذي سيتم أرسال حساب أوقات الصلاة فية",
        role="الترتبة التي يتم منشنها عند أرسال الصلاة"
    )
    async def set_prayer_command(self, interaction: discord.Interaction, channel: discord.TextChannel, address: str, role: t.Optional[discord.Role] = None):
        db, azan_db = Database(), AzanDatabase()
        data = azan_db.find_guild(interaction.guild.id)
        if data:
            azan_db.delete(interaction.guild.id)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://api.aladhan.com/v1/timingsByAddress?address=%s&method=5" % (
                address
            )) as resp:
                res = await resp.json()
                if res["code"] != 200:
                    return await interaction.response.send_message("لم يتم العثور على العنوان المدخل", ephemeral=True)
        hooks = await channel.webhooks()
        hook = discord.utils.get(hooks, name="فاذكروني")
        if not hook:
            hook = await channel.create_webhook(name="فاذكروني")
        azan_db.insert(
            interaction.guild.id, channel_id=channel.id, 
            address=address, role_id=role.id if role else None,
            webhook_url=hook.url
        )
        await interaction.response.send_message(f"تم تحديد القناة الخاصة بالأذكار بنجاح ✅")
        data = res["data"]
        embed = discord.Embed(
            title="أوقات الصلاة في %s" % address + " ليوم %s" % datetime.fromtimestamp(int(data["date"]["timestamp"])).strftime("%d/%m/%Y"),
            color=0xffd430,
            timestamp=datetime.fromtimestamp(int(data["date"]["timestamp"]))
        )
        embed.add_field(name="صلاة الفجْر:", value=data["timings"]["Fajr"])
        embed.add_field(name="الشروق:", value=data["timings"]["Sunrise"])
        embed.add_field(name="صلاة الظُّهْر:", value=data["timings"]["Dhuhr"])
        embed.add_field(name="صلاة العَصر:", value=data["timings"]["Asr"])
        embed.add_field(name="صلاة المَغرب:", value=data["timings"]["Maghrib"])
        embed.add_field(name="صلاة العِشاء:", value=data["timings"]["Isha"])
        await interaction.channel.send(embed=embed)

    @app_commands.command(name="pray", description="تعين قناة أرسال الأذكار و الأدعية 📌")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(channel="القناة التي سيتم أرسال الأذكار و الأدعية فيها")
    async def set_pray_command(self, interaction: discord.Interaction, channel: discord.TextChannel):
        db = Database()
        data = db.find_guild(interaction.guild.id)
        if not data:
            db.insert_guild(interaction.guild.id)
        if not interaction.guild.me.guild_permissions.manage_webhooks:
            return await interaction.response.send_message("البوت لا يمتلك صلاحات التحكم بالويب هوك\n`MANAGE_WEBHOOKS`", ephemeral=True)
        hook = await channel.create_webhook(
            name="فاذكروني", 
            avatar=(await self.bot.user.avatar.read()),
            reason="لإحياء سنة ذِكر الله"
        )
        db.update_guild(interaction.guild.id, channel_id=channel.id, webhook={"id": hook.id, "token": hook.token})
        await interaction.response.send_message(f"تم تعين قناة الأذكار و الأدعية إلى {channel.mention} بنجاح ✅")



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
