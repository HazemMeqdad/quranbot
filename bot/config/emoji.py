class Emoji:
    def __init__(self, bot):
        self._bot = bot
        self.fdr_50 = self._bot.get_emoji(853023772248244224)
        self.ping = self._bot.get_emoji(845021892943544330)
        self.discord = self._bot.get_emoji(846498253674643478)
        self.online = self._bot.get_emoji(853024905426763796)
        self.errors = self._bot.get_emoji(843739803870035979)
        self.on = self._bot.get_emoji(843739804973531176)
        self.off = self._bot.get_emoji(843739805309468674)
        # self.fdr_50 = self._bot.get_emoji()
        # self.fdr_50 = self._bot.get_emoji()

