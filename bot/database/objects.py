from __future__ import annotations
from enum import Enum


class Guild:
    def __init__(self, data_guild: dict) -> None:
        self._data = data_guild
    
    @property
    def id(self) -> int:
        return self._data.get("_id")
    
    @property
    def prefix(self) -> str:
        return self._data.get("prefix")
    
    @property
    def channel_id(self) -> int | None:
        return self._data.get("channel")
    
    @property
    def time(self) -> int:
        return self._data.get("time")
    
    @property
    def anti_spam(self) -> bool:
        return self._data.get("anti_spam")
    
    @property
    def embed(self) -> bool:
        return self._data.get("embed")
    
    @property
    def role_id(self) -> int | None:
        return self._data.get("role_id")

class Azkar:
    def __init__(self, data: dict) -> None:
        self._data = data
    
    @property
    def id(self):
        return self._data.get("_id")
    
    @property
    def content(self):
        return self._data.get("msg")
    
    def __repr__(self) -> str:
        return self.content

class GuildUpdateType(Enum):
    prefix = "prefix"
    channel = "channel"
    time = "time"
    anti_spam = "anti_spam"
    embed = "embed"
    role_id = "role_id"
