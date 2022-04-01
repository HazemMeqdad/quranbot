from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import typing as t


@dataclass
class Guild:
    _id: int
    prefix: str
    channel: t.Optional[int]
    time: int
    anti_spam: bool
    embed: bool
    role_id: t.Optional[int] = None

    @property
    def id(self) -> int:
        return self._id


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
