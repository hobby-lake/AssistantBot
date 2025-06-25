from discord.ext import commands
from discord.commands import slash_command
from discord import ApplicationContext
from src.commands import BOSYU
from src.core import BASE

class BosyuManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="bosyu", description="任意のゲームで募集をかけます")
    async def bosyu(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)
        guild = ctx.guild
        filtered_roles_path = BASE.get_json_path(guild_id=guild.id, category="role")
        filtered_roles = BASE.dataload(filtered_roles_path)
        if guild is None:
            await ctx.respond("このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
            return
        if not filtered_roles:
            await ctx.respond("使用可能なロールが見つかりません。", ephemeral=True)
            return

        view = BOSYU.BosyuUI(interaction=ctx.interaction, roles=guild.roles)
        await ctx.respond("募集内容を入力してください：", view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(BosyuManager(bot))
    print(f"✅ {BosyuManager.__name__} loaded")