from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
import aiohttp
import discord
from utlits import Pray
import typing as t
import pytz
import json
from database import Database
from database.objects import Azan, DbGuild
from utlits.cache import Cache


class Tasks(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.cache: Cache = Cache(60 * 60 * 12)
        self.azan_cache = Cache(60 * 60 * 1)

    async def cog_load(self) -> None:
        self.pray_checker.start()
        self.azan_checker.start()

    async def cog_unload(self) -> None:
        self.pray_checker.cancel()
        self.azan_checker.cancel()

    async def process_guild(self, data: DbGuild):
        channel = self.bot.get_channel(data.channel_id)
        guild = self.bot.get_guild(data._id)
        pray = Pray.get_pray()
        if not channel or not guild or not guild.me.guild_permissions.manage_webhooks:
            await Database.update_one("guilds", {"_id": data._id}, {"channel_id": None, "webhook": None})
            return
        try:
            async with aiohttp.ClientSession() as session:
                hook = discord.Webhook.from_url(data.webhook_url, session=session)
                embed = discord.Embed(
                    title=pray["category"],
                    description=pray["zekr"],
                    color=0xffd430,
                    timestamp=datetime.now()
                )
                embed.set_thumbnail(url=self.bot.user.avatar.url)
                embed.set_footer(text="بوت فاذكروني لإحياء سنة ذِكر الله", icon_url=self.bot.user.avatar.url)
                if pray.get("description") and pray.get("description").get("arabic"):
                    embed.add_field(name="وصف", value=pray["description"]["arabic"], inline=False)
                if pray.get("reference") != False:
                    embed.add_field(name="المرجعي", value=pray["reference"])
                if pray.get("number") != False:
                    embed.add_field(name="تكرار", value=pray["number"])
                new_datetime = datetime.now().timestamp() + data.time
                await Database.update_one("guilds", {"_id": data._id}, {"next_zker": datetime.fromtimestamp(new_datetime)})
                if data.embed:
                    await hook.send(
                        embed=embed, 
                        username=self.bot.user.name,
                        avatar_url=self.bot.user.avatar.url
                    )
                    return
                await hook.send(
                    f"**{pray['category']}**\n> {pray['zekr']}", 
                    username=self.bot.user.name,
                    avatar_url=self.bot.user.avatar.url
                )
        except (discord.HTTPException, discord.NotFound, discord.Forbidden):
            await Database.update_one("guilds", {"_id": data._id}, {"channel_id": None, "webhook": None})
        
    @tasks.loop(minutes=15)
    async def pray_checker(self):
        await self.bot.wait_until_ready()
        guilds = await Database.find("guilds", {
            "next_zker": {"$lt": datetime.now()}, 
            "channel_id": {"$ne": None}, 
            "webhook_url": {"$ne": None}
        })
        for g in guilds:
            guild = DbGuild.from_kwargs(**g)
            await self.process_guild(guild)

    async def get_prayertimes_by_address(self, address: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.aladhan.com/v1/timingsByAddress?address={address}&method=5") as resp:
                data = await resp.json()
                return data["data"]

    async def process_azan(self, data: Azan, azan: t.Tuple[str, str], addres_data: dict):
        guild = self.bot.get_guild(data._id)
        channel = self.bot.get_channel(data.channel_id)
        if self.azan_cache.has(f"azan:guild:{guild.id}"):
            return
        if not channel or not guild or not guild.me.guild_permissions.manage_webhooks:
            await Database.delete_one("azan", {"_id": data._id})
            return
        try:
            async with aiohttp.ClientSession() as session:
                hook = discord.Webhook.from_url(data.webhook_url, session=session)
                date = datetime.now(pytz.timezone(addres_data["meta"]["timezone"]))
                azan_data  = Pray.AZAN_DATA[azan[0]]
                next_azan = Pray.get_next_azan_time(addres_data["timings"], addres_data["meta"]["timezone"])
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
                if next_azan != (None, None):
                    embed.add_field(
                        name=f"وقت الصلاة التالي {Pray.AZAN_DATA[next_azan[0]]['name']} بعد:",
                        value=discord.utils.format_dt(next_azan[1], "R")
                    )
                await hook.send(
                    content=("<@&%d>" % data.role_id) if data.role_id else "",
                    embed=embed, 
                    username=self.bot.user.name,
                    avatar_url=self.bot.user.avatar.url,
                    allowed_mentions=discord.AllowedMentions.all(),
                )
                self.azan_cache.set(f"azan:guild:{guild.id}", "1")
        except (discord.HTTPException, discord.NotFound, discord.Forbidden):
            await Database.delete_one("azan", {"_id": data._id})

    @tasks.loop(minutes=2)
    async def azan_checker(self):
        data = await Database.find("azan", {})
        for a in data:
            azan = Azan.from_kwargs(**a)
            address = azan.address
            if self.cache.has(f"azan:{address}"):
                data = json.loads(self.cache.get(f"azan:{address}"))
            else:
                data = await self.get_prayertimes_by_address(address)
                self.cache.set(f"azan:{address}", json.dumps(data))
            now = datetime.now(tz=pytz.timezone(data["meta"]["timezone"]))
            close_azan = Pray.get_colser_azan(data["timings"], now)
            if not close_azan:
                continue
            await self.process_azan(azan, close_azan, data)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tasks(bot))
