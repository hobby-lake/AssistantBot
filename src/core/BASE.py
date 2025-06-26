"""BASE.py
>環境変数の定義
>JSONデータの読み書き
>データパスの生成
"""
from dotenv import load_dotenv
import os
import json
from pathlib import Path
from src.core import CONSOLE

# 環境変数の読み込み
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = [int(gid.strip()) for gid in os.getenv("DEBUG_GUILD_ID", "").split(",") if gid.strip()]
AUTHORIZED_USER_ID = int(os.getenv("DEV"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")

TWITCH_TOKEN_PATH = Path("data") / "api_data" / "TWITCH_TOKEN.json"

# 互換パスの生成
prefix = {
    "member":"MEM",
    "role":"ROL",
    "streamer":"STR",
    "event":"EVE",
    "report":"REP"
}

# JSONファイルのパスを取得
def get_json_path(guild_id: int, category: str) -> Path:
    return Path("data") / f"{category}_data" / f"{prefix[category]}{guild_id}.json"

# イベント管理用
def get_event_path(guild_id: int, category: str, status: str, event_id: str) -> Path:
    """イベント専用：scheduled/done ディレクトリにイベントID名のディレクトリを返す"""
    assert status in ("scheduled", "done"), f"status は 'scheduled' または 'done' である必要があります：{status}"
    return Path("data") / f"{category}_data" / str(guild_id) / status / f"{event_id}.json"

def datasave(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def dataload(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        CONSOLE.text(f"ファイルが見つかりません：{filename}\n処理をスキップします。", CONSOLE.WARN)
        return {}
    except json.JSONDecodeError:
        CONSOLE.text(f"デコードできませんでした：{filename}\n処理をスキップします。", CONSOLE.WARN)
        return {}
    
