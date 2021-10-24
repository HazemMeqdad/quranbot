from bot.bot import Bot
import os
import uvloop

if os.name != "nt":
    uvloop.install()

if __name__ == "__main__":
    bot = Bot()
    bot.run()
