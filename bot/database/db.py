import time 
from typing import Any
from .objects import Guild, Azkar, GuildUpdateType
import random
from pymongo.database import Database
import typing as t
from datetime import datetime

class DB:
    def __init__(self, db_client: Database) -> None:
        self.client: Database = db_client
        self.col_guilds = db_client.get_collection("guilds")
        self.col_azkar = db_client.get_collection("azkar")

    def speed_test(self):
        time_start = time.monotonic()
        self.col_guilds.find({})
        time_end = time.monotonic()
        return round((time_end - time_start) * 1000)
    
    def get_random_zker(self) -> Azkar:
        data = self.col_azkar.find({})
        return Azkar(random.choice(list(data)))

    def fetch_guild(self, guild_id: int) -> t.Optional[Guild]:
        result = self.col_guilds.find_one({"_id": guild_id})
        if not result:
            self.insert(guild_id)
        result = self.col_guilds.find_one({"_id": guild_id})
        return Guild(**result) if result else None

    def fetch_guilds_by_time(self, time: int) -> t.List[Guild]:
        data = self.col_guilds.find({"time": time})
        return [Guild(**i) for i in list(data)]

    def update_guild(self, guild: Guild, update_type: GuildUpdateType, new_value: Any):
        self.col_guilds.update_one({"_id": guild.id}, {"$set": {update_type.value: new_value}})
    
    def delete_guild(self, guild_id: int):
        self.col_guilds.delete_one({"_id": guild_id})

    def fetch_guilds_with_datetime(self) -> t.List[Guild]:
        now = datetime.now()
        data = self.col_guilds.find({"next_zker": {"$lt": now}})
        return [Guild(**i) for i in list(data)]

    def insert(self, guild_id: int):
        data = {
            "_id": guild_id,
            "channel_id": None,
            "time": 3600,
            "embed": False,
            "role_id": None,
            "webhook": None,
            "next_zker": datetime.now()
        }

        self.col_guilds.insert_one(data)
        return data
