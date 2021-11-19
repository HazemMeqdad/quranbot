from __future__ import annotations
from typing import Any

import hikari
from .objects import Guild, Azkar, GuildUpdateType
import random
from pymongo.database import Database


class DB:
    def __init__(self, db_client: Database) -> None:
        self.client: Database = db_client
        self.col_guilds = db_client.get_collection("guilds")
        self.col_azkar = db_client.get_collection("azkar")
        self.guilds: list[dict] = self.col_guilds.find({})
        self.azkar: list[dict] = self.col_azkar.find({})
        self._create_cache()

    def speed_test(self):
        return self.client.command("ping").get("ok")

    def _create_cache(self):
        self._guilds: dict = {}
        self._azkar: list[Azkar] = []
        for guild in self.guilds:
            self._guilds[guild.get("_id")] = Guild(guild)
        for zker in self.azkar:
            self._azkar.append(Azkar(zker))
    
    def get_random_zker(self) -> Azkar:
        return random.choice(self._azkar)

    def clear(self) -> None:
        self._guilds.clear()
        self._azkar.clear()
        self._create_cache()

    def get_guild(self, guild_id: int) -> Guild | None:
        return self._guilds.get(guild_id)

    def get_guilds(self) -> list[Guild]:
        return [Guild(i) for i in self._guilds.items()]
    
    def get_all_channels(self) -> list[object]:
        return [guild for guild in self.get_guilds()]

    def get_all_channels_by_time(self, bot, time: int) -> list[Guild]:
        return [Guild(i) for i in self.col_guilds.find({"time": time}) if i.get("channel")]

    def fetch_guild(self, guild_id: int) -> Guild | None:
        result = self.col_guilds.find_one({"_id": guild_id})
        return Guild(result) if result else None

    def update_guild(self, guild: Guild, update_type: GuildUpdateType, new_value: Any):
        self.col_guilds.update_one({"_id": guild.id}, {"$set": {update_type.value: new_value}})
        self._guilds[guild.id] = self.fetch_guild(guild.id)
    
    def insert(self, guild_id: int):
        if not self.get_guild(guild_id) and not self.fetch_guild(guild_id):
            data = {
                "_id": guild_id,
                "prefix": "!",
                "channel": None,
                "time": 1800,
                "anti_spam": False,
                "embed": False
            }

            self.col_guilds.insert_one(data)
            self._guilds[guild_id] = Guild(data)
