import json
from src import COLOR

def save(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        COLOR.text(f"ファイルが見つかりません：{filename}\n新規作成します。", COLOR.WARN)
        return {}
    except json.JSONDecodeError:
        COLOR.text(f"デコードできませんでした：{filename}\n空の辞書を出力します。", COLOR.WARN)
        return {}