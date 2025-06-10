from discord.ext import commands
from discord.commands import slash_command
from discord import ApplicationContext
import importlib

class CheckCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="check",
        description="Botが動作しているか確認します。",
        guild_ids=None
    )
    async def check(self, ctx: ApplicationContext):
        message = ("🛠️ モジュールステータス\n")
        
        loaded_cogs = list(self.bot.cogs.keys())
        total_cogs = len(loaded_cogs)

        modules_to_check = ["src.JSON", "src.COLOR", "src.SECURE"]
        module_statuses = []
        for mod in modules_to_check:
            try:
                importlib.import_module(mod)
                module_statuses.append(f"`{mod}`: ✅")
            except Exception as e:
                module_statuses.append(f"`{mod}`: ❌ ({type(e).__name__})")
        message += "\n📦 モジュールチェック:\n" + "\n".join(module_statuses)
        message += f"\n🧩 読み込み済みのCog: **{total_cogs}**個\n🧪 読み込まれているCog:\n"

        if loaded_cogs:
            message += "\n".join(f"・{name}" for name in loaded_cogs)
        else:
            message += "（なし）"

        message += (
            "\n\n🛠️ コマンド更新は以下のURLから:\n"
            "[OAuth2 リンク](https://discord.com/oauth2/authorize?client_id=1380828889156423761&permissions=8&integration_type=0&scope=bot+applications.commands)"
        )

        await ctx.respond(message)

def setup(bot):
    bot.add_cog(CheckCommand(bot))
    print(f"✅ {CheckCommand.__name__} loaded")