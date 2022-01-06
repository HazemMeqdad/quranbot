from dataclasses import dataclass
import typing


@dataclass(init=True)
class Emojis:
    def __init__(self, emoji_config: typing.Dict[str, str]):
        self.hashtag = emoji_config["hashtag"]
        self.on = emoji_config["_on"]
        self.off = emoji_config["_off"]
        self.ping = emoji_config["ping"]
        self.error = emoji_config["error"]
        self.like = emoji_config["like"]
        self.dislike = emoji_config["dislike"]

