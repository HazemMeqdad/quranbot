from __future__ import annotations
import typing
from enum import Enum
from pymongo import MongoClient
import hikari
from datetime import datetime
from random import choice

mongo_url = open("./bot/config/mongo_url.txt", "r").read()

db = MongoClient(mongo_url)
db_client = db["fa-azcrone"]
col_guilds = db_client["guilds"]
col_blacklist_user = db_client["blacklist_users"]
col_blacklist_guild = db_client["blacklist_guilds"]
col_azkar = db_client["azker"]
col_shards = db_client["shards"]

print('`connect MongoDB database`')


def speedtest() -> int:
    start = datetime.now().timestamp()
    test_connection = MongoClient(mongo_url)
    test_connection.close()
    end = datetime.now().timestamp()
    return round((end - start) * 1000)


def get_all_channels():
    return col_guilds.find()


def get_all_channels_by_time(time: int) -> list[dict]:
    return [i for i in col_guilds.find({"time": time}) if i.get("channel")]


class GuildUpdateType(Enum):
    prefix = "prefix"
    channel = "channel"
    time = "time"
    anti_spam = "anti_spam"
    embed = "embed"


class Guild(object):
    def __init__(self, guild_id: typing.Union[hikari.Snowflake]):
        self._guild_id = int(guild_id)

    @property
    def info(self) -> dict:
        return col_guilds.find_one({"_id": self._guild_id})

    async def update_where(self, module: GuildUpdateType, value) -> dict:
        col_guilds.update_one({"_id": self._guild_id}, {"$set": {module.value: value}})
        return self.info

    async def insert(self) -> dict:
        if self.info:
            return {"msg": "This guild already exists"}
        data = {
            "_id": self._guild_id,
            "prefix": "!",
            "channel": None,
            "time": 3600,
            "anti_spam": False,
            "embed": False
        }
        col_guilds.insert_one(data)
        return self.info


class BlackListUser(object):
    def __init__(self, user: hikari.User):
        self._user = user

    def insert(self, mod_id: int, reason=None) -> dict:
        if self.info:
            return {"msg": "This user already exists"}
        data = {
            "_id": self._user.id,
            "mod_id": mod_id,
            "reason": reason,
            "timestamp": datetime.now().timestamp()
        }
        col_blacklist_user.insert(data)
        return self.info

    def delete(self):
        col_blacklist_user.delete_one({"_id": self._user.id})

    @property
    def info(self) -> dict:
        return col_blacklist_user.find_one({"_id": self._user.id})

    @property
    def check(self) -> bool:
        if not self.info:
            return True
        return False


class BlackListGuild(object):
    def __init__(self, user: hikari.User):
        self._user = user

    def insert(self, mod_id: int, reason=None) -> dict:
        if self.info:
            return {"msg": "This user already exists"}
        data = {
            "_id": self._user.id,
            "mod_id": mod_id,
            "reason": reason,
            "timestamp": datetime.now().timestamp()
        }
        col_blacklist_guild.insert(data)
        return self.info

    def delete(self):
        col_blacklist_guild.delete_one({"_id": self._user.id})

    @property
    def info(self) -> dict:
        return col_blacklist_guild.find_one({"_id": self._user.id})

    @property
    def check(self) -> bool:
        if not self.info:
            return True
        return False


class Azkar(object):
    @property
    def last_id(self) -> int:
        try:
            return col_azkar.find().sort("_id", -1).limit(1)[0].get("_id") + 1
        except:
            return 1

    def add(self, msg: str):
        col_azkar.insert_one({"_id": self.last_id, "msg": msg})

    @staticmethod
    def remove(_id: int):
        col_azkar.delete_one({"_id": _id})

    @staticmethod
    def edit(_id: int, new_msg: str):
        col_azkar.update_one({"_id": _id}, {"$set": {"msg": new_msg}})

    @property
    def random(self) -> dict:
        return choice([i for i in col_azkar.find()])


class Shards(object):
    def __init__(self, shard_id, **kwargs):
        self.shard_id = shard_id
        self.data = kwargs

    def insert(self):
        if self.info:
            return
        json = {
            "_id": self.shard_id,
            **self.data
        }
        col_shards.insert_one(json)

    @property
    def info(self):
        return col_shards.find_one({"_id": self.shard_id})

    def update(self):
        if not self.info:
            self.insert()
        col_shards.update_one({"_id": self.shard_id}, {"$set": {**self.data}})
