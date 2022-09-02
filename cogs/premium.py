import discord
from discord.ext import commands
from discord import app_commands

@app_commands.guild_only()
class Premium(commands.GroupCog, name="premium"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @app_commands.command(name="buy", description="شرأء نسخة خاصة من البوت")
    async def buy(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="بسم الله الرحمن الرحيم",
            description="النسخة الخاصة من بوت فاذكروني, يمكنك الآن شراء نسختك الخاصة من بوت فاذكروني",
            color=0xffd430
        )
        embed.add_field(name="السعر:", value="شهر: 2.99$\nثلاث شهور: 7.99$\nغير ذالك تواصل معنا", inline=False)
        embed.add_field(name="الخصائص:", value="بوت خاص لك يمكنك فقط تغير اسم و صورة البوت لا توجد اي ميزات حصرية للنسخه البريميوم", inline=False)
        embed.add_field(name="طريقة الطلب:", value="[تواصل معنا](https://discord.gg/VX5F54YNuy)")
        embed.set_footer(
            text="النسخة البريميوم لبوت فاذكروني هدفها الدعم المادي للبوت لشراء الخوادم الخاص للبوت و ليس للأرباح الشخصية",
            icon_url=self.bot.user.avatar.url   
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Premium(bot))
