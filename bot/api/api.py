from flask import Flask, request, jsonify
import logging
from lightbulb import BotApp, SlashCommandGroup
from threading import Thread
from waitress import serve
import typing
from flask_cors import CORS
from bot.database.objects import GuildUpdateType
import asyncio 


logger = logging.getLogger("bot.api")


class Api:
    def __init__(self, bot: BotApp) -> None:
        self.app = Flask(__name__)  # type: Flask
        CORS(self.app)
        self.bot = bot

    def index(self):
        return jsonify({"status": "ok"})

    def bot_info(self):
        return jsonify({
            "shards": self.bot.shard_count,
            "guilds": len(self.bot.cache.get_available_guilds_view().values()),
            "channels": len(self.bot.cache.get_guild_channels_view().values()),
        })

    def check(self, guild_id: int):
        guild = self.bot.cache.get_guild(guild_id)
        return jsonify({"check": True if guild else False})

    def guilds_check(self):
        data = request.json
        cache_guilds = [i.id for i in self.bot.cache.get_available_guilds_view().values()]
        guilds = [i for i in data["guilds"] if i in cache_guilds]
        return jsonify({"guilds": guilds})

    def get_guild(self, guild_id: int):
        channels = self.bot.cache.get_guild_channels_view_for_guild(guild_id)
        roles = self.bot.cache.get_roles_view_for_guild(guild_id)
        return jsonify({
            "channels": [{"id": channel.id.__str__(), "name": channel.name, "type": channel.type.value} for channel in channels.values()],
            "roles": [{"id": role.id.__str__(), "name": role.name} for role in roles.values()]
        })

    def get_guild_info(self, guild_id: int):
        guild = self.bot.cache.get_guild(guild_id)
        # if guild:
        #     owner = await guild.fetch_owner()
        return jsonify({
            "status": True if guild else False,
            "guild": {
                "id": str(guild.id),
                "name": guild.name,
                "icon": guild.icon_url.url if guild.icon_url else f"https://via.placeholder.com/1024/2c2f33/ffffff?text={guild.name[0]}",
                "owner_id": str(guild.owner_id),
                # "owner": owner.username + "#" + owner.discriminator,
                # "owner_id": owner.id,
                "joined_at": guild.joined_at.timestamp(),
                "member_count": guild.member_count,
                "channels": len(guild.get_channels()),
                "emojis": len(guild.get_emojis()),
                "features": guild.features,
                "banner": guild.banner_url.url if guild.banner_url else None,
                "description": guild.description,
            } if guild else None
        })

    def commands(self):
        commands = self.bot._slash_commands
        fields: typing.List[typing.Dict] = []
        for name, command in commands.items():
            if isinstance(command, SlashCommandGroup):
                for com_name, com in command.subcommands.items():
                    fields.append({"name": f"/{name} {com_name}", "description": com.description})
                continue
            if command.hidden:
                continue
            fields.append({"name": f"/{name}", "description": command.description})
        return jsonify({"commands": fields})

    def run_as_thread(self):
        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/ping", "ping", self.index)

        self.app.add_url_rule("/info", "bot_info", self.bot_info)

        self.app.add_url_rule("/guild/<int:guild_id>", "get_guild", self.get_guild)
        self.app.add_url_rule("/guild/<int:guild_id>/check", "check", self.check)
        self.app.add_url_rule("/guilds/check", "guilds_check", self.guilds_check)
        self.app.add_url_rule("/commands", "commands", self.commands)
        self.app.add_url_rule("/guild/<int:guild_id>/info", "get_guild_info", self.get_guild_info)
        run = lambda : serve(self.app, host="0.0.0.0", port=8080)
        keep_alive = lambda : Thread(target=run).start()
        keep_alive()
