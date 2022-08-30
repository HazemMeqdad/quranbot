import pymongo
import os
from dataclasses import dataclass
import typing as t
from datetime import datetime
import pymongo.collection

coon = pymongo.MongoClient(os.environ["MONGO_URL"])
db = coon.get_database("fdrbot")

@dataclass
class DbGuild:
    _id: int
    channel_id: t.Optional[int]
    time: int
    embed: bool
    role_id: t.Optional[int]
    webhook: t.Dict[str, t.Union[str, int]]
    next_zker: datetime
    moshaf_type: t.Optional[int] = None

@dataclass
class Saves:
    _id: str
    data: t.Dict[t.Any, t.Any]

@dataclass
class Azan:
    _id: int
    channel_id: int
    address: str
    role_id: t.Optional[int] = None

class BaseDatabase:
    def __init__(self) -> None:
        self.col: pymongo.collection.Collection = None
    
    def find_all(self) -> list:
        return list(self.col.find({}))
    
    def delete(self, _id: int) -> None:
        self.col.delete_one({"_id": _id})

class Database(BaseDatabase):
    """
    Database for the bot
    """
    def __init__(self) -> None:
        self.col = db.get_collection("guilds")

    def find_guild(self, guild_id: int) -> t.Optional[DbGuild]:
        data = self.col.find_one({"_id": guild_id})
        if not data:
            return None
        return DbGuild(**data)

    @t.overload
    def find_all(self) -> t.List[DbGuild]:
        data = self.col.find({})
        return [DbGuild(**i) for i in list(data)]

    def fetch_guilds_with_datetime(self) -> t.List[DbGuild]:
        now = datetime.now()
        data = self.col.find({
            "next_zker": {"$lt": now}, 
            "channel_id": {"$ne": None}, 
            "webhook": {"$ne": None}
        })
        return [DbGuild(**i) for i in list(data) if i.get("channel_id") is not None and i.get("webhook") is not None]

    def insert_guild(self, guild_id: int) -> None:
        self.col.insert_one({
            "_id": guild_id,
            "channel_id": None,
            "time": 3600,
            "embed": False,
            "role_id": None,
            "webhook": None,
            "next_zker": datetime.now(),
            "moshaf_type": None
        })
    
    def update_guild(self, guild_id: int, **kwargs) -> None:
        self.col.update_one({"_id": guild_id}, {"$set": kwargs})
    
    def delete_guild(self, guild_id: int) -> None:
        self.col.delete_one({"_id": guild_id})


class SavesDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__()
        self.col = db.get_collection("saves")

    def insert(self, _id: str, data: t.Dict[t.Any, t.Any]) -> None:
        self.col.insert_one({
            "_id": _id,
            "data": data
        })

    def find_all(self) -> t.List[Saves]:
        data = self.col.find({})
        return [Saves(**i) for i in list(data)]

    def find_one(self, _id: str) -> t.Optional[Saves]:
        data = self.col.find_one({"_id": _id})
        if not data:
            return None
        return Saves(**data)

    def update(self, _id: str, data: t.Dict[t.Any, t.Any]) -> None:
        self.col.update_one({"_id": _id}, {"$set": {"data": data}})


class AzanDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__()
        self.col = db.get_collection("azan")
    
    def find_guild(self, _id: int) -> t.Optional[Azan]:
        data = self.col.find_one({"_id": _id})
        if not data:
            return None
        return Azan(**data)

    def find_all(self) -> t.List[Azan]:
        data = self.col.find({})
        return [Azan(**i) for i in list(data)]

    def insert(self, _id: int, channel_id: int, address: str, role_id: t.Optional[int] = None) -> None:
        self.col.insert_one({
            "_id": _id,
            "channel_id": channel_id,
            "address": address,
            "role_id": role_id
        })

    def update(self, _id: int, channel_id: int, address: str, role_id: t.Optional[int] = None) -> None:
        self.col.update_one({"_id": _id}, {"$set": {
            "channel_id": channel_id,
            "address": address,
            "role_id": role_id
        }})

    def delete(self, _id: int) -> None:
        self.col.delete_one({"_id": _id})

