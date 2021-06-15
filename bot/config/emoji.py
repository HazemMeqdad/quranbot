class Emoji:
    def __init__(self, bot):
        self.bot = bot
        self.fdr_50 = self.bot.get_emoji(845022052482023495)
        self.ping = self.bot.get_emoji(845021892943544330)
        self.discord = self.bot.get_emoji(846498253674643478)
        self.online = self.bot.get_emoji(853481780484898827)
        self.errors = self.bot.get_emoji(843739803870035979)
        self.on = self.bot.get_emoji(843739804973531176)
        self.off = self.bot.get_emoji(843739805309468674)
        self.fdr_25 = self.bot.get_emoji(844982470611959838)
        self.fdr_4 = self.bot.get_emoji(851776213139587123)
        self.fdr_5 = self.bot.get_emoji(851776233284304907)
        self.yes = self.bot.get_emoji(853378118928564234)
        self.no1 = self.bot.get_emoji(853379949641859072)
        self.loading = self.bot.get_emoji(854391288023089182)

        # self.fdr_50 = str(self.bot.get_emoji(845022052482023495))
        # self.ping = str(self.bot.get_emoji(845021892943544330))
        # self.discord = str(self.bot.get_emoji(846498253674643478))
        # self.online = str(self.bot.get_emoji(853481780484898827))
        # self.errors = str(self.bot.get_emoji(843739803870035979))
        # self.on = str(self.bot.get_emoji(843739804973531176))
        # self.off = str(self.bot.get_emoji(843739805309468674))
        # self.fdr_25 = str(self.bot.get_emoji(844982470611959838))
        # self.fdr_4 = str(self.bot.get_emoji(851776213139587123))
        # self.fdr_5 = str(self.bot.get_emoji(851776233284304907))
        # self.yes = str(self.bot.get_emoji(853378118928564234))
        # self.no1 = str(self.bot.get_emoji(853379949641859072))

        # self.fdr_50 = "<:fdr50:845022052482023495>"
        # self.ping = "<a:ping:845021892943544330>"
        # self.discord = "<a:discord:846498253674643478>"
        # self.errors = "<:errors:843739803870035979>"
        # self.on = "<:on:843739804973531176>"
        # self.off = "<:off:843739805309468674>"
        # self.fdr_25 = "<:fdr25:844982470611959838>"
        # self.fdr_4 = "<:fdr4:851776213139587123>"
        # self.fdr_5 = "<:fdr5:851776233284304907>"
        # self.yes = "<:true:853378118928564234>"
        # # self.yes = "✅"
        # # self.no1 = "❌"
        # self.no1 = "<:false:853379949641859072>"