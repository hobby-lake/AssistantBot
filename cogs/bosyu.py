import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ui import Modal, InputText, Button, View, Select
from discord.enums import InputTextStyle
from discord import ApplicationContext
from src import JSON, COLOR

# ゲーム選択セレクトメニュー
class GameSelect(Select):
    def __init__(self, interaction: discord.Interaction, roles, parent_view):
        self.parent_view = parent_view

        base_data = JSON.load(f".\\data\\role_data\\L{interaction.guild.id}.json")
        valid_role_ids = set(base_data.keys())

        matched_roles = [
            role for role in roles
            if str(role.id) in valid_role_ids and not role.managed
        ]

        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in matched_roles
        ]

        super().__init__(
            placeholder="ロールを選択してください",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.selected_role_id = int(self.values[0])
        await interaction.response.defer()

# モーダル
class BosyuModal(discord.ui.Modal):
    def __init__(self, parent_view):
        super().__init__(title="募集内容入力")
        self.parent_view = parent_view

        self.add_item(discord.ui.InputText(label="人数", placeholder="例: 4"))
        self.add_item(discord.ui.InputText(label="詳細", style=discord.InputTextStyle.long, required=False))

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.人数 = self.children[0].value
        self.parent_view.詳細 = self.children[1].value
        await interaction.response.send_message("内容を保存しました。完了ボタンを押してください。", ephemeral=True)

# UIビュー
class BosyuUI(discord.ui.View):
    def __init__(self, roles, parent_interaction: discord.Interaction):
        super().__init__(timeout=300)
        self.selected_role_id = None
        self.人数 = None
        self.詳細 = None
        self.remaining = None
        self.owner_id = parent_interaction.user.id  # 募集者のIDを記録
        self.parent_interaction = parent_interaction

        self.add_item(GameSelect(parent_interaction, roles, self))

    @discord.ui.button(label="詳細を入力", style=discord.ButtonStyle.primary)
    async def open_modal(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(BosyuModal(self))

    @discord.ui.button(label="完了", style=discord.ButtonStyle.success)
    async def complete(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            self.remaining = int(self.人数)
        except ValueError:
            await interaction.response.send_message("人数の入力が不正です。数字を入力してください。", ephemeral=True)
            return

        msg = (
            f"🎮 <@&{self.selected_role_id}> を募集中です！\n"
            f"👥 @{self.人数}人 お待ちしてます！\n"
            f"📝 募集詳細：{self.詳細 or 'なし'}"
        )
        await interaction.response.send_message(msg, view=ParticipationView(self), ephemeral=False)
        self.stop()


# 参加/観戦/終了用の別ビュー
class ParticipationView(discord.ui.View):
    def __init__(self, bosyu_view: BosyuUI):
        super().__init__(timeout=None)
        self.bosyu_view = bosyu_view

    @discord.ui.button(label="参加する", style=discord.ButtonStyle.primary)
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.bosyu_view.remaining is None:
            await interaction.response.send_message("募集人数が設定されていません。", ephemeral=True)
            return

        self.bosyu_view.remaining -= 1
        await interaction.response.send_message(f"{interaction.user.mention} が参加しました！（残り: {self.bosyu_view.remaining}人）", ephemeral=False)

        if self.bosyu_view.remaining <= 0:
            for child in self.children:
                if isinstance(child, discord.ui.Button) and child.label in ["参加する", "観戦する"]:
                    child.disabled = True
            await interaction.message.edit(content="✅ 募集は終了しました！", view=self)

    @discord.ui.button(label="観戦する", style=discord.ButtonStyle.secondary)
    async def watch(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(f"{interaction.user.mention} が観戦希望です！", ephemeral=False)

    @discord.ui.button(label="募集終了", style=discord.ButtonStyle.danger)
    async def end(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.bosyu_view.owner_id:
            await interaction.response.send_message("このボタンは募集者のみ使用できます。", ephemeral=True)
            return

        for child in self.children:
            child.disabled = True
        await interaction.message.edit(content="🛑 募集は募集者によって終了されました。", view=self)
        await interaction.response.send_message("募集を終了しました。", ephemeral=True)

# コグ本体
class BosyuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="bosyu", description="任意のゲームで募集をかけます")
    async def bosyu(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)
        guild = ctx.guild
        if guild is None:
            await ctx.respond("このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
            return

        view = BosyuUI(roles=guild.roles, parent_interaction=ctx.interaction)
        await ctx.respond("募集内容を入力してください：", view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(BosyuCog(bot))
    print(f"✅ {BosyuCog.__name__} loaded")