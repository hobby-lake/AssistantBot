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