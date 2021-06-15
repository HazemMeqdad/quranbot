import mysql.connector
import bot.config as config
import discord
import time
import datetime

db = mysql.connector.connect(**config.database)

cr = db.cursor(buffered=True)

cr.execute("""
CREATE TABLE if not exists `guilds` (
  `id` bigint(30) PRIMARY KEY,
  `guild_name` varchar(25) DEFAULT NULL,
  `prefix` text DEFAULT '!',
  `channel` bigint(30) DEFAULT NULL,
  `time` int(11) DEFAULT 3600 CHECK (`time` >= 1800 and `time` <= 86400),
  `anti_spam` tinyint(1) DEFAULT 0,
  `embed` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
""")

cr.execute("""
CREATE TABLE IF NOT EXISTS blacklist(
    id BIGINT(30) PRIMARY KEY,
    mod_id BIGINT(30) NOT NULL,
    reason VARCHAR(30) DEFAULT NULL,
    timestamp BIGINT(30) NOT NULL
)
""")

print('`connect MySql database`')


def speedtest():
    start = time.monotonic()
    cr.execute("SELECT * FROM guilds")
    end = time.monotonic()
    return round((end - start) * 1000)


class All:
    @staticmethod
    def get_all_channels():
        cr.execute('SELECT * FROM guilds WHERE channel IS NOT NULL')
        return cr.fetchall()


class Guild:
    def __init__(self, guild: discord.Guild):
        self._guild = guild

    @property
    def info(self):
        cr.execute("SELECT * FROM guilds WHERE id = %s" % self._guild.id)
        return cr.fetchone()

    @staticmethod
    def commit():
        db.commit()

    def update_where(self, module, value):
        cr.execute(f"UPDATE guilds SET {module} = %s WHERE id = %s", (value, self._guild.id))
        self.commit()

    def insert(self):
        try:
            cr.execute("INSERT INTO guilds(id, guild_name) VALUES(%s, %s)", (self._guild.id, self._guild.name))
            self.commit()
        except mysql.connector.errors.IntegrityError:
            return


class BlackList:
    def __init__(self, user: discord.User):
        self._user = user

    @staticmethod
    def commit():
        db.commit()

    def insert(self, mod_id, reason=None):
        try:
            cr.execute(
                "INSERT INTO blacklist(id, mod_id, reason, timestamp) VALUES(%s, %s, %s, %s)",
                (self._user.id, mod_id, reason, datetime.datetime.now().timestamp())
            )
            self.commit()
        except mysql.connector.errors.IntegrityError:
            return

    def delete(self):
        cr.execute("DELETE FROM blacklist WHERE id = %s", (self._user.id,))
        self.commit()

    @property
    def info(self):
        cr.execute("SELECT * FROM blacklist WHERE id = %s", (self._user.id,))
        return cr.fetchone()

    @property
    def check(self):
        if not self.info:
            return True
        return False
