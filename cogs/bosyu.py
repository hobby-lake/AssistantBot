from discord.ext import commands
from discord.commands import slash_command
from discord import ApplicationContext
from src.commands import BosyuUI

class BosyuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="bosyu", description="任意のゲームで募集をかけます")
    async def bosyu(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)
        guild = ctx.guild
        if guild is None:
            await ctx.respond("このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
            return

        view = BosyuUI(interaction=ctx.interaction, roles=guild.roles)
        await ctx.respond("募集内容を入力してください：", view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(BosyuCog(bot))
    print(f"✅ {BosyuCog.__name__} loaded")