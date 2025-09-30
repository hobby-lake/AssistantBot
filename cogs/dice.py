from discord.ext import commands
from discord.commands import slash_command
from discord import ApplicationContext

from src.commands import DICE


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="dice", description="/dice サイコロの数 サイコロの目の数")
    async def bosyu(self, ctx: ApplicationContext, dice_amount: int, dice_type: int):
        await DICE.roll(ctx=ctx, amount=dice_amount, type=dice_type)

def setup(bot):
    bot.add_cog(Dice(bot))
    print(f"✅ {Dice.__name__} loaded")