import os
import discord
from discord.ext import commands
from discord import Bot
from src.core import CONSOLE, BASE

class MainProcess(Bot):
    def __init__(self):
        """DevelopperPortal側の設定
        全インテンツの有効化が必須
        """
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.guild_ids = BASE.GUILD_IDS

        self.add_listener(self.on_application_command_error)

    # 認証サーバーの確認
    async def on_ready(self):
        CONSOLE.text(f"> Activating: {self.user}", CONSOLE.Log)
        CONSOLE.text("> Authorized servers:", CONSOLE.Data)
        for guild_id in self.guild_ids:
            try:
                guild = await self.fetch_guild(guild_id)
                if guild:
                    print(f"・{guild.name} (ID: {guild.id})")
                else:
                    print(f"・ID: {guild_id} → ❌ 取得失敗")
            except discord.NotFound:
                print(f"・ID: {guild_id} → ❌ 存在しません（NotFound）")
            except discord.HTTPException as e:
                print(f"・ID: {guild_id} → ❌ HTTPエラー: {e}")
        CONSOLE.text("> Activated!", CONSOLE.Log)

    # エラーハンドラー
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error):
        CONSOLE.text(f"[ERROR] {ctx.command} にてエラー: {type(error).__name__}: {error}\n{type(error)}", CONSOLE.Error)

        if isinstance(error, discord.errors.Forbidden):
            await ctx.respond("❌ Botに権限がありません。", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.respond("❌ あなたにこの操作を行う権限がありません。", ephemeral=True)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.respond(f"⚠️ 実行中にエラーが発生しました: `{error.original}`", ephemeral=True)
        else:
            await ctx.respond("❌ @lake0808 らけちゃあああん!エラー出てるよぉ!", ephemeral=False)

# Botの立ち上げとCogの登録
async def main():
    bot = MainProcess()
    CONSOLE.text("Bot is starting...", CONSOLE.Log)
    for file in os.listdir("cogs"):
        if file.endswith(".py") and not file.startswith("__"):
            bot.load_extension(f"cogs.{file[:-3]}")
    await bot.start(BASE.DISCORD_TOKEN)

# メインプロセスの実行
if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        CONSOLE.text(f"Error: {e}", CONSOLE.Error)