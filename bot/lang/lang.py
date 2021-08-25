from discord import Guild
from .. import db
from json import load
from discord.ext.commands.core import Command


class Languages(object):
    def __init__(self, guild: Guild):
        self._guild = guild
        self.path = "bot/lang/json/"

    @property
    def get_lang(self) -> str:
        lang = db.Guild(self._guild).info.get("lang")
        if not lang:
            return "ar"
        return lang

    def _read(self):
        with open(f"{self.path}{self.get_lang}.json", "r", encoding='utf-8') as file:
            data = load(file)
        return data

    def get_response(self, command: Command):
        return self._read()[command.cog_name][command.name]

    def get_response_errors(self):
        return self._read()["Errors"]
