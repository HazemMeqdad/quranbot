import discord
import lavalink
from discord.ext import commands
from discord import app_commands
import aiohttp
import typing as t
from utlits import BaseView
from utlits.voice_client import LavalinkVoiceClient
from utlits import get_quran_embed
from discord.ui import View
import json

cdn_radio_cache = []

class VoiceView(BaseView):
    def __init__(self, player: lavalink.DefaultPlayer = None, user_id: int = None, reader: str = None, disabled: bool = False, message: t.Optional[discord.Message] = None):
        super().__init__(timeout=None)
        self.player = player
        self.user_id = user_id
        self.message = None
        self.postion = 1
        self.reader = reader
        self.message = message
        if disabled:
            for index, item in enumerate(self.children):
                if isinstance(item, discord.ui.TextInput) or (isinstance(item, discord.ui.Button) and item.style == discord.ButtonStyle.link):
                    continue
                self.children[index].disabled = True
    
    def set_postion(self, postion: int):
        self.postion = postion
    
    @discord.ui.button(label="⏯️", style=discord.ButtonStyle.grey, custom_id="voice:pause")
    async def pause(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.paused:
            await self.player.set_pause(False)
            await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))
        else:
            await self.player.set_pause(True)
            await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))

    @discord.ui.button(label="⏹️", style=discord.ButtonStyle.red, custom_id="voice:stop")
    async def stop(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        self.player.queue.clear()
        if self.player.is_playing:
            await self.player.stop()
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect(force=True)
        for index, item in enumerate(self.children):
            if isinstance(item, discord.ui.TextInput) or (isinstance(item, discord.ui.Button) and item.style == discord.ButtonStyle.link):
                continue
            self.children[index].disabled = True
        embed = interaction.message.embeds[0]
        state_field = list(filter(lambda x: x.name == "الحالة:", embed.fields))[0]
        embed.set_field_at(embed.fields.index(state_field), name="الحالة:", value="متوقف")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⏭️", style=discord.ButtonStyle.grey, custom_id="voice:next")
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.is_playing:
            await self.player.skip()
        if len(self.player.queue) == 0:
            return await interaction.response.edit_message()
        
        await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))
    
    @discord.ui.button(label="🔉", style=discord.ButtonStyle.grey, custom_id="voice:volume:down")
    async def down_volume(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.is_playing:
            await self.player.set_volume(self.player.volume - 10)
            await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))

    @discord.ui.button(label="🔊", style=discord.ButtonStyle.grey, custom_id="voice:volume:up")
    async def up_volume(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.is_playing and self.player.volume < 100:
            await self.player.set_volume(self.player.volume + 10)
        await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))

    @discord.ui.button(label="🔂", style=discord.ButtonStyle.grey, custom_id="voice:repeat:surah")
    async def repeat(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.is_playing:
            if self.player.loop == 1:
                self.player.set_loop(0)
            else:
                self.player.set_loop(1)
        await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))

    @discord.ui.button(label="🔁", style=discord.ButtonStyle.grey, custom_id="voice:repaet:all")
    async def repeat_all(self, interaction: discord.Interaction, button: discord.Button):
        if not self.player or not self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("لا يمكنك أستخدام هذه القائمة", ephemeral=True)
        if self.player.is_playing:
            if self.player.loop == 2:
                self.player.set_loop(0)
            else:
                self.player.set_loop(2)
        await interaction.response.edit_message(embed=get_quran_embed(self.player, reader=self.reader, user_id=self.user_id))   


