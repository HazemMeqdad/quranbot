import discord
from discord.ext import commands
from discord import app_commands

class Errors(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error

    async def cog_unload(self) -> None:
        self.bot.tree.on_error = None

    async def on_app_command_error(self, interaction: discord.Interaction, error: Exception) -> None:
        """Handles slash command errors."""
        if isinstance(error, app_commands.errors.CommandInvokeError):
            error_message = str(error.original).split("str: ")[-1].strip()
            await interaction.response.send_message(error_message, ephemeral=True)
            return
        if isinstance(error, app_commands.errors.CommandNotFound):
            await interaction.response.send_message(f"Command not found.", ephemeral=True)
            return
        await interaction.response.send_message(f"An error occured: {error}", ephemeral=True)
        raise error

    # Igrone commands prefix errors
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        return 

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Errors(bot))
