"""SECURITY.py
>コマンドの実行制限
"""
from discord import ApplicationContext
from src.core import CONSOLE
import os
from dotenv import load_dotenv

load_dotenv()
DEV = int(os.getenv("DEV"))
POINT_ADMIN = int(os.getenv("POINT_ADMIN"))

async def Restrict(ctx: ApplicationContext):
    if ctx.guild is None:
        await ctx.respond("❌ このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
        return False
    if not ctx.author.guild_permissions.manage_guild and ctx.author.id != DEV and ctx.author.id != POINT_ADMIN:
        await ctx.respond("❌ このコマンドを使うにはサーバー管理権限が必要です。", ephemeral=True)
        CONSOLE.text(f"{ctx.author.name}'s Access was denied!", CONSOLE.WARN)
        return False
    return True