from flask import Flask, request, jsonify
import logging
from lightbulb import BotApp, SlashCommandGroup
from threading import Thread
from waitress import serve
import typing

from bot.database.objects import GuildUpdateType


logger = logging.getLogger("bot.api")


class Api:
    def __init__(self, bot: BotApp) -> None:
        self.app = Flask(__name__)  # type: Flask
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

    def get_guild(self, guild_id: int):
        guild = self.bot.cache.get_available_guild(int(guild_id))
        return jsonify({"status": True if guild else False})

    def get_guild_channels(self, guild_id: int):
        channels = self.bot.cache.get_guild_channels_view_for_guild(int(guild_id))
        return jsonify({"channels": [{"id": channel.id, "name": channel.name, "type": channel.type.value} for channel in channels.values()]})

    def get_guild_roles(self, guild_id: int):
        roles = self.bot.cache.get_roles_view_for_guild(int(guild_id))
        return jsonify({"roles": [{"id": role.id, "name": role.name} for role in roles.values()]})

    def get_info_from_db(self, guild_id: int):
        guild = self.bot.db.fetch_guild(guild_id)
        if not guild:
            data = self.bot.db.insert(guild_id)
        return jsonify({"guild": guild._data if guild else data})

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

    # database methods
    def update_channel(self, guild_id: int):
        channel_id = request.json.get("channel_id")
        self.bot.db.update_guild(self.bot.db.fetch_guild(guild_id), GuildUpdateType.channel, channel_id)
        return jsonify({"channel_id": channel_id})

    def quran_channel(self, guild_id: int):
        # new_prefix = request.form.get("channel")
        # guild = self.bot.db.fetch_guild(guild_id)
        # self.bot.db.update_prefix(guild, GuildUpdateType., new_prefix)
        return jsonify({"status": True})
        
    def update_role(self, guild_id: int):
        role_id = request.form.get("role_id")
        self.bot.db.update_guild(guild_id, GuildUpdateType.role_id, role_id)
        return jsonify({"role_id": role_id})

    def update_time(self, guild_id: int):
        time = request.form.get("time")
        self.bot.db.update_guild(guild_id, GuildUpdateType.time, time)
        return jsonify({"time": time})
    
    def update_color(self, guild_id: int):
        # color = request.form.get("color")
        # self.bot.db.update_guild(guild_id, GuildUpdateType.color, color)
        return jsonify({"status": True})

    def update_anti_spam(self, guild_id: int):
        stats = request.form.get("anti_spam")
        self.bot.db.update_guild(guild_id, GuildUpdateType.anti_spam, stats)
        return jsonify({"status": stats})
    
    def update_embed(self, guild_id: int):
        stats = request.form.get("embed")
        self.bot.db.update_guild(guild_id, GuildUpdateType.embed, stats)
        return jsonify({"status": stats})    

    def run_as_thread(self):
        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/ping", "ping", self.index)

        self.app.add_url_rule("/bot_info", "bot_info", self.bot_info)

        self.app.add_url_rule("/get_guild/<int:guild_id>", "get_guild", self.get_guild)
        self.app.add_url_rule("/get_guild/<int:guild_id>/channels", "get_guild_channels", self.get_guild_channels)
        self.app.add_url_rule("/get_guild/<int:guild_id>/info", "get_info_from_db", self.get_info_from_db)
        self.app.add_url_rule("/get_guild/<int:guild_id>/roles", "get_guild_roles", self.get_guild_roles)
        self.app.add_url_rule("/commands", "commands", self.commands)

        # database methods
        self.app.add_url_rule("/update_channel/<int:guild_id>", "update_channel", self.update_channel, methods=["POST"])
        self.app.add_url_rule("/quran_channel/<int:guild_id>", "quran_channel", self.quran_channel, methods=["POST"])
        self.app.add_url_rule("/update_role/<int:guild_id>", "update_role", self.update_role, methods=["POST"])
        self.app.add_url_rule("/update_time/<int:guild_id>", "update_time", self.update_time, methods=["POST"])
        self.app.add_url_rule("/update_color/<int:guild_id>", "update_color", self.update_color, methods=["POST"])
        self.app.add_url_rule("/update_anti_spam/<int:guild_id>", "update_anti_spam", self.update_anti_spam, methods=["POST"])
        self.app.add_url_rule("/update_embed/<int:guild_id>", "update_embed", self.update_embed, methods=["POST"])

        run = lambda : serve(self.app, host="127.0.0.1", port=8080)
        keep_alive = lambda : Thread(target=run).start()
        keep_alive()
