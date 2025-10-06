from discord.ext import commands
from discord.commands import slash_command
from discord import ApplicationContext

from src.commands.DICE import Kujibiki as SOURCE


class Kujibiki(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="kujibiki", description="くじびきを作成します")
    async def kujibiki(self, ctx: ApplicationContext):
        await ctx.send_modal(SOURCE.Modal(None))

def setup(bot):
    bot.add_cog(Kujibiki(bot))
    print(f"✅ {Kujibiki.__name__} loaded")