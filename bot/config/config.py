from configparser import ConfigParser

x = ConfigParser()
x.read("config.ini")

token = x.get("BOT", "token")
owners = list(map(int, x.get("BOT", "owners").split(",")))
default_prefix = x.get("BOT", "default_prefix")
default_time = x.getint("BOT", "default_time")
shards_count = x.getint("BOT", "shards_count")

webhook_shard = x.get("WEBHOOK", "shards")
webhook_errors = x.get("WEBHOOK", "errors")
webhook_log = x.get("WEBHOOK", "logs")
webhook_blacklist = x.get("WEBHOOK", "blacklist")

mongo_url = x.get("DATABASE", "mongo_url")


class Emoji:
    def __init__(self, bot):
        self.bot = bot
        self.fdr_50 = self.bot.get_emoji(x.getint("EMOJIS", "fdr_50"))
        self.ping = self.bot.get_emoji(x.getint("EMOJIS", "ping"))
        self.discord = self.bot.get_emoji(x.getint("EMOJIS", "discord"))
        self.online = self.bot.get_emoji(x.getint("EMOJIS", "online"))
        self.errors = self.bot.get_emoji(x.getint("EMOJIS", "errors"))
        self.on = self.bot.get_emoji(x.getint("EMOJIS", "on"))
        self.off = self.bot.get_emoji(x.getint("EMOJIS", "off"))
        self.fdr_25 = self.bot.get_emoji(x.getint("EMOJIS", "fdr_25"))
        self.fdr_4 = self.bot.get_emoji(x.getint("EMOJIS", "fdr_4"))
        self.fdr_5 = self.bot.get_emoji(x.getint("EMOJIS", "fdr_5"))
        self.yes = self.bot.get_emoji(x.getint("EMOJIS", "yes"))
        self.no1 = self.bot.get_emoji(x.getint("EMOJIS", "no1"))
        self.loading = self.bot.get_emoji(x.getint("EMOJIS", "loading"))
        self.MisharyAlafasy = self.bot.get_emoji(x.getint("EMOJIS", "MisharyAlafasy"))
        self.YasserAlDousari = self.bot.get_emoji(x.getint("EMOJIS", "YasserAlDousari"))
        self.MaherAlmaikulai = self.bot.get_emoji(x.getint("EMOJIS", "MaherAlmaikulai"))
        self.IslamSobhi = self.bot.get_emoji(x.getint("EMOJIS", "IslamSobhi"))
        self.AbdullrahmanAlsudais = self.bot.get_emoji(x.getint("EMOJIS", "AbdullrahmanAlsudais"))
        self.AbdulBasitAbdulSamad = self.bot.get_emoji(x.getint("EMOJIS", "AbdulBasitAbdulSamad"))


# https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
def _hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


class Color:
    def __init__(self):
        self.red = _hex_to_rgb(x.get("COLOR", "red"))
        self.green = _hex_to_rgb(x.get("COLOR", "green"))
        self.gold = _hex_to_rgb(x.get("COLOR", "gold"))
