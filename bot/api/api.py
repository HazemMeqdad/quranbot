from flask import Flask, request, jsonify
import logging
from lightbulb import BotApp, SlashCommandGroup
from threading import Thread
from waitress import serve
import typing
from flask_cors import CORS
from bot.database.objects import GuildUpdateType


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
            "users": len(self.bot.cache.get_users_view().values())
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
            "channels": [{"id": channel.id, "name": channel.name, "type": channel.type.value} for channel in channels.values()],
            "roles": [{"id": role.id, "name": role.name} for role in roles.values()]
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

        run = lambda : serve(self.app, host="127.0.0.1", port=8080)
        keep_alive = lambda : Thread(target=run).start()
        keep_alive()
