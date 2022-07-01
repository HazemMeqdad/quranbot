from dataclasses import dataclass
import typing
import os

@dataclass(init=True)
class Emojis:
    def __init__(self):
        self.hashtag = os.environ.get("HASHTAG_EMOJI", "🔗")
        self.on = os.environ.get("ON_EMOJI", "✅")
        self.off = os.environ.get("OFF_EMOJI", "❌")
        self.ping = os.environ.get("PING_EMOJI", "🏓")
        self.error = os.environ.get("ERROR_EMOJI", "❌")
        self.like = os.environ.get("LIKE_EMOJI", "✅")
        self.dislike = os.environ.get("DISLIKE_EMOJI", "❌")

