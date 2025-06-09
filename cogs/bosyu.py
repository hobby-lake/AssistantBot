import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ui import Select
from discord import ApplicationContext
from src import JSON

# ゲーム選択セレクトメニュー
class GameSelectView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, roles, parent_view):
        super().__init__(timeout=300)
        self.parent_view = parent_view
        self.interaction = interaction
        self.roles = roles
        self.current_page = 0

        self.base_data = JSON.load(f".\\data\\role_data\\L{interaction.guild.id}.json")
        self.valid_role_ids = [str(rid) for rid in self.base_data.keys()]
        self.filtered_roles = [role for role in self.roles if str(role.id) in self.valid_role_ids and not role.managed]

        self.page_count = max(1, (len(self.filtered_roles) + 24) // 25)
        self.select_menu = self.create_select_menu()
        self.add_item(self.select_menu)

        if self.page_count > 1:
            self.add_item(PrevButton(self))
            self.add_item(NextButton(self))

    def create_select_menu(self):
        start = self.current_page * 25
        end = start + 25
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in self.filtered_roles[start:end]
        ]

        return GameSelect(options, self.parent_view)

    async def update_select(self, interaction):
        self.clear_items()
        self.select_menu = self.create_select_menu()
        self.add_item(self.select_menu)
        if self.page_count > 1:
            self.add_item(PrevButton(self))
            self.add_item(NextButton(self))
        await interaction.response.edit_message(view=self)

class GameSelect(discord.ui.Select):
    def __init__(self, options, parent_view):
        super().__init__(
            placeholder="ロールを選択してください（ページ対応）",
            min_values=1,
            max_values=1,
            options=options
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.parent_view.selected_role_id = int(self.values[0])
        await interaction.response.send_message("ロールを選択しました！", ephemeral=True)

class PrevButton(discord.ui.Button):
    def __init__(self, view: GameSelectView):
        super().__init__(label="<< 前", style=discord.ButtonStyle.secondary)
        self.view_ref = view

    async def callback(self, interaction: discord.Interaction):
        if self.view_ref.current_page > 0:
            self.view_ref.current_page -= 1
            await self.view_ref.update_select(interaction)

class NextButton(discord.ui.Button):
    def __init__(self, view: GameSelectView):
        super().__init__(label="次 >>", style=discord.ButtonStyle.secondary)
        self.view_ref = view

    async def callback(self, interaction: discord.Interaction):
        if self.view_ref.current_page < self.view_ref.page_count - 1:
            self.view_ref.current_page += 1
            await self.view_ref.update_select(interaction)

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
        self.owner_id = parent_interaction.user.id
        self.parent_interaction = parent_interaction

        self.role_select_view = GameSelectView(parent_interaction, roles, self)
        for item in self.role_select_view.children:
            self.add_item(item)

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