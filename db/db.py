import sqlite3

db = sqlite3.connect("db/db.sqlite")

cr = db.cursor()

cr.execute(
    "CREATE TABLE IF NOT EXISTS guilds(guild_id INTEGER PRIMARY KEY, guild_name TEXT, channel INTEGER DEFAULT NULL, prefix TEXT DEFAULT '!')")
cr.execute(
    "CREATE TABLE IF NOT EXISTS cooldown(user_id INTEGER PRIMARY KEY)")


def get_cooldown():
    user = cr.execute("SELECT user_id FROM cooldown")
    all_user = user.fetchall()
    list_users = []
    for i in all_user:
        list_users.append(i[0])
    return list_users


def get_prefix(ctx):
    prefix = cr.execute("SELECT prefix FROM guilds WHERE guild_id = ?", (ctx.guild.id,))
    return prefix.fetchone()[0]


def commit():
    db.commit()
