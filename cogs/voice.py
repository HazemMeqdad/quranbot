import discord
import lavalink
import os
from discord.ext import commands
from discord import app_commands
import aiohttp
import typing as t

from cogs.utlits.views import DownloadSurahView
from .utlits.voice_client import LavalinkVoiceClient

surahs_cache = []
cdn_surah_audio_cache = []
cdn_radio_cache = []


class Player(commands.GroupCog, name="quran"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.lavalink: lavalink.Client = self.bot.lavalink
        self.lavalink.add_event_hook(self.track_hook)

    def cog_unload(self) -> None:
        self.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        """ Command before-invoke handler. """
        guild_check = ctx.guild is not None
        #  This is essentially the same as `@commands.guild_only()`
        #  except it saves us repeating ourselves (and also a few lines).

        if guild_check:
            await self.ensure_voice(ctx)
            #  Ensure that the bot and command author share a mutual voicechannel.

        return guild_check

    async def ensure_voice(self, interaction: discord.Interaction) -> None:
        """ This check ensures that the bot and command author are in the same voicechannel. """
        player = self.bot.lavalink.player_manager.create(interaction.guild.id)
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        if not interaction.user.voice or not interaction.user.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            raise commands.CommandInvokeError('يجب عليك دخول روم صوتية لأستعمال هذا الأمر')

        v_client = interaction.guild.voice_client
        if not v_client:


            permissions = interaction.user.voice.channel.permissions_for(interaction.guild.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                raise commands.CommandInvokeError('البوت لا يمتلك صلاحيات:\n`CONNECT`\n`SPEAK`')

            player.store('channel', interaction.channel.id)
            await interaction.user.voice.channel.connect(cls=LavalinkVoiceClient, self_deaf=True)
        else:
            if v_client.channel.id != interaction.user.voice.channel.id:
                raise commands.CommandInvokeError("يجب عليك أن تكون الروم الصوت الذي يوجد به البوت")

    async def ensure_connected(self, interaction: discord.Interaction) -> None:
        """ This check ensures that the bot is in a voicechannel. """
        player = self.bot.lavalink.player_manager.get(interaction.guild.id)
        if not interaction.guild.voice_client:
            raise commands.CommandInvokeError('البوت غير متصل بروم صوتي')

        if not interaction.user.voice or (player.is_connected and interaction.user.voice.channel.id != int(player.channel_id)):
            raise commands.CommandInvokeError("يجب عليك ان تدخل الروم الصوتي الخاص بالبوت <#%d>!" % player.channel_id)

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = event.player.guild_id
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)

    async def reader_autocomplete(self, interaction: discord.Interaction, current: t.Optional[str] = None) -> t.List[app_commands.Choice]:
        """Autocomplete for reader selection."""
        global cdn_surah_audio_cache
        if not cdn_surah_audio_cache:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://cdn.fdrbot.com/reciters/cdn_surah_audio.json") as resp:
                    cdn_surah_audio_cache = await resp.json()
        data = cdn_surah_audio_cache
        if not current:
            return [app_commands.Choice(name=i["name"], value=i["identifier"]) for i in data][:25]
        return [app_commands.Choice(name=i["name"], value=i["identifier"]) for i in data if current in i["reciter"]][:25]

    async def surah_autocomplete(self, interaction: discord.Interaction, current: t.Optional[str] = None) -> t.List[app_commands.Choice]:
        global surahs_cache
        if not surahs_cache:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://cdn.fdrbot.com/reciters/surah.json") as resp:
                    surahs_cache = await resp.json()
        if not current:
            return [app_commands.Choice(name=i["titleAr"], value=c+1) for c, i in enumerate(surahs_cache)][:25]
        return [app_commands.Choice(name=i["titleAr"], value=c+1) for c, i in enumerate(surahs_cache) if current in i["titleAr"]][:25]

    @app_commands.command(name="play", description="تشغيل القرآن الكريم بالصوت")
    @app_commands.autocomplete(quran_reader=reader_autocomplete, surah=surah_autocomplete)
    @app_commands.describe(
        quran_reader="أختر القارئ",
        surah="أختر السورة",
    )
    async def quran_play(self, interaction: discord.Interaction, quran_reader: str, surah: t.Optional[int] = None):
        await self.ensure_voice(interaction)
        player = self.lavalink.player_manager.get(interaction.guild.id)
        if len(player.queue) != 0:
            await interaction.response.send_message("يجب عليك إيقاف المشغل حاليا حتى تستطيع أستخدام الأمر", ephemeral=True)
            return
        reader_name = [i for i in cdn_surah_audio_cache if i["identifier"] == quran_reader][0]["name"]
        if surah is not None:
            if surah > 114:
                return await interaction.response.send_message("السورة غير موجودة يرجى التأكد من أختبار احد الخيارت المتاحة", ephemeral=True)
            surah_name = surahs_cache[surah-1]["titleAr"]
            results = await self.lavalink.get_tracks(f"https://cdn.islamic.network/quran/audio-surah/128/{quran_reader}/{surah}.mp3")
            player.add(results.tracks[0])
            if not player.is_playing:
                await player.play()
            await interaction.response.send_message(f"تم تشغيل سورة **{surah_name}** بوت الشيخ **{reader_name}**")
            return
        urls = [f"https://cdn.islamic.network/quran/audio-surah/128/{quran_reader}/{i}.mp3" for i in range(1, 115)]
        await interaction.response.send_message(f"تم تشغيل القرآن الكريم كامل بصوت الشيخ **{reader_name}**")
        for url in urls:
            results = await self.lavalink.get_tracks(url)
            if not results.tracks:
                continue
            player.add(results.tracks[0])
            if not player.is_playing:
                await player.play()

    async def radio_reader_autocomplete(self, interaction: discord.Interaction, current: t.Optional[str] = None) -> t.List[app_commands.Choice]:
        """Autocomplete for reader selection."""
        global cdn_radio_cache
        if not cdn_radio_cache:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.mp3quran.net/api_2/radios?language=ar") as resp:
                    cdn_radio_cache = (await resp.json())["reads"]
        data = cdn_radio_cache
        if not current:
            return [app_commands.Choice(name=i["name"], value=i["URL"]) for i in data][:25]
        return [app_commands.Choice(name=i["name"], value=i["URL"]) for i in data if current in i["name"]][:25]

    @app_commands.command(name="radio", description="تشغيل أذاعة القرآن الكريم 📻")
    @app_commands.autocomplete(quran_reader=radio_reader_autocomplete)
    async def quran_radio(self, interaction: discord.Interaction, quran_reader: str):
        await self.ensure_voice(interaction)
        player = self.lavalink.player_manager.get(interaction.guild.id)
        if len(player.queue) != 0:
            await interaction.response.send_message("يجب عليك إيقاف المشغل حاليا حتى تستطيع أستخدام الأمر", ephemeral=True)
            return
        if not quran_reader.lower().startswith("https://qurango.net/radio/"):
            return await interaction.response.send_message("يرجى التأكد من أختيار قارئ من القائمة فقط")
        reader_name = [i for i in cdn_radio_cache if i["URL"] == quran_reader][0]["name"]
        results = await self.lavalink.get_tracks(quran_reader)
        player.add(results.tracks[0])
        if not player.is_playing:
            await player.play()
        await interaction.response.send_message(f"تم تشغيل أذاعة القرآن الكريم بصوت الشيخ **{reader_name}**")

    @app_commands.command(name="stop", description="إيقاف تشغيل القرآن الكريم.")
    async def quran_stop(self, interaction: discord.Interaction):
        await self.ensure_connected(interaction)
        player = self.lavalink.player_manager.get(interaction.guild.id)
        player.queue.clear()
        if player.is_playing:
            await player.stop()
        await interaction.guild.voice_client.disconnect(force=True)
        await interaction.response.send_message("تم إيقاف تشغيل القرآن الكريم")

    @app_commands.command(name="pause", description="إيقاف مؤقت لتشغيل القرآن الكريم.")
    async def quran_pause(self, interaction: discord.Interaction):
        await self.ensure_connected(interaction)
        player = self.lavalink.player_manager.get(interaction.guild.id)
        if player.is_playing:
            await player.set_pause(True)
        await interaction.response.send_message("تم إيقاف القرآن الكريم بشكل مؤقت, يمكنك استخدام الأمر `quran resume` للمتابعة")
    
    @app_commands.command(name="resume", description="مواصلة تشغيل القرآن الكريم.")
    async def quran_resume(self, interaction: discord.Interaction):
        await self.ensure_connected(interaction)
        player = self.lavalink.player_manager.get(interaction.guild.id)
        if player.is_playing:
            await player.set_pause(False)
        await interaction.response.send_message("تم مواصلة تشغيل القرآن الكريم")

    @app_commands.command(name="volume", description="تغيير مستوى الصوت.")
    @commands.before_invoke(ensure_connected)
    async def quran_volume(self, interaction: discord.Interaction, volume: int):
        player = self.lavalink.player_manager.get(interaction.guild.id)
        if volume > 100:
            return await interaction.response.send_message("لا يمكن تغيير مستوى الصوت لأكثر من 100", ephemeral=True)
        await player.set_volume(volume)
        await interaction.response.send_message(f"تم تغيير مستوى الصوت إلى **{volume}**")

    @app_commands.command(name="details", description="عرض تفاصيل القرآن الكريم المشغل حاليا")
    async def quran_info_command(self, interaction: discord.Interaction):
        player = self.lavalink.player_manager.get(interaction.guild.id)
        if not player or not player.is_playing:
            return await interaction.response.send_message("لا يوجد أي قرآن مشغل حاليا", ephemeral=True)
        track = player.current
        embed = discord.Embed(
            title="القرآن الكريم",
            color=0xffd430
        )
        embed.add_field(name="القارئ:", value=track.author)
        embed.add_field(name="السورة:", value=track.title)
        embed.add_field(name="المستوى:", value=player.volume)
        embed.add_field(name="الحالة:", value="متوقف" if player.paused else "مشغل")
        if len(player.queue) > 1:
            embed.add_field(name="القادم:", value=f"{player.queue[1].title}")
            embed.add_field(name="عدد السور المتبقية بالقراءة:", value=f"{len(player.queue)}")
        await interaction.response.send_message(embed=embed, view=DownloadSurahView(track.uri))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Player(bot))