@app_commands.guild_only()
class Player(commands.GroupCog, name="quran"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.lavalink: lavalink.Client = self.bot.lavalink
        self.control_panels: t.Dict[int, t.List[discord.Message]] = {}

    def cog_unload(self) -> None:
        self.lavalink._event_hooks.clear()

    def cog_load(self) -> None:
        self.lavalink.add_event_hook(self.track_hook)

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
                raise commands.CommandInvokeError("يجب عليك أن تكون في الروم الصوت الذي يوجد به البوت")

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
            messages = self.control_panels.get(guild_id, [])
            for message in messages:
                if message is None:
                    continue
                view = View.from_message(message)
                for index, item in enumerate(view.children):
                    item.disabled = True
                await message.edit(view=view)

    async def reader_autocomplete(self, interaction: discord.Interaction, current: t.Optional[str] = None) -> t.List[app_commands.Choice]:
        """Autocomplete for reader selection."""

        with open("json/cdn_surah_audio.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if not current:
            return [app_commands.Choice(name=i["name"], value=i["identifier"]) for i in data][:25]
        return [app_commands.Choice(name=i["name"], value=i["identifier"]) for i in data if current in i["name"]][:25]

    async def surah_autocomplete(self, interaction: discord.Interaction, current: t.Optional[str] = None) -> t.List[app_commands.Choice]:
        with open("json/surahs.json", "r", encoding="utf-8") as f:
            surahs = json.load(f)
        if not current:
            return [app_commands.Choice(name=i, value=c+1) for c, i in enumerate(surahs)][:25]
        return [app_commands.Choice(name=i, value=c+1) for c, i in enumerate(surahs) if current in i][:25]

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
        with open("json/cdn_surah_audio.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        reader_name = [i for i in data if i["identifier"] == quran_reader][0]["name"]
        view = VoiceView(player, interaction.user.id, reader_name)
        if surah is not None:
            if surah > 114:
                return await interaction.response.send_message("السورة غير موجودة يرجى التأكد من أختبار احد الخيارت المتاحة", ephemeral=True)
            results = await self.lavalink.get_tracks(f"https://cdn.islamic.network/quran/audio-surah/128/{quran_reader}/{surah}.mp3")
            player.add(results.tracks[0])
            if not player.is_playing:
                await player.play()
            embed = get_quran_embed(player, reader=reader_name, user_id=interaction.user.id)
            await interaction.response.send_message(
                embed=embed,
                view=view
            )
            view.message = await interaction.original_response()
            if not self.control_panels.get(interaction.guild.id):
                self.control_panels[interaction.guild.id] = []
            self.control_panels[interaction.guild.id].append(await interaction.original_response())
            return
        urls = [f"https://cdn.islamic.network/quran/audio-surah/128/{quran_reader}/{i}.mp3" for i in range(1, 115)]
        track = (await self.lavalink.get_tracks(urls[0])).tracks[0]
        embed = get_quran_embed(player, track, reader=reader_name, user_id=interaction.user.id)
        
        await interaction.response.send_message(
            embed=embed, 
            view=view
        )
        view.message = await interaction.original_response()
        if not self.control_panels.get(interaction.guild.id):
                self.control_panels[interaction.guild.id] = []
        self.control_panels[interaction.guild.id].append(await interaction.original_response())
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
        if not quran_reader.lower().startswith("https://backup.qurango.net/radio/"):
            return await interaction.response.send_message("يرجى التأكد من أختيار قارئ من القائمة فقط")
        reader_name = [i for i in cdn_radio_cache if i["URL"] == quran_reader][0]["name"]
        results = await self.lavalink.get_tracks(quran_reader)
        player.add(results.tracks[0])
        if not player.is_playing:
            await player.play()
        embed = get_quran_embed(player, reader=reader_name, user_id=interaction.user.id)
        view = VoiceView(player, interaction.user.id, reader_name)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
        if not self.control_panels.get(interaction.guild.id):
                self.control_panels[interaction.guild.id] = []
        self.control_panels[interaction.guild.id].append(view.message)

    @app_commands.command(name="stop", description="إيقاف تشغيل القرآن الكريم.")
    async def quran_stop(self, interaction: discord.Interaction):
        await self.ensure_connected(interaction)
        player = self.lavalink.player_manager.get(interaction.guild.id)
        player.queue.clear()
        if player.is_playing:
            await player.stop()
        await interaction.guild.voice_client.disconnect(force=True)
        await interaction.response.send_message("تم إيقاف تشغيل القرآن الكريم")

    @app_commands.command(name="control", description="عرض تفاصيل القرآن الكريم المشغل حاليا")
    async def quran_info_command(self, interaction: discord.Interaction):
        player = self.lavalink.player_manager.get(interaction.guild.id)
        if not player or not player.is_playing:
            return await interaction.response.send_message("لا يوجد أي قرآن مشغل حاليا", ephemeral=True)
        embed = get_quran_embed(player, user_id=interaction.user.id)
        view = VoiceView(player, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
        if not self.control_panels.get(interaction.guild.id):
                self.control_panels[interaction.guild.id] = []
        self.control_panels[interaction.guild.id].append(view.message)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Player(bot))

