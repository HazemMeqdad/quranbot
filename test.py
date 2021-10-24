import os
import pymongo
import database
import time
import uvloop

if os.name != "nt":
    uvloop.install()


mongo_url = open("./bot/config/mongo_url.txt", "r").read()

db = pymongo.MongoClient(mongo_url)
db_client = db["fa-azcrone"]

print('`connect MongoDB database`')

start = time.monotonic()

cache = database.DB(db_client=db_client)
print(cache.get_guild(729526735749513267).prefix)
print(cache.get_guild(729526735749513267).time)
print(cache.get_guild(729526735749513267).embed)


print(time.monotonic() - start)
