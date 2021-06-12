import mysql.connector
import bot.config as config
import discord
import datetime


db = mysql.connector.connect(
    host=config.database['host'],
    user=config.database['user'],
    password=config.database['password'],
    database=config.database['database']
)


cr = db.cursor(buffered=True)

cr.execute("""
CREATE TABLE IF NOT EXISTS guilds(
    id BIGINT(30) PRIMARY KEY,
    guild_name VARCHAR(25) NOT NULL,
    prefix TEXT DEFAULT '!',
    channel BIGINT(30) NOT NULL,
    time INT DEFAULT 3600 CHECK(time>=1800 AND time<=86400),
    timer INT DEFAULT 0,
    anti_spam BOOLEAN DEFAULT false,
    embed BOOLEAN DEFAULT false
)
""")

print('`connect MySql database`')


def speed_test():
    start = datetime.datetime.now().timestamp()
    db_test = mysql.connector.connect(
        host=config.database['host'],
        user=config.database['user'],
        password=config.database['password'],
        database=config.database['database']
    )
    db_test.close()
    return round(datetime.datetime.now().timestamp() - start)


class All:
    @staticmethod
    def get_all_channels():
        cr.execute('SELECT id, channel, time FROM guilds WHERE channel IS NOT NULL')
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
        cr.execute(f"UPDATE guilds SET '{module}' = %s WHERE id = %s", (value, self._guild.id))

    def delete_where(self, module, value):
        cr.execute(f"UPDATE guilds SET '{module}' = %s WHERE id = %s", (value, self._guild.id))

    def insert(self):
        cr.execute("INSERT INTO guilds(id, guild_name) VALUES(%s, %s)", (self._guild.id, self._guild.name))