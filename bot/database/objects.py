from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import typing as t


@dataclass
class Guild:
    _id: int
    time: int
    embed: bool
    channel_id: t.Optional[int] = None
    role_id: t.Optional[int] = None
    webhook_url: t.Optional[str] = None
    color: str = None

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
    channel_id = "channel_id"
    time = "time"
    embed = "embed"
    role_id = "role_id"
    webhook_url = "webhook_url"
