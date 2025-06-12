# コマンド実行権限の確認
from discord import ApplicationContext
from src import COLOR
import os
from dotenv import load_dotenv

load_dotenv()
DEV = int(os.getenv("DEV"))

async def Restrict(ctx: ApplicationContext):
    if ctx.guild is None:
        await ctx.respond("❌ このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
        return False
    if not ctx.author.guild_permissions.manage_guild and ctx.author.id != DEV:
        await ctx.respond("❌ このコマンドを使うにはサーバー管理権限が必要です。", ephemeral=True)
        COLOR.text(f"{ctx.author.name}'s Access was denied!", COLOR.WARN)
        return False
    return True