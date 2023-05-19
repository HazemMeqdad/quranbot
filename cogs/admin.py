import discord
from discord.ext import commands
from discord import app_commands
from utlits import Pray
import aiohttp
from utlits.msohaf_data import moshafs, moshaf_types
from datetime import datetime
import typing as t
from utlits.views import OpenMoshafView
from database import Database, DataNotFound
from database.objects import DbGuild, Azan

@app_commands.default_permissions(administrator=True)
@app_commands.guild_only()
class Admin(commands.GroupCog, name="set"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="embed", description="تغير خاصية أرسال الأذكار و الأدعية إلى أمبد 📋")
    @app_commands.describe(mode="تحديد الوضع True(تفعيل)/False(إيقاف)")
    async def set_embed_command(self, interaction: discord.Interaction, mode: bool) -> None:
        try:
            data = await Database.find_one("guilds", {"_id": interaction.guild_id})
        except DataNotFound:
            data = DbGuild(interaction.guild_id)
            await Database.insert("guilds", data)
        await Database.update_one("guilds", {"_id": interaction.guild_id}, {"embed": mode})
        if data.embed:
            await interaction.response.send_message("تم تفعيل خاصية الأمبد بنجاح ✅")
        else:
            await interaction.response.send_message("تم إيقاف خاصية الأمبد بنجاح ✅")

    @app_commands.command(name="time", description="تغير وقت الأذكار و الأدعية 🕒")
    @app_commands.describe(time="وقت الأذكار و الأدعية")
    @app_commands.choices(
        time=[app_commands.Choice(name=Pray.times.get(i), value=i) for i in list(Pray.times.keys())]
    )
    async def set_time_command(self, interaction: discord.Interaction, *, time: int):
        try:
            data = await Database.find_one("guilds", {"_id": interaction.guild_id})
        except DataNotFound:
            data = DbGuild(interaction.guild_id)
            await Database.insert("guilds", data)
        if not data.channel_id:
            return await interaction.response.send_message("يجب تحديد قناة أولاً, أستخدم أمر `set pray` 📌", ephemeral=True)

        await Database.update_one("guilds", {"_id": interaction.guild_id}, {"time": time})

        await interaction.response.send_message(f"تم تغير وقت الأذكار و الأدعية إلى {Pray.times.get(time)} بنجاح ✅")

    @app_commands.command(name="azan", description="تعين قناة أرسال الصلاة 📌")
    @app_commands.describe(
        channel="القناة التي سيتم أرسال الصلاة فيها", 
        address="العنوان الذي سيتم أرسال حساب أوقات الصلاة فية",
        role="الترتبة التي يتم منشنها عند أرسال الصلاة"
    )
    async def set_prayer_command(self, interaction: discord.Interaction, channel: discord.TextChannel, address: str, role: t.Optional[discord.Role] = None):
        try:
            await Database.find_one("guilds", {"_id": interaction.guild_id})
            await Database.delete_one("azan", {"_id": interaction.guild_id})
        except DataNotFound:
            ...
        async with aiohttp.ClientSession() as session:
            async with session.get("http://api.aladhan.com/v1/timingsByAddress?address=%s&method=5" % (
                address
            )) as resp:
                res = await resp.json()
                if res["code"] != 200:
                    return await interaction.response.send_message("لم يتم العثور على العنوان المدخل", ephemeral=True)
        channel_hooks = await self.bot.http.channel_webhooks(channel.id)
        hooks = list(filter(lambda x: x["user"]["id"] == str(self.bot.user.id) and x["type"] == 1, channel_hooks))
        if hooks:
            hook = hooks[0]
        else:
            hook = await channel.create_webhook(name="فاذكروني")
        obj = Azan(
            interaction.guild_id, 
            channel_id=channel.id, 
            address=address,
            role_id=role.id if role else None,
            webhook_url=hook.url if isinstance(hook, discord.Webhook) else "https://discord.com/api/webhooks/%s/%s" % (hook["id"], hook["token"])
        )
        await Database.insert("azan", obj)
        await interaction.response.send_message(f"تم تحديد القناة الخاصة بالأذكار بنجاح ✅")
        data = res["data"]
        next_azan = Pray.get_next_azan_time(data["timings"], data["meta"]["timezone"])
        embed = discord.Embed(
            title="أوقات الصلاة في %s" % address + " ليوم %s" % datetime.fromtimestamp(int(data["date"]["timestamp"])).strftime("%d/%m/%Y"),
            color=0xffd430,
            timestamp=datetime.fromtimestamp(int(data["date"]["timestamp"]))
        )
        embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/451230075875504128/ZRTmO08X.jpeg")
        embed.add_field(name="صلاة الفجْر:", value=Pray.format_time_str(data["timings"]["Fajr"]))
        embed.add_field(name="الشروق:", value=Pray.format_time_str(data["timings"]["Sunrise"]))
        embed.add_field(name="صلاة الظُّهْر:", value=Pray.format_time_str(data["timings"]["Dhuhr"]))
        embed.add_field(name="صلاة العَصر:", value=Pray.format_time_str(data["timings"]["Asr"]))
        embed.add_field(name="صلاة المَغرب:", value=Pray.format_time_str(data["timings"]["Maghrib"]))
        embed.add_field(name="صلاة العِشاء:", value=Pray.format_time_str(data["timings"]["Isha"]))
        embed.add_field(name=f"تبقى على وقت صلاة {Pray.AZAN_DATA[next_azan[0]]['name']}:", value=discord.utils.format_dt(next_azan[1], "R"))
        await interaction.channel.send(embed=embed)

    @app_commands.command(name="pray", description="تعين قناة أرسال الأذكار و الأدعية 📌")
    @app_commands.describe(channel="القناة التي سيتم أرسال الأذكار و الأدعية فيها")
    async def set_pray_command(self, interaction: discord.Interaction, channel: discord.TextChannel):
        try:
            data = await Database.find_one("guilds", {"_id": interaction.guild_id})
        except DataNotFound:
            data = DbGuild(interaction.guild_id)
            await Database.insert("guilds", data)
        if not interaction.guild.me.guild_permissions.manage_webhooks:
            return await interaction.response.send_message("البوت لا يمتلك صلاحات التحكم بالويب هوك\n`MANAGE_WEBHOOKS`", ephemeral=True)
        channel_hooks = await self.bot.http.channel_webhooks(channel.id)
        hooks = list(filter(lambda x: x["user"]["id"] == str(self.bot.user.id) and x["type"] == 1, channel_hooks))
        if hooks:
            hook = hooks[0]
        else:
            hook = await channel.create_webhook(name="فاذكروني")
        print(1)
        await Database.update_one("guilds", {"_id": interaction.guild_id}, {"webhook_url": hook.url if isinstance(hook, discord.Webhook) else hook.get("url")})

        print(2)
        print(channel.id)
        await Database.update_one("guilds", {"_id", interaction.guild_id}, {"channel_id": 123})
        
        print(3)
        await interaction.response.send_message(f"تم تعين قناة الأذكار و الأدعية إلى {channel.mention} بنجاح ✅")

    @app_commands.command(name="moshaf", description="تعين لوحة للقرآن الكريم 📚")
    @app_commands.choices(moshaf_type=[app_commands.Choice(name=i["name"], value=i["value"]) for i in moshaf_types])
    @app_commands.describe(moshaf_type="نوع القرآن الكريم")
    @app_commands.default_permissions(manage_guild=True)
    async def setup(self, interaction: discord.Interaction, moshaf_type: int) -> None:
        try:
            data = await Database.find_one("guilds", {"_id": interaction.guild_id})
        except DataNotFound:
            data = DbGuild(interaction.guild_id)
            await Database.insert("guilds", data)
            
        moshaf = [i for i in moshaf_types if i["value"] == moshaf_type][0]

        embed = discord.Embed(title=moshaf["name"], color=0xffd430)
        embed.set_image(url=moshafs[str(moshaf["value"])]["cover"])
        embed.set_footer(text="أضغط على الزر الموجود أسفل لفتح المصحف")

        await Database.update_one("guilds", {"_id": interaction.guild_id}, {"moshaf_type": moshaf_type})
        await interaction.response.send_message("تم تعيين لوحة القرآن الكريم بنجاح", ephemeral=True)
        await interaction.channel.send(embed=embed, view=OpenMoshafView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
