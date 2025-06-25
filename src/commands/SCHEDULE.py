import requests
from datetime import datetime
import discord
from src.core import API, BASE, CONSOLE

def get_combined_schedule(streamer_config, twitch_token):
    result = []

    if "youtube" in streamer_config:
        result += API.YouTubeAPI.get_schedule(streamer_config["youtube"])

    if "twitch" in streamer_config:
        try:
            broadcaster_id = API.TwitchAPI.get_broadcaster_id(
                username=streamer_config["twitch"],
                access_token=twitch_token,
            )
            result += API.TwitchAPI.get_schedule(
                broadcaster_id=broadcaster_id,
                access_token=twitch_token
            )
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                # スケジュールなし→無視
                pass
            else:
                raise

    return sorted(result, key=lambda x: x["date"])

def build_schedule_embed(guild_id: int, streamer_id, schedule_list):
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]

    now = datetime.now()
    this_month = []
    next_month = []
    future = []

    for item in schedule_list:
        d = item["date"]
        formatted = f"{d.strftime('%m/%d')} ({weekdays[d.weekday()]}) {item['title']}"

        if d.year == now.year and d.month == now.month:
            this_month.append(formatted)
        elif d.year == now.year and d.month == (now.month % 12) + 1:
            next_month.append(formatted)
        else:
            future.append(formatted)

    # 配信者の表示名取得
    path = BASE.get_json_path(guild_id, "streamer")
    streamer_data = BASE.dataload(path)
    streamer_name = streamer_data[streamer_id]["display_name"]

    embed = discord.Embed(title=f"📅 {streamer_name}の配信予定", color=0x00aaff)

    if this_month:
        embed.add_field(name=f"{now.month}月の予定", value="\n".join(this_month), inline=False)
    if next_month:
        embed.add_field(name=f"{(now.month % 12) + 1}月の予定", value="\n".join(next_month), inline=False)
    if future:
        embed.add_field(name="以降の予定", value="\n".join(future), inline=False)

    embed.set_footer(text="毎時自動更新されます")
    return embed

async def initialize(ctx, name, channel):
    guild_id = ctx.guild.id
    path = str(BASE.get_json_path(guild_id=guild_id, category="streamer"))
    config = BASE.dataload(path)

    if name not in config:
        await ctx.respond(f"❌ 登録id `{name}` は存在しません。", ephemeral=True)
        return

    # スケジュール取得
    channel_id = config[name].get("youtube_channel_id")
    if channel_id:
        schedule = API.YouTubeAPI.get_schedule(channel_id=channel_id)
    else:
        CONSOLE.text(f"[ERROR]ChannelIDが無効か正しくありません。", CONSOLE.Error)
        return

    # Embed 作成
    embed = build_schedule_embed(
        guild_id=guild_id,
        streamer_id=name,
        schedule_list=schedule
    )

    # メッセージ送信
    msg_id = config[name].get("calendar_message_id")
    try:
        if msg_id:
            old_msg = await channel.fetch_message(msg_id)
            await old_msg.edit(embed=embed)
            msg = old_msg
        else:
            msg = await channel.send(embed=embed)
            config[name]["calendar_message_id"] = msg.id
    except discord.NotFound:
        msg = await channel.send(embed=embed)
        config[name]["calendar_message_id"] = msg.id

    config[name]["AT"] = [ctx.author.id, channel.id]  # 必要に応じて変更

    BASE.datasave(config, path)

    await ctx.respond(f"✅ `{name}` のカレンダーを {channel.mention} に設置しました。", ephemeral=True)
    CONSOLE.text(f"✅ `{name}` のカレンダーを {channel.mention} に設置しました。", CONSOLE.Log)
    CONSOLE.text(f"カレンダーのメッセージID: {msg.id}\nカレンダーのチャンネルID: {channel.id}\nカレンダーの登録者ID: {ctx.author.id}", CONSOLE.Data)