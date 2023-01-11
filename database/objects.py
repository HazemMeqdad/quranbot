from dataclasses import dataclass
import typing as t
from datetime import datetime
from inspect import signature

# https://stackoverflow.com/questions/55099243/python3-dataclass-with-kwargsasterisk
class BaseObject(object):
    @classmethod
    def from_kwargs(cls, **kwargs):
        # fetch the constructor's signature
        cls_fields = {field for field in signature(cls).parameters}

        # split the kwargs into native ones and new ones
        native_args, new_args = {}, {}
        for name, val in kwargs.items():
            if name in cls_fields:
                native_args[name] = val
            else:
                new_args[name] = val

        # use the native ones to create the class ...
        ret = cls(**native_args)

        # ... and add the new ones by hand
        for new_name, new_val in new_args.items():
            setattr(ret, new_name, new_val)
        return ret

@dataclass(init=True)
class DbGuild(BaseObject):
    _id: int
    channel_id: t.Optional[int] = None
    time: int = 1800
    embed: bool = False
    role_id: t.Optional[int] = None
    next_zker: datetime = datetime.now()
    webhook_url: t.Optional[int] = None
    moshaf_type: t.Optional[int] = None

@dataclass(init=True)
class Saves(BaseObject):
    _id: str
    data: t.Dict[t.Any, t.Any]

@dataclass(init=True)
class Azan(BaseObject):
    _id: int
    channel_id: int
    address: str
    role_id: t.Optional[int] = None
    webhook_url: t.Optional[str] = None
