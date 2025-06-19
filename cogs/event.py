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

    async def callback(self, interaction: discord.Interaction):
        try:
            info = {
                "author": self.author,
                "name": self.name.value,
                "date": self.date.value,
                "time": self.time.value,
                "location": self.location.value,
                "start": datetime.datetime.strptime(f"{self.date.value} {self.time.value}", "%Y-%m-%d %H:%M"),
                "end": None
            }

            # 一時保存（必要ならここで interaction.client に保存しても良い）
            view = ProceedView(bot=self.bot, author=self.author, base_info=info)
            await interaction.response.send_message(
                "✅ 基本情報を受け取りました。\n続けて「付与ポイント」の設定を行うには下のボタンを押してください。",
                ephemeral=True,
                view=view
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(f"エラーが発生しました: `{e}`", ephemeral=True)


class PointsInfoModal(discord.ui.Modal):
    def __init__(self, bot, author: discord.Member, base_info):
        super().__init__(title="付与ポイント情報 (任意)")
        self.bot = bot
        self.author = author

        self.base_info = base_info

        self.reward = discord.ui.InputText(label="参加賞ポイント", placeholder="例: 10", required=False)
        self.top_points = discord.ui.InputText(label="首位ポイント", placeholder="例: 100", required=False)
        self.offset = discord.ui.InputText(label="順位ごとの差分", placeholder="例: 10", required=False)
        self.cutoff = discord.ui.InputText(label="ポイント足切り", placeholder="例: 30", required=False)
        
        self.add_item(self.reward)
        self.add_item(self.top_points)
        self.add_item(self.offset)
        self.add_item(self.cutoff)

    async def callback(self, interaction: discord.Interaction):
        if not self.base_info or self.base_info["author"].id != self.author.id:
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
        author = self.base_info["author"]
        start = self.base_info["start"]
        end = self.base_info["end"]

        # Discordのイベント作成
        event = await guild.create_scheduled_event(
            name=self.base_info["name"],
            start_time=start,
            end_time=end,
            description=f"開催者: {author.display_name}",
            location=self.base_info["location"]
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
            "name": self.base_info["name"],
            "開催者": author.id,
            "開始": start.isoformat()
        }
        JSON.save(index, index_file)

        # イベント詳細保存
        event_data = {
            "開催者": author.id,
            "名称": self.base_info["name"],
            "日程": [self.base_info["date"], self.base_info["time"]],
            "開催場所": self.base_info["location"],
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

        await interaction.response.send_message(f"✅ イベント `{self.base_info['name']}` を作成しました！", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("❌ イベント作成中にエラーが発生しました。", ephemeral=True)

class ProceedView(discord.ui.View):
    def __init__(self, bot, author, base_info):
        super().__init__(timeout=300)
        self.bot = bot
        self.author = author
        self.base_info = base_info

    @discord.ui.button(label="次へ", style=discord.ButtonStyle.primary)
    async def proceed_button(self, button, interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("このボタンはあなたのものではありません。", ephemeral=True)
            return
        await interaction.response.send_modal(
            PointsInfoModal(bot=self.bot, author=self.author, base_info=self.base_info)
        )

class EventManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    event = SlashCommandGroup("event", "イベント管理コマンド")

    @event.command(name="create", description="新しいDiscordイベントを作成します")
    async def create(self, ctx: ApplicationContext):
        modal = BasicInfoModal(bot=self.bot, author=ctx.author)
        await ctx.send_modal(modal)

def setup(bot):
    bot.add_cog(EventManager(bot))
    print(f"✅ {EventManager.__name__} loaded")