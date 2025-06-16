import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
from discord import ApplicationContext
from src import JSON, PATH
import datetime

class BasicInfoModal(discord.ui.Modal):
    def __init__(self, bot, author: discord.Member):
        super().__init__(title="イベント基本情報")
        self.bot = bot
        self.author = author

        self.name = discord.ui.InputText(label="イベント名", placeholder="例: ギルド大会", required=True)
        self.date = discord.ui.InputText(label="開催日 (YYYY-MM-DD)", placeholder="2025-06-20", required=True)
        self.time = discord.ui.InputText(label="開始時刻 (HH:MM 24h)", placeholder="20:00", required=True)
        self.location = discord.ui.InputText(label="開催場所", placeholder="ボイスチャンネル名など", required=True)

        self.add_item(self.name)
        self.add_item(self.date)
        self.add_item(self.time)
        self.add_item(self.location)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            print("✅ on_submit called")  # デバッグ用
            await interaction.response.send_message("✅ モーダル送信を受け取りました", ephemeral=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                await interaction.response.send_message(
                    f"⚠️ エラーが発生しました: `{e}`", ephemeral=True
                )
            except discord.InteractionResponded:
                await interaction.followup.send(
                    f"⚠️ フォローアップエラー: `{e}`", ephemeral=True
                )

class PointsInfoModal(discord.ui.Modal):
    def __init__(self, bot, author: discord.Member):
        super().__init__(title="付与ポイント情報 (任意)")
        self.bot = bot
        self.author = author

        self.reward = discord.ui.InputText(label="参加賞ポイント", placeholder="例: 10", required=False)
        self.top_points = discord.ui.InputText(label="首位ポイント", placeholder="例: 100", required=False)
        self.offset = discord.ui.InputText(label="順位ごとの差分", placeholder="例: 10", required=False)
        self.cutoff = discord.ui.InputText(label="ポイント足切り", placeholder="例: 30", required=False)
        
        self.add_item(self.reward)
        self.add_item(self.top_points)
        self.add_item(self.offset)
        self.add_item(self.cutoff)

    async def on_submit(self, interaction: discord.Interaction):
        # 基本情報取得
        info = getattr(interaction.client, "_temp_event_info", None)
        if not info or info["author"].id != self.author.id:
            await interaction.response.send_message("エラー: 基本情報が見つかりません。もう一度やり直してください。", ephemeral=True)
            return
        
        # デフォルト値や型変換を試みる
        def to_int_or_zero(value):
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0
        
        reward = to_int_or_zero(self.reward.value)
        top_points = to_int_or_zero(self.top_points.value)
        offset = to_int_or_zero(self.offset.value)
        cutoff = to_int_or_zero(self.cutoff.value)

        guild = interaction.guild
        author = info["author"]
        start = info["start"]
        end = info["end"]

        # Discordのイベント作成
        event = await guild.create_scheduled_event(
            name=info["name"],
            start_time=start,
            end_time=end,
            description=f"開催者: {author.display_name}",
            location=info["location"]
        )
        event_id = str(event.id)
        guild_id = str(guild.id)

        # ファイル準備
        event_file = PATH.get_event(guild_id, "event", "scheduled", event_id)
        index_file = PATH.get_event(guild_id, "event", "scheduled", "index")
        event_file.parent.mkdir(parents=True, exist_ok=True)
        index_file.parent.mkdir(parents=True, exist_ok=True)

        # index更新
        index = JSON.load(index_file)
        index[event_id] = {
            "name": info["name"],
            "開催者": author.id,
            "開始": start.isoformat()
        }
        JSON.save(index, index_file)

        # イベント詳細保存
        event_data = {
            "開催者": author.id,
            "名称": info["name"],
            "日程": [info["date"], info["time"]],
            "開催場所": info["location"],
            "参加賞": reward,
            "付与ポイント": {
                "首位": top_points,
                "オフセット": offset,
                "足切り": cutoff
            }
        }
        JSON.save(event_data, event_file)

        # 一時保存データクリア
        delattr(interaction.client, "_temp_event_info")

        await interaction.response.send_message(f"✅ イベント `{info['name']}` を作成しました！", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("❌ イベント作成中にエラーが発生しました。", ephemeral=True)


class EventManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    event = SlashCommandGroup("event", "イベント管理コマンド")

    @event.command(name="create", description="新しいDiscordイベントを作成します")
    async def create(self, ctx: ApplicationContext):
        modal = BasicInfoModal(bot=self.bot, author=ctx.author)
        await ctx.send_modal(modal)

    # 省略： end コマンドは以前のままでOK


def setup(bot):
    bot.add_cog(EventManager(bot))
    print(f"✅ {EventManager.__name__} loaded")