import os
import discord
from discord.ext import commands
from discord import Bot
from dotenv import load_dotenv
from src import JSON,COLOR

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = [int(gid.strip()) for gid in os.getenv("DEBUG_GUILD_ID", "").split(",") if gid.strip()]
AUTHORIZED_USER_ID = int(os.getenv("DEV"))

# メインプログラム
class MainProcess(Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.guild_ids = GUILD_IDS

        self.add_listener(self.on_application_command_error)

    async def on_ready(self):
        COLOR.text(f"> Activating: {self.user}", COLOR.Log)
        COLOR.text("> Authorized servers:", COLOR.Data)
        for guild_id in GUILD_IDS:
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
        COLOR.text("> Activated!", COLOR.Log)

    async def on_application_command_error(self, ctx: discord.ApplicationContext, error):
        COLOR.text(f"[ERROR] {ctx.command} にてエラー: {type(error).__name__}: {error}", COLOR.Error)

        if isinstance(error, discord.errors.Forbidden):
            await ctx.respond("❌ Botに権限がありません。", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.respond("❌ あなたにこの操作を行う権限がありません。", ephemeral=True)
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.respond(f"⚠️ 実行中にエラーが発生しました: `{error.original}`", ephemeral=True)
        else:
            await ctx.respond("❌ 未知のエラーが発生しました。", ephemeral=True)

# Botの立ち上げとCogの登録
async def main():
    bot = MainProcess()
    COLOR.text("Bot is starting...", COLOR.Log)
    for file in os.listdir("cogs"):
        if file.endswith(".py") and not file.startswith("__"):
            bot.load_extension(f"cogs.{file[:-3]}")
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        COLOR.text(f"Error: {e}", COLOR.Error)