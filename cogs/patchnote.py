from discord.ext import commands
from discord.commands import slash_command
from discord import ApplicationContext, Embed

class releasenote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
    name="releasenote",
    description="Botが動作しているか確認します。リリースノートも送信します。",
    guild_ids=None
    )
    async def check(self, ctx: ApplicationContext):
        embed = Embed(
            title="🛠️ Bot情報の確認",
            color=0x00ff7f  # 任意のカラーコード
        )

        # ✅ コマンド情報
        loaded_cogs = list(self.bot.cogs.keys())
        total_cogs = len(loaded_cogs)

        embed.add_field(name="🧩 有効なコマンド・コマンドグループ", value=f"{total_cogs} 個", inline=True)
        embed.add_field(
            name="🧪 以下一覧",
            value="\n".join(f"・{name}" for name in loaded_cogs) if loaded_cogs else "（なし）",
            inline=False
        )

        # リリースノート
        embed.add_field(
            name="📄 リリースノート Ver2.2.0",
            value=("""
- **修正**: コード設計の見直しとリファクタリングを行い、可読性と保守性を向上させました。
- **修正**: APIの扱い方を変更しました。
- **修正**: 募集コマンドでメンションを追加で送信するようにしました。
                """),
            inline=False
        )

        embed.set_footer(text="✅ チェック完了")
        
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(releasenote(bot))
    print(f"✅ {releasenote.__name__} loaded")