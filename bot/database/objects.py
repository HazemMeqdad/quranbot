from dataclasses import dataclass
from enum import Enum
import typing as t
from datetime import datetime

@dataclass
class Guild:
    _id: int
    time: int
    embed: bool
    next_zker: datetime
    channel_id: t.Optional[int] = None
    role_id: t.Optional[int] = None
    webhook: t.Optional[t.Dict[t.Any]] = None
    color: t.Optional[str] = None

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
    webhook = "webhook"
    next_zker = "next_zker"
