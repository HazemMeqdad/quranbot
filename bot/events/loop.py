from discord.ext import tasks
import bot.db as db
import discord
from discord.utils import get
from discord.ext.commands import Cog


async def send(client, time: int):
    for i in db.get_all_channels_by_time(time):
        guild: discord.Guild = client.get_guild(i[0])
        if not guild:
            continue
        x = db.Guild(guild)
        channel = guild.get_channel(x.info.get("channel"))
        if not channel:
            continue
        if x.info.get("anti_spam"):
            try:
                message = await channel.fetch_message(channel.last_message_id)
                if message.author == client.user:
                    continue
            except:
                continue
        try:
            z = db.Azkar().random
            if x.info.get("embed"):
                embed = discord.Embed(
                    title=str(z["_id"]),
                    description=z["msg"],
                    color=discord.Color.gold()
                )
                embed.set_footer(text=client.footer, icon_url=client.user.avatar_url)
                embed.set_thumbnail(url=client.user.avatar_url)
                if guild.me.permissions_in(channel).manage_webhooks:
                    webhooks = await channel.webhooks()
                    webhook = get(webhooks, name='فاذكروني')
                    if not webhook:
                        webhook = await channel.create_webhook(
                            name="فاذكروني",
                            avatar=await client.user.avatar_url.read(),
                            reason=client.footer
                        )
                    await webhook.send(embed=embed)
                    continue
                await channel.send(embed=embed)
                continue
            if guild.me.permissions_in(channel).manage_webhooks:
                webhooks = await channel.webhooks()
                webhook = get(webhooks, name='فاذكروني')
                if not webhook:
                    webhook = await channel.create_webhook(
                        name="فاذكروني",
                        avatar=await client.user.avatar_url.read(),
                        reason=client.footer
                    )
                await webhook.send("> " + z["msg"])
                continue
            await channel.send("> " + z["msg"])
        except:
            continue


class Loop(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def start(self):
        print('`events has been ready`')

        self._send_30m.start()
        self._send_1h.start()
        self._send_2h.start()
        self._send_6h.start()
        self._send_12h.start()
        self._send_24h.start()

    @tasks.loop(minutes=30)
    async def _send_30m(self):
        await send(self.bot, 1800)

    @tasks.loop(hours=1)
    async def _send_1h(self):
        await send(self.bot, 3600)

    @tasks.loop(hours=2)
    async def _send_2h(self):
        await send(self.bot, 7200)

    @tasks.loop(hours=6)
    async def _send_6h(self):
        await send(self.bot, 21600)

    @tasks.loop(hours=12)
    async def _send_12h(self):
        await send(self.bot, 43200)

    @tasks.loop(hours=24)
    async def _send_24h(self):
        await send(self.bot, 86400)


def setup(bot):
    bot.add_cog(Loop(bot))
