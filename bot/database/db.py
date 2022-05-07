import time 
from typing import Any
from .objects import Guild, Azkar, GuildUpdateType
import random
from pymongo.database import Database
import typing as t
import threading

class DB:
    def __init__(self, db_client: Database) -> None:
        self.client: Database = db_client
        self.col_guilds = db_client.get_collection("guilds")
        self.col_azkar = db_client.get_collection("azkar")
        self.guilds: list[dict] = self.col_guilds.find({})
        self.azkar: list[dict] = self.col_azkar.find({})
        threading.Thread(target=self._create_cache).start()

    def speed_test(self):
        time_start = time.monotonic()
        self.col_guilds.find({})
        time_end = time.monotonic()
        return round((time_end - time_start) * 1000)

    def _create_cache(self):
        self._guilds: dict = {}
        self._azkar: list[Azkar] = []
        for guild in self.guilds:
            self._guilds[guild.get("_id")] = Guild(**guild)
        for zker in self.azkar:
            self._azkar.append(Azkar(zker))
    
    def get_random_zker(self) -> Azkar:
        return random.choice(self._azkar)

    def clear(self) -> None:
        self._guilds.clear()
        self._azkar.clear()
        self._create_cache()

    def get_guild(self, guild_id: int) -> t.Optional[Guild]:
        return self._guilds.get(guild_id)

    def get_guilds(self) -> t.List[Guild]:
        return [Guild(**i) for i in self._guilds.items()]
    
    def get_all_channels(self) -> t.List[object]:
        return [guild for guild in self.get_guilds()]

    def fetch_guild(self, guild_id: int) -> t.Optional[Guild]:
        result = self.col_guilds.find_one({"_id": guild_id})
        return Guild(**result) if result else None

    def fetch_guilds_by_time(self, time: int) -> t.List[Guild]:
        return [Guild(**i) for i in self.col_guilds.find({"time": time})]

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
                "embed": False,
                "role_id": None
            }

            self.col_guilds.insert_one(data)
            self._guilds[guild_id] = Guild(**data)
            return self._guilds[guild_id]
