# https://gist.github.com/HazemMeqdad/7df331cd799ab5db1d622dc849fa9c5b
import typing as t
from datetime import datetime, timedelta

# Create class can save data in memory with expire time
class Cache:
    def __init__(self, expire_time: int = 60 * 60 * 24):
        self.expire_time = expire_time
        self.cache: t.Dict[str, t.Any] = {}

    def set(self, key: str, value: t.Any):
        self.cache[key] = {"value": value, "time": datetime.now() + timedelta(seconds=self.expire_time)}

    def get(self, key: str) -> t.Any:
        if key not in self.cache:
            return None
        if self.cache[key]["time"] < datetime.now():
            del self.cache[key]
            return None
        return self.cache.get(key)["value"]

    def delete(self, key: str):
        if key in self.cache:
            return
        del self.cache[key]

    def clear(self):
        self.cache.clear()

    def has(self, key: str) -> bool:
        return key in self.cache

    def __contains__(self, item):
        return item in self.cache

    def __getitem__(self, item):
        return self.cache[item]

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __delitem__(self, key):
        del self.cache[key]

    def __iter__(self):
        return iter(self.cache)

    def __len__(self):
        return len(self.cache)

    def __repr__(self):
        return f"Cache(expire_time={self.expire_time}, cache={self.cache})"

    def __str__(self):
        return f"Cache(expire_time={self.expire_time}, cache={self.cache})"
    
