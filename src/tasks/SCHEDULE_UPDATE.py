from src.core import BASE, CONSOLE, API
from src.commands import SCHEDULE
import discord

async def run(self):
    """定期的に配信者のカレンダーを更新するタスク"""
    for guild_id in self.bot.guild_ids:
        path = str(BASE.get_json_path(guild_id=guild_id, category="streamer"))
    config = BASE.dataload(path)

    for name, data in config.items():
        if "AT" not in data or len(data["AT"]) < 2:
            continue

        # スケジュール取得
        if "youtube_channel_id" in data:
            schedule = API.YouTubeAPI.get_schedule(data["youtube_channel_id"])
        else:
            CONSOLE.text(f"[ERROR]ChannelIDが無効か正しくありません。", CONSOLE.Error)
            return

        embed = SCHEDULE.build_schedule_embed(
            guild_id=guild_id,
            streamer_id=name,
            schedule_list=schedule
        )

        channel_id = data["AT"][1]
        channel = self.bot.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            continue

        try:
            msg_id = data.get("calendar_message_id")
            if msg_id:
                message = await channel.fetch_message(msg_id)
                await message.edit(embed=embed)
            else:
                message = await channel.send(embed=embed)
                data["calendar_message_id"] = message.id  # 初回のみ保存
        except discord.NotFound:
            # メッセージが存在しない場合、新規送信してID保存
            message = await channel.send(embed=embed)
            data["calendar_message_id"] = message.id
        except Exception as e:
            print(f"⚠️ カレンダー更新失敗: {name} in {guild_id} => {e}")

    BASE.datasave(config, path)
    CONSOLE.text("✅ 配信者のカレンダーを更新しました。", CONSOLE.Log)