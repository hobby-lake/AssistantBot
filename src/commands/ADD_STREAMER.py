from src.core import BASE
import re

async def run(ctx, name: str, display_name: str, youtube_channel_id: str = None, twitch_username: str = None):
    guild_id = ctx.guild.id
    path = str(BASE.get_json_path(guild_id=guild_id,category="streamer"))
    data = BASE.dataload(path)

    # 英数字チェック
    if not re.fullmatch(r"[a-zA-Z0-9_]+", name):
        await ctx.respond("❌ `name` には英数字とアンダースコアのみ使用できます。", ephemeral=True)
        return

    if name in data:
        await ctx.respond(f"⚠️ ID `{name}` の情報を更新します", ephemeral=True)

    data[name] = {
        "display_name": display_name,
        "youtube_channel_id": youtube_channel_id,
        "twitch": twitch_username,
        "AT": []
    }

    BASE.datasave(data, path)
    await ctx.respond(f"✅ `{display_name}` を ID `{name}` として登録しました。", ephemeral=True)