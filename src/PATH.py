# 互換パス生成
from pathlib import Path

prefix = {
    "member":"MEM",
    "role":"ROL",
    "streamer":"STR",
    "event":"EVE"
}

def get_json(guild_id: int, category: str) -> Path:
    return Path("data") / f"{category}_data" / f"{prefix[category]}{guild_id}.json"

# event.py専用
def get_event(guild_id: int, category: str, status: str, event_id: str) -> Path:
    """イベント専用：scheduled/done ディレクトリにイベントID名のディレクトリを返す"""
    assert status in ("scheduled", "done"), f"status は 'scheduled' または 'done' である必要があります：{status}"
    return Path("data") / f"{category}_data" / str(guild_id) / status / f"{event_id}.json"