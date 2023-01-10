import discord 
from . import BaseView

class MoveModule(discord.ui.Modal, title="أنتقال إلى صفحة محددة"):
    position = discord.ui.TextInput(
        label="الصفحة", 
        style=discord.ui.text_input.TextStyle.short,
        placeholder="أدخل رقم الصفحة",
        required=True,
        min_length=1,
    )
    
    def __init__(self, view: BaseView, max_value: int) -> None:
        super().__init__()
        self.view = view
        self.position.max_value = max_value
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        if int(self.position.value) > self.position.max_value or int(self.position.value) < 1:
            await interaction.response.send_message("الصفحة المحددة غير موجودة", ephemeral=True)
            return
        self.view.set_position(int(self.position.value))
        await interaction.response.edit_message(embed=await self.view.get_page())
