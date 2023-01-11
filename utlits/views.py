import discord
from .msohaf_data import moshaf_types, moshafs
from cogs.moshaf import MoshafView
from . import BaseView
from database import Database

class OpenMoshafView(BaseView):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📖", style=discord.ButtonStyle.grey, custom_id="moshaf:open")
    async def open_moshaf(self, interaction: discord.Interaction, button: discord.Button):
        db_data = await Database.find_one("saves", {"_id": f"moshaf_{interaction.user.id}"}, raise_not_found=False)
        data = db_data.data if db_data else None
        guild_data = await Database.find_one("guilds", {"_id": interaction.guild.id})
        moshaf_type = guild_data.moshaf_type if guild_data.moshaf_type else 1
        page_number = 1
        if data is not None and data["moshaf_type"] == moshaf_type:
            page_number = data["page_number"]

        moshaf = [i for i in moshaf_types if i["value"] == moshaf_type][0]

        embed = discord.Embed(title=moshaf["name"], color=0xffd430)
        embed.set_image(url=f"http://www.islamicbook.ws/{moshaf_type}/{page_number}.{moshafs[str(moshaf['value'])]['type']}")
        embed.set_footer(text=f"الصفحة {page_number}/{moshafs[str(moshaf['value'])]['page_end']}")
        await interaction.response.send_message(
            embed=embed, 
            view=MoshafView(moshaf_type, page_number, moshafs[str(moshaf['value'])]["page_end"], interaction.user.id),
            ephemeral=True
        )