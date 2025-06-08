from discord.ext import commands
from discord.commands import slash_command
from discord import ApplicationContext

class CheckCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_ids = bot.guild_ids

    @slash_command(
        name="check",
        description="Botが動作しているか確認します。",
        guild_ids=None  # None にするとグローバル登録。遅延あり。
    )
    async def check(self, ctx: ApplicationContext):
        await ctx.respond("Botは正常に動作しています。\nコマンド更新は以下のURLからお願いします。\nhttps://discord.com/oauth2/authorize?client_id=1380828889156423761&permissions=8&integration_type=0&scope=bot+applications.commands")

def setup(bot):
    bot.add_cog(CheckCommand(bot))
    print(f"✅ {CheckCommand.__name__} loaded")