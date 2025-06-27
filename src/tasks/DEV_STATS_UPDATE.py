import discord
from src.commands import STATS
from src.core import BASE, CONSOLE

async def run(bot: discord.bot, config):
    """定期的に開発状況を更新するタスク"""
    embed_info = config.get("Share_dev_stats")

    if not embed_info:
        CONSOLE.text(text="[WARN]埋め込みが登録されていません。", pattern=CONSOLE.Warn)
        return  # メッセージ未登録
    
    channel = bot.get_channel(embed_info["channel_id"])
    if not channel:
        return

    try:
        message = await channel.fetch_message(embed_info["message_id"])
    except discord.NotFound:
        CONSOLE.text(text="[WARN]埋め込み先が見つかりませんでした。", pattern=CONSOLE.Warn)
        return  # メッセージが削除された可能性あり

    for guild_id in BASE.GUILD_IDS:
        data = STATS.get_data(guild_id=guild_id)
    if data is None:
        return

    embed = await STATS.set_embed(data)
    await message.edit(embed=embed)