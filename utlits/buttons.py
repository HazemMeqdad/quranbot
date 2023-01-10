from discord import ButtonStyle
from discord.ui import View, Button
import typing as t

class BaseView(View):
    async def on_timeout(self) -> None:
        for index, item in enumerate(self.children):
            self.children[index].disabled = True
        await self.message.edit(view=self)

class SupportButtons(BaseView):
    def __init__(self, timeout: t.Optional[int] = None):
        super().__init__(timeout=timeout)
        self.add_item(Button(
            style=ButtonStyle.url,
            label="إضافة البوت",
            url=f"https://discord.com/oauth2/authorize?client_id=728782652454469662&permissions=8&scope=bot%20applications.commands"
        ))
        self.add_item(Button(
            style=ButtonStyle.url,
            label="الدعم الفني",
            url="https://discord.gg/VX5F54YNuy"
        ))
        self.add_item(Button(
            style=ButtonStyle.url,
            label="لوحة التحكم",
            url="https://fdrbot.com"
        ))

class DownloadSurahView(BaseView):
    def __init__(self, link: str):
        super().__init__(timeout=None)
        self.add_item(Button(
            style=ButtonStyle.link,
            label="تحميل السورة",
            url=link
        ))

