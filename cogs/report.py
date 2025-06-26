from discord.ext import commands
from discord.commands import SlashCommandGroup
from discord import ApplicationContext
from src.commands import REPORT

class ReportSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    report = SlashCommandGroup("report", "レポートコマンド")

    @report.command(name="bug", description="バグレポートを送信します。")
    async def bug(self, ctx: ApplicationContext):
        guild = ctx.guild
        if guild is None:
            await ctx.respond("このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
            return

        await ctx.send_modal(REPORT.BugReportModal())

def setup(bot):
    bot.add_cog(ReportSystem(bot))
    print(f"✅ {ReportSystem.__name__} loaded")