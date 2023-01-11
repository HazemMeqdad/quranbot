import motor.motor_asyncio as motor
import os
import typing as t
from .objects import DbGuild, Saves, Azan
from dataclasses import asdict


class DataNotFound(Exception):
    ...

class Database(object):
    URI = os.environ["MONGO_URL"]
    CLIENT: motor.AsyncIOMotorClient = None
    DATABASE: motor.AsyncIOMotorDatabase = None

    @staticmethod
    def initialize():
        Database.CLIENT = client = motor.AsyncIOMotorClient(Database.URI)
        Database.DATABASE = client["QuranBot"]
    
    @staticmethod
    async def insert(collection: str, data: t.Union[t.Dict, DbGuild, Saves, Azan]) -> None:
        if isinstance(data, (DbGuild, Saves, Azan)):
            await Database.DATABASE[collection].insert_one(asdict(data))
            return
        await Database.DATABASE[collection].insert_one(data)

    @staticmethod
    async def find(collection: str, query: t.Dict) -> t.Dict:
        data = Database.DATABASE[collection].find(query)
        as_list = await data.to_list(length=None)
        return as_list

    @staticmethod
    async def find_one(collection: str, query: t.Dict, raise_not_found: bool = True) -> t.Union[t.Dict, DbGuild, Saves, Azan, None]:
        data = await Database.DATABASE[collection].find_one(query)
        if not data and raise_not_found:
            raise DataNotFound(f"Data of `{query}` is missing")
        elif not data:
            return None
        match collection:
            case "guilds":
                return DbGuild.from_kwargs(**data)
            case "saves":
                return Saves.from_kwargs(**data)
            case "azan":
                return Azan.from_kwargs(**data)
            case _:
                return data

    @staticmethod
    async def update_one(collection: str, query: t.Dict, new_values: t.Dict) -> None:
        await Database.DATABASE[collection].update_one(query, {"$set": new_values})

    @staticmethod
    async def delete_one(collection: str, query: t.Dict) -> None:
        await Database.DATABASE[collection].delete_one(query)

