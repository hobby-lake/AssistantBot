import discord
from datetime import datetime
from src.core import BASE, CONSOLE

def get_data(guild_id: int = 0):
    path = BASE.get_json_path(guild_id=guild_id, category="report")
    data = BASE.dataload(path)
    if data == {}:
        return ["┣ ありません。"] * 6
    amount_data = max(int(k) for k in data.keys())
    
    debug_scheduled         = ""
    debug_in_progress       = ""
    debug_solved            = ""

    impriment_scheduled     = ""
    impriment_in_progress   = ""
    impriment_solved        = ""

    for key in range(1, amount_data + 1):
        str_key = str(key)
        if data[str_key]["type"]    == "bug":
            if data[str_key]["stats"]   == "Scheduled":
                debug_scheduled         = debug_scheduled + f"┣ {data[str_key]['subject']}\n"
            elif data[str_key]["stats"] == "InProgress":
                debug_in_progress       = debug_in_progress + f"┣ {data[str_key]['subject']}\n"
            elif data[str_key]["stats"] == "Solved":
                debug_solved            = debug_solved + f"┣ {data[str_key]['subject']}\n"
        elif data[str_key]["type"]  == "impriment":
            if data[str_key]["stats"]   == "Scheduled":
                impriment_scheduled     = impriment_scheduled + f"┣ {data[str_key]['subject']}\n"
            elif data[str_key]["stats"] == "InProgress":
                impriment_in_progress   = impriment_in_progress + f"┣ {data[str_key]['subject']}\n"
            elif data[str_key]["stats"] == "Solved":
                impriment_solved        = impriment_solved + f"┣ {data[str_key]['subject']}\n"

    results = [debug_scheduled, debug_in_progress, debug_solved,
              impriment_scheduled, impriment_in_progress, impriment_solved]
    
    for index, result in enumerate(results):
        if result == "":
            results[index] = "┣ ありません。"
        results[index] = results[index] + f"┗━━━━━━━━━━━━━━━━━━━━"
        CONSOLE.text(f"No.{index+1} Loaded", CONSOLE.Data)

    return results

async def set_embed(data):
    progress = discord.Embed(
        title="🛠 開発状況について",
        description="現在の開発・調整・修正状況を表示します。",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    progress.add_field(name="__バグの修正__",
                        value="┣ **対応予定**\n" \
                        f"{data[0]}\n" \
                        "┣ **対応中**\n" \
                        f"{data[1]}\n" \
                        "┣ **経過観察中**\n" \
                        f"{data[2]}\n",
                        inline=True)
    progress.add_field(name="__新機能の実装__",
                        value="┣ **実装予定**\n" \
                        f"{data[3]}\n" \
                        "┣ **実装中**\n" \
                        f"{data[4]}\n" \
                        "┣ **調整中**\n" \
                        f"{data[5]}\n",
                        inline=True)
    progress.set_footer(text="処置が完了した個所は一覧から削除されます。\n2時間に1度更新されます。")

    return progress