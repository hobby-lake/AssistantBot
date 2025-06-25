from discord import ApplicationContext
from src.core import BASE, CONSOLE, SECURITY
import os
from datetime import date

today = date.today()

async def run(self, ctx: ApplicationContext):
    await ctx.defer()
    if await SECURITY.Restrict(ctx) == False:
        return
    
    guild = ctx.guild
    save_path = str(BASE.get_json_path(guild_id=guild.id,category="member"))
    if not os.path.exists(save_path):
        members_data = {}
    else:
        members_data = BASE.dataload(save_path)

    async for member in guild.fetch_members(limit=None):
        if not member.bot:
            if str(member.id) not in members_data:
                # 新規登録
                members_data[str(member.id)] = {
                    "name": member.name,
                    "point": 0,
                    "last_updated": today.strftime("%Y-%m-%d")
                }
                CONSOLE.text(f"{member.name} ({str(member.id)}) の情報を記録しました。", CONSOLE.Data)
            else:
                try:
                    member_data = members_data[str(member.id)]
                    if member_data.get("name") != member.name:
                        member_data["name"] = member.name
                        member_data["last_updated"] = today.strftime("%Y-%m-%d")
                        CONSOLE.text(f"{member.display_name} の名前を更新しました。", CONSOLE.WARN)
                except Exception as e:
                    # データが壊れている場合、最小限の値を保持して修復
                    old_point = members_data.get(str(member.id), {}).get("point", 0)
                    members_data[str(member.id)] = {
                        "name": member.name,
                        "point": old_point,
                        "last_updated": today.strftime("%Y-%m-%d")
                    }
                    CONSOLE.text(f"{member.name} のデータが壊れていたため修復しました。", CONSOLE.WARN)

    BASE.datasave(members_data, save_path)

    added = sum(1 for m_id in members_data if "point" not in members_data[m_id])

    CONSOLE.text(f"✅ {len(members_data)}人のメンバー情報を `MEM{guild.id}.json` に保存しました！", CONSOLE.Log)
    await ctx.respond(
        f"✅ メンバー情報を更新しました！\n"
        f"・新規追加: {added}人\n"
        f"・合計記録人数: {len(members_data)}人\n"
        f"（実行者: {ctx.author.mention}）"
    )