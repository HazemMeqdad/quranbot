from mysql.connector import connect, errors
import bot.config as config
import discord
from time import monotonic
from datetime import datetime
from os.path import isfile
import os
from random import choice

build_path = r"\build.sql"
dir_path = os.path.dirname(os.path.realpath(__file__))

db = connect(**config.database)
cr = db.cursor(buffered=True)


if isfile(build_path):
    cr.execute("source %s" % dir_path+build_path)


print('`connect MySql database`')


def speedtest():
    start = monotonic()
    cr.execute("SELECT * FROM guilds")
    end = monotonic()
    return round((end - start) * 1000)


class Main:
    @staticmethod
    def commit():
        db.commit()


def get_all_channels():
    cr.execute('SELECT * FROM guilds WHERE channel IS NOT NULL')
    return cr.fetchall()


def get_all_channels_by_time(time: int):
    cr.execute('SELECT id FROM guilds WHERE channel IS NOT NULL AND time = %s' % (time,))
    return cr.fetchall()


class Guild(Main):
    def __init__(self, guild: discord.Guild):
        self._guild = guild

    @property
    def info(self) -> dict:
        cr.execute("SELECT * FROM guilds WHERE id = %s" % self._guild.id)
        x = cr.fetchone()
        m = {
            "id": x[0],
            "guild_name": x[1],
            "prefix": x[2],
            "channel": x[3],
            "time": x[4],
            "anti_spam": x[5],
            "embed": x[6]
        }
        return m

    def update_where(self, module, value):
        cr.execute(f"UPDATE guilds SET {module} = %s WHERE id = %s", (value, self._guild.id))
        self.commit()

    def insert(self):
        try:
            cr.execute("INSERT INTO guilds(id, guild_name) VALUES(%s, %s)", (self._guild.id, self._guild.name))
            self.commit()
        except errors.IntegrityError:
            return


class BlackList(Main):
    def __init__(self, user: discord.User):
        self._user = user

    def insert(self, mod_id, reason=None):
        try:
            cr.execute(
                "INSERT INTO blacklist(id, mod_id, reason, timestamp) VALUES(%s, %s, %s, %s)",
                (self._user.id, mod_id, reason, datetime.now().timestamp())
            )
            self.commit()
        except errors.IntegrityError:
            return

    def delete(self):
        cr.execute("DELETE FROM blacklist WHERE id = %s", (self._user.id,))
        self.commit()

    @property
    def info(self):
        cr.execute("SELECT * FROM blacklist WHERE id = %s", (self._user.id,))
        return cr.fetchone()

    @property
    def check(self) -> bool:
        if not self.info:
            return True
        return False


class Azkar(Main):
    def add(self, msg: str):
        cr.execute("INSERT INTO azkar(msg) VALUES(%s)", (msg,))
        self.commit()

    def remove(self, _id: int):
        cr.execute("DELETE FROM azkar WHERE id = %s", (_id,))
        self.commit()

    @property
    def random(self) -> dict:
        cr.execute("SELECT * FROM azkar")
        x = choice(cr.fetchall())
        return {"_id": x[0], "msg": x[1]}

