from discord.ext import commands
from discord.commands import slash_command
from discord import ApplicationContext, Embed
import importlib

class CheckCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
    name="check",
    description="Botが動作しているか確認します。リリースノートも送信します。",
    guild_ids=None
)
    async def check(self, ctx: ApplicationContext):
        embed = Embed(
            title="🛠️ Botステータス確認",
            description="Botの稼働状況とモジュールの読み込み状況を確認します。",
            color=0x00BFFF  # 任意のカラーコード
        )

        # ✅ モジュールチェック
        modules_to_check = ["src.JSON", "src.COLOR", "src.SECURE"]
        module_statuses = []
        for mod in modules_to_check:
            try:
                importlib.import_module(mod)
                module_statuses.append(f"`{mod}`: ✅")
            except Exception as e:
                module_statuses.append(f"`{mod}`: ❌ ({type(e).__name__})")

        embed.add_field(name="📦 モジュールチェック", value="\n".join(module_statuses), inline=False)

        # ✅ Cog情報
        loaded_cogs = list(self.bot.cogs.keys())
        total_cogs = len(loaded_cogs)

        embed.add_field(name="🧩 読み込み済みのCog", value=f"{total_cogs} 個", inline=True)
        embed.add_field(
            name="🧪 Cog一覧",
            value="\n".join(f"・{name}" for name in loaded_cogs) if loaded_cogs else "（なし）",
            inline=False
        )

        # ✅ OAuth2リンク
        embed.add_field(
            name="🔗 コマンド更新リンク",
            value="[OAuth2 リンク](https://discord.com/oauth2/authorize?client_id=1380828889156423761&permissions=8&integration_type=0&scope=bot+applications.commands)",
            inline=False
        )

        embed.set_footer(text="✅ チェック完了")
        
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(CheckCommand(bot))
    print(f"✅ {CheckCommand.__name__} loaded")