import json
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
from cogs.utlits.views import AzanView
from .utlits.database import Azan, AzanDatabase, Database, DbGuild
import aiohttp
import discord
import aioredis
from .utlits import AZAN_DATA, between_two_numbers, get_next_azan
import typing as t
import pytz

class Tasks(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.redis: aioredis.Redis = bot.redis

    async def cog_load(self) -> None:
        self.pray_checker.start()
        self.azan_checker.start()

    async def cog_unload(self) -> None:
        self.pray_checker.cancel()
        self.azan_checker.cancel()

    async def get_pray(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cdn.fdrbot.com/pray/random") as resp:
                data = await resp.json()
                return data

    async def process_guild(self, data: DbGuild):
        db = Database()
        channel = self.bot.get_channel(data.channel_id)
        guild = self.bot.get_guild(data._id)
        pray = await self.get_pray()
        if not channel or not guild or not guild.me.guild_permissions.manage_webhooks:
            db.update_guild(data._id, channel_id=None, webhook=None)
            return
        try:
            async with aiohttp.ClientSession() as session:
                webhook_url = "https://discord.com/api/webhooks/%s/%s" % (data.webhook["id"], data.webhook["token"])
                hook = discord.Webhook.from_url(webhook_url, session=session)

                embed = discord.Embed(
                    title=pray["id"],
                    description=pray["text"],
                    color=0xffd430
                )
                embed.set_thumbnail(url=self.bot.user.avatar.url)
                embed.set_footer(text="بوت فاذكروني لإحياء سنة ذِكر الله", icon_url=self.bot.user.avatar.url)
                new_datetime = datetime.now().timestamp() + data.time
                db.update_guild(data._id, next_zker=datetime.fromtimestamp(new_datetime))
                if data.embed:
                    await hook.send(
                        embed=embed, 
                        username=self.bot.user.name,
                        avatar_url=self.bot.user.avatar.url
                    )
                    return  
                await hook.send(
                    f"> {pray['text']}", 
                    username=self.bot.user.name,
                    avatar_url=self.bot.user.avatar.url
                )
        except (discord.HTTPException, discord.NotFound, discord.Forbidden):
            db.update_guild(data._id, channel_id=None, webhook=None)
        
    @tasks.loop(minutes=15)
    async def pray_checker(self):
        await self.bot.wait_until_ready()
        db = Database()
        guilds = db.fetch_guilds_with_datetime()
        for guild in guilds:
            await self.process_guild(guild)

    async def get_prayertimes_by_address(self, address: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.aladhan.com/v1/timingsByAddress?address={address}&method=5") as resp:
                data = await resp.json()
                return data["data"]

    async def process_azan(self, data: Azan, azan: t.Tuple[str, str], addres_data: dict):
        db = AzanDatabase()
        guild = self.bot.get_guild(data._id)
        channel = self.bot.get_channel(data.channel_id)
        if await self.redis.exists(f"azan:guild:{guild.id}"):
            return
        if not channel or not guild or not guild.me.guild_permissions.manage_webhooks:
            db.delete(data._id)
            return
        try:
            async with aiohttp.ClientSession() as session:
                hook = discord.Webhook.from_url(data.webhook_url, session=session)
                date = datetime.now(pytz.timezone(addres_data["meta"]["timezone"]))
                azan_data  = AZAN_DATA[azan[0]]
                next_azan = get_next_azan(azan[0])
                data_next_azan = addres_data["timings"][next_azan]
                next_azan_date = datetime.fromtimestamp(datetime(date.year, date.month, date.day).timestamp() + (int(data_next_azan.split(":")[0]) * 3600) + (int(data_next_azan.split(":")[1]) * 60))
                embed = discord.Embed(
                    title=f"**حان الآن وقت صلاة {azan_data['name']} بتوقيت {data.address}**",
                    description=f"**يوم {date.strftime('%d/%m/%Y')}م الموافق {addres_data['date']['hijri']['weekday']['ar']} {addres_data['date']['hijri']['date'].replace('-', '/')}هـ**",
                    color=0xffd430
                )
                embed.set_author(name="مواقيت الصلاة")
                embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/451230075875504128/ZRTmO08X.jpeg")
                embed.set_footer(text="بوت فاذكروني لإحياء سنة ذِكر الله", icon_url=self.bot.user.avatar.url)
                sunau_before = f"**{azan_data['sunna_before']}** ركعات" if azan_data['sunna_before'] != 0 else "**لايوجد**"
                sunau_after = f"**{azan_data['sunna_after']}** ركعات" if azan_data['sunna_after'] != 0 else "**لايوجد**"
                embed.add_field(
                    name=f"صلاة {azan_data['name']}", 
                    value=f"عدد ركعاتها: **{azan_data['rakats']}** ركعات\n"
                        f"سنن قبل الصلاة: {sunau_before}\n" 
                        f"سنن بعد الصلاة: {sunau_after}",
                    inline=False
                )
                embed.add_field(
                    name=f"وقت الصلاة التالي {AZAN_DATA[next_azan]['name']} بعد:",
                    value=f"<t:{int(next_azan_date.timestamp())}:R>"
                )
                await hook.send(
                    content=("<@&%d>" % data.role_id) if data.role_id else "",
                    embed=embed, 
                    username=self.bot.user.name,
                    avatar_url=self.bot.user.avatar.url,
                    allowed_mentions=discord.AllowedMentions.all(),
                )
                await self.redis.set(f"azan:guild:{guild.id}", "1", ex=60*60*2)
        except (discord.HTTPException, discord.NotFound, discord.Forbidden):
            db.delete(data._id)

    def get_colser_azan(self, timings: dict, now: datetime) -> t.Tuple[str, datetime]:
        for key, value in timings.items():
            if key not in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
                continue
            h = int(value.split(":")[0])
            m = int(value.split(":")[1])
            if h == now.hour and between_two_numbers(m, now.minute-2, now.minute+2):
                return key, value
        return None

    @tasks.loop(minutes=2)
    async def azan_checker(self):
        db = AzanDatabase()
        for azan in db.find_all():
            address = azan.address
            if await self.redis.exists(f"azan:{address}"):
                data = json.loads(await self.redis.get(f"azan:{address}"))
            else:
                data = await self.get_prayertimes_by_address(address)
                await self.redis.set(f"azan:{address}", json.dumps(data), ex=3600)
            now = datetime.now(tz=pytz.timezone(data["meta"]["timezone"]))
            close_azan = self.get_colser_azan(data["timings"], now)
            if not close_azan:
                continue
            await self.process_azan(azan, close_azan, data)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tasks(bot))
