from pymongo import MongoClient
from bot import config
from datetime import datetime
from discord import Guild as GuildObject
from discord import User as UserObject
from random import choice

db = MongoClient(config.mongo_url)
db_client = db["fa-azcrone"]
col_guilds = db_client["guilds"]
col_blacklist_user = db_client["blacklist_users"]
col_blacklist_guild = db_client["blacklist_guilds"]
col_azkar = db_client["azkar"]


print('`connect MongoDB database`')


def speedtest() -> int:
    start = datetime.now().timestamp()
    test_connection = MongoClient(config.mongo_url)
    test_connection.close()
    end = datetime.now().timestamp()
    return round((end - start) * 1000)


def get_all_channels():
    return col_guilds.find()


def get_all_channels_by_time(time: int):
    return col_guilds.find({"time": time})


class Guild(object):
    def __init__(self, guild: GuildObject):
        self._guild = guild

    @property
    def info(self) -> dict:
        return col_guilds.find_one({"_id": self._guild.id})

    def update_where(self, module, value) -> dict:
        col_guilds.update_one({"_id": self._guild.id}, {"$set": {module: value}})
        return self.info

    def insert(self) -> dict:
        if self.info:
            return {"msg": "This guild already exists"}
        data = {
            "_id": self._guild.id,
            "name": self._guild.name,
            "prefix": config.default_prefix,
            "time": config.default_time,
            "anti_spam": False,
            "embed": False
        }
        col_guilds.insert_one(data)
        return self.info


class BlackListUser(object):
    def __init__(self, user: UserObject):
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
    def __init__(self, user: GuildObject):
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
        if not col_azkar.find():
            return 1
        return col_azkar.find().sort("_id", -1).limit(1)[0].get("_id") + 1

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
        x = choice(col_azkar.find())
        return x
