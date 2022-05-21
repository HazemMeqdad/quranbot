from dataclasses import dataclass
import typing


@dataclass(init=True)
class Emojis:
    def __init__(self, emoji_config: typing.Dict[str, str]):
        self.hashtag = emoji_config.get("hashtag", "#️⃣")
        self.on = emoji_config.get("_on", "🟢")
        self.off = emoji_config.get("_off", "🔴")
        self.ping = emoji_config.get("ping", "🏓")
        self.error = emoji_config.get("error", "❌")
        self.like = emoji_config.get("like", "✅")
        self.dislike = emoji_config.get("dislike", "❌")

