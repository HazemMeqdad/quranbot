import mysql.connector
import config
import discord


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
embed BOOLEAN DEFAULT false)
""")

print('`connect MySql database`')


def get_prefix(guild: discord.Guild):
    cr.execute("SELECT prefix FROM guilds WHERE id = %s", (guild.id,))
    return cr.fetchone()[0]


def get_channel(guild: discord.Guild):
    cr.execute("SELECT channel FROM guilds WHERE id = %s", (guild.id,))
    return cr.fetchone()[0]


def get_time(guild: discord.Guild):
    cr.execute('SELECT time FROM guilds WHERE id = %s', (guild.id,))
    return cr.fetchone()[0]


def get_timer(guild: discord.Guild):
    cr.execute('SELECT timer FROM guilds WHERE id = %s', (guild.id,))
    return cr.fetchone()[0]


def get_all_channels():
    cr.execute('SELECT id, channel, time FROM guilds WHERE channel IS NOT NULL')
    # cr.execute('SELECT * FROM guilds WHERE channel IS NOT NULL')
    return cr.fetchall()


def set_prefix(guild: discord.Guild, new_prefix: str):
    cr.execute('UPDATE guilds SET prefix = %s WHERE id = %s', (new_prefix, guild.id))
    commit()
    return


def set_channel(guild: discord.Guild, new_channel: discord.TextChannel):
    cr.execute('UPDATE guilds SET channel = %s WHERE id = %s', (new_channel.id, guild.id))
    commit()
    return


def set_time(guild: discord.Guild, new_time: int):
    cr.execute('UPDATE guilds SET time = %s WHERE id = %s', (new_time, guild.id))
    cr.execute('UPDATE guilds SET timer = %s WHERE id = %s', (new_time, guild.id))
    commit()
    return


def edit_time(guild: discord.Guild, time: int):
    cr.execute('UPDATE guilds SET timer = %s WHERE id = %s', (time, guild.id))
    commit()


def rev_timer(guild: discord.Guild):
    cr.execute('UPDATE guilds SET timer = %s WHERE id = %s', (get_time(guild), guild.id))
    commit()
    return


def delete_guild(guild_id: int):
    cr.execute('DELETE FROM guilds WHERE id = %s', (guild_id,))
    commit()
    return


def remove_channel(guild: discord.Guild):
    cr.execute('UPDATE guilds SET channel = %s WHERE id = %s', (None, guild.id))
    commit()
    return


def get_spam(guild: discord.Guild):
    cr.execute('SELECT anti_spam FROM guilds WHERE id = %s', (guild.id,))
    if cr.fetchone()[0] == 1:
        return True
    return False


def anti_spam(guild: discord.Guild, status: bool):
    if status:
        cr.execute('UPDATE guilds SET anti_spam = TRUE WHERE id = %s', (guild.id,))
        commit()
        return
    cr.execute('UPDATE guilds SET anti_spam = FALSE WHERE id = %s', (guild.id,))
    commit()
    return


def add_guild(guild: discord.Guild):
    try:
        cr.execute('INSERT INTO guilds(id, guild_name) VALUES(%s, %s)', (guild.id, guild.name))
        commit()
    except mysql.connector.errors.IntegrityError:
        pass


def remove_guild(guild: discord.Guild):
    try:
        cr.execute('DELETE FROM guilds WHERE id = %s', (guild.id,))
        commit()
    except:
        pass


def embed(guild: discord.Guild, status: bool):
    if status:
        cr.execute('UPDATE guilds SET embed = TRUE WHERE id = %s', (guild.id,))
        commit()
        return
    cr.execute('UPDATE guilds SET embed = FALSE WHERE id = %s', (guild.id,))
    commit()
    return


def get_embed(guild: discord.Guild):
    cr.execute('SELECT embed FROM guilds WHERE id = %s', (guild.id,))
    if cr.fetchone()[0] == 1:
        return True
    return False


def get_info(guild: discord.Guild):
    cr.execute('SELECT * FROM guilds WHERE id = %s', (guild.id,))
    return cr.fetchone()


def commit():
    db.commit()


# print(get_all_channels())


# cr.execute('SELECT * FROM guilds WHERE id = 654423706294026270')

# d = cr.fetchone()
# print(d)
# for i in d:
#     print(f'{i}: {type(i)}')

