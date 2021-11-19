import hikari


class EmojiNotFound(Exception):
    ...

class Emojis(object):
    def __init__(self, rest: hikari.impl.rest.RESTClientImpl):
        self.rest = rest

    @property
    async def hashtag(self) -> hikari.KnownCustomEmoji:
        emoji = await self.rest.fetch_emoji(843710915861545000, 845022052482023495)
        if isinstance(emoji, hikari.KnownCustomEmoji):
            return emoji
        raise EmojiNotFound("hashtag emoji not found :/")

    @property
    async def on(self) -> hikari.KnownCustomEmoji:
        emoji = await self.rest.fetch_emoji(843710915861545000, 843739804973531176)
        if isinstance(emoji, hikari.KnownCustomEmoji):
            return emoji
        raise EmojiNotFound("on emoji not found :/")

    @property
    async def off(self) -> hikari.KnownCustomEmoji:
        emoji = await self.rest.fetch_emoji(843710915861545000, 843739805309468674)
        if isinstance(emoji, hikari.KnownCustomEmoji):
            return emoji
        raise EmojiNotFound("off emoji not found :/")

    @property
    async def ping(self) -> hikari.KnownCustomEmoji:
        emoji = await self.rest.fetch_emoji(843710915861545000, 845021892943544330)
        if isinstance(emoji, hikari.KnownCustomEmoji):
            return emoji
        raise EmojiNotFound("off emoji not found :/")

    @property
    async def error(self) -> hikari.KnownCustomEmoji:
        emoji = await self.rest.fetch_emoji(843710915861545000, 843739803870035979)
        if isinstance(emoji, hikari.KnownCustomEmoji):
            return emoji
        raise EmojiNotFound("error emoji not found :/")

    @property
    async def yes(self) -> hikari.KnownCustomEmoji:
        emoji = await self.rest.fetch_emoji(843710915861545000, 845022054699892757)
        if isinstance(emoji, hikari.KnownCustomEmoji):
            return emoji
        raise EmojiNotFound("yes emoji not found :/")

    @property
    async def no(self) -> hikari.KnownCustomEmoji:
        emoji = await self.rest.fetch_emoji(843710915861545000, 845022058345398272)
        if isinstance(emoji, hikari.KnownCustomEmoji):
            return emoji
        raise EmojiNotFound("no emoji not found :/")

