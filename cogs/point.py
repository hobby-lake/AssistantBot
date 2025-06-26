from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
from discord import ApplicationContext, Member
from src.commands import POINT

class PointManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    point = SlashCommandGroup("point", "ポイント管理コマンド")

    @point.command(name="check", description="ポイント残高を確認します。")
    async def check(self, ctx: ApplicationContext, target: Option(Member, "対象ユーザー", required = False, default=None)): # type:ignore
        await POINT.check(self, ctx, target)

    @point.command(name="plus", description="ポイントを付与します。")
    async def plus(self, ctx: ApplicationContext, target: Member, amount: int):
        await POINT.plus(self, ctx, target, amount)

    @point.command(name="minus", description="ポイントを減らします。")
    async def minus(self, ctx: ApplicationContext, target: Member, amount: int):
        await POINT.minus(self, ctx, target, amount)

def setup(bot):
    bot.add_cog(PointManager(bot))
    print(f"✅ {PointManager.__name__} loaded")