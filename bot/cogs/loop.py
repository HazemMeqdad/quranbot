import discord
from discord.ext import commands, tasks
from bot import db
from requests import request


class Loop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._send_30m.start()
        self._send_1h.start()
        self._send_2h.start()
        self._send_6h.start()
        self._send_12h.start()
        self._send_24h.start()

    def unload(self):
        self._send_30m.cancel()
        self._send_1h.cancel()
        self._send_2h.cancel()
        self._send_6h.cancel()
        self._send_12h.cancel()
        self._send_24h.cancel()

    async def send(self, time: int):
        for i in db.get_all_channels_by_time(time):
            guild = self.bot.get_guild(i["_id"])
            if not guild:
                continue
            x = db.Guild(guild)
            channel = guild.get_channel(x.info.get("channel"))
            if guild.me.guild_permissions.manage_webhooks is False or not channel:
                continue
            try:
                webhooks = await channel.webhooks()
            except:
                continue
            webhook = discord.utils.get(webhooks, name='فاذكروني')
            if x.info.get("anti_spam"):
                if not webhook:
                    pass
                else:
                    try:
                        message = await channel.fetch_message(channel.last_message_id)
                        if message.author.id == webhook.id:
                            continue
                    except:
                        pass
            try:
                z = db.Azkar().random
                if not webhook:
                    webhook = await channel.create_webhook(
                        name="فاذكروني",
                        avatar=await self.bot.user.avatar.read(),
                        reason=self.bot.footer
                    )
                if x.info.get("embed"):
                    embed = discord.Embed(
                        title=str(z["_id"]),
                        description="> " + z["msg"],
                        color=0xffd430
                    )
                    embed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar.url)
                    embed.set_thumbnail(url=self.bot.user.avatar.url)
                    request(
                        method="POST",
                        url=webhook.url,
                        json={
                            "username": self.bot.user.name,
                            "avatar_url": self.bot.user.avatar.url,
                            "embeds": [embed.to_dict()]
                        }
                    )
                    continue
                request(
                    method="POST",
                    url=webhook.url,
                    json={
                        "username": self.bot.user.name,
                        "avatar_url": self.bot.user.avatar.url,
                        "content": "> " + z["msg"]
                    }
                )
                continue
            except:
                continue

    @tasks.loop(minutes=30)
    async def _send_30m(self):
        await self.send(1800)

    @tasks.loop(hours=1)
    async def _send_1h(self):
        await self.send(3600)

    @tasks.loop(hours=2)
    async def _send_2h(self):
        await self.send(7200)

    @tasks.loop(hours=6)
    async def _send_6h(self):
        await self.send(21600)

    @tasks.loop(hours=12)
    async def _send_12h(self):
        await self.send(43200)

    @tasks.loop(hours=24)
    async def _send_24h(self):
        await self.send(86400)

    @_send_30m.before_loop
    async def before_send_30m(self):
        await self.bot.wait_until_ready()

    @_send_1h.before_loop
    async def before_send_1h(self):
        await self.bot.wait_until_ready()

    @_send_2h.before_loop
    async def before__send_2h(self):
        await self.bot.wait_until_ready()

    @_send_6h.before_loop
    async def before_send_6h(self):
        await self.bot.wait_until_ready()

    @_send_12h.before_loop
    async def before_send_12h(self):
        await self.bot.wait_until_ready()

    @_send_24h.before_loop
    async def before_send_24h(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Loop(bot))
