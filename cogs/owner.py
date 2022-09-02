import discord
from discord.ext import commands
from discord import app_commands


@app_commands.guild_only()
class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="restart", description="Reloads a cog.")
    @commands.is_owner()
    async def all_reload(self, interaction: discord.Interaction) -> None:
        """Reloads a cog."""
        for cog in self.bot.cogs:
            try:
                await self.bot.reload_extension(cog)
            except Exception as e:
                await interaction.response.send_message(f"Failed to reload cog {cog}: {e}")
            else:
                await interaction.response.send_message(f"Reloaded cog {cog}")

    @app_commands.command(name="load", description="Loads a cog.")
    @commands.is_owner()
    async def load(self, interaction: discord.Interaction, cog: str) -> None:
        """Loads a cog."""
        try:
            await self.bot.load_extension(cog)
        except Exception as e:
            await interaction.response.send_message(f"Failed to load cog {cog}: {e}")
        else:
            await interaction.response.send_message(f"Loaded cog {cog}")
        
    @app_commands.command(name="unload", description="Unloads a cog.")
    @commands.is_owner()
    async def unload(self, interaction: discord.Interaction, cog: str) -> None:
        """Unloads a cog."""
        try:
            await self.bot.unload_extension(cog)
        except Exception as e:
            await interaction.response.send_message(f"Failed to unload cog {cog}: {e}")
        else:
            await interaction.response.send_message(f"Unloaded cog {cog}")
        
    @app_commands.command(name="reload", description="Reloads a cog.")
    @commands.is_owner()
    async def reload(self, interaction: discord.Interaction, cog: str) -> None:
        """Reloads a cog."""
        try:
            await self.bot.reload_extension(cog)
        except Exception as e:
            await interaction.response.send_message(f"Failed to reload cog {cog}: {e}")
        else:
            await interaction.response.send_message(f"Reloaded cog {cog}")
        
    @app_commands.command(name="eval", description="Evaluates a code.")
    @commands.is_owner()
    async def eval(self, interaction: discord.Interaction, *, code: str) -> None:
        """Evaluates a code."""
        try:
            result = eval(code)
        except Exception as e:
            await interaction.response.send_message(f"Failed to evaluate code: {e}")
        else:
            await interaction.response.send_message(f"Evaluated code: {result}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot))
