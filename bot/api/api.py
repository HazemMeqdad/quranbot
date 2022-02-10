from hikari import ChannelType
from flask import Flask, request, jsonify
import logging
from lightbulb import BotApp
from threading import Thread
from waitress import serve


logger = logging.getLogger("bot.api")


class Api:
    def __init__(self, bot: BotApp) -> None:
        self.app = Flask(__name__)  # type: Flask
        self.bot = bot

    def index(self):
        return jsonify({"status": "ok"})

    def guilds_count(self):
        return jsonify({"count": len(self.bot.cache.get_available_guilds_view().values())})

    def shards_count(self):
        return jsonify({"count": self.bot.shard_count})

    def channels_count(self):
        return jsonify({"count": len(self.bot.cache.get_guild_channels_view().values())})

    def users_count(self):
        return jsonify({"count": len(self.bot.cache.get_users_view().values())})

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

    def run_as_thread(self):
        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/guilds_count", "guilds_count", self.guilds_count)
        self.app.add_url_rule("/shards_count", "shards_count", self.shards_count) 
        self.app.add_url_rule("/channels_count", "channels_count", self.channels_count)
        self.app.add_url_rule("/users_count", "users_count", self.users_count)
        self.app.add_url_rule("/get_guild/<int:guild_id>", "get_guild", self.get_guild)
        self.app.add_url_rule("/get_guild/<int:guild_id>/channels", "get_guild_channels", self.get_guild_channels)
        self.app.add_url_rule("/get_guild/<int:guild_id>/info", "get_info_from_db", self.get_info_from_db)
        self.app.add_url_rule("/get_guild/<int:guild_id>/roles", "get_guild_roles", self.get_guild_roles)

        run = lambda : serve(self.app, host="127.0.0.1", port=8080)
        keep_alive = lambda : Thread(target=run).start()
        keep_alive()
