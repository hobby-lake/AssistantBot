import discord
from discord.ext import commands
from discord.commands import slash_command
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
        return GameSelect(options=options, parent_bosyu_view=self.parent_view)

    async def update_select(self, interaction):
        self.clear_items()
        self.select_menu = self.create_select_menu()
        self.add_item(self.select_menu)
        if self.page_count > 1:
            self.add_item(PrevButton(self))
            self.add_item(NextButton(self))
        await interaction.response.edit_message(view=self)

class GameSelect(discord.ui.Select):
    def __init__(self, options, parent_bosyu_view):
        super().__init__(
            placeholder="ロールを選択してください（ページ対応）",
            min_values=1,
            max_values=1,
            options=options
        )
        self.parent_bosyu_view = parent_bosyu_view

    async def callback(self, interaction: discord.Interaction):
        self.parent_bosyu_view.selected_role_id = int(self.values[0])
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
    def __init__(self, interaction: discord.Interaction, roles):
        super().__init__(timeout=300)
        self.interaction = interaction
        self.roles = roles

        self.selected_role_id = None
        self.人数 = None
        self.詳細 = None
        self.remaining = None
        self.owner_id = interaction.user.id

        self.role_select_view = GameSelectView(interaction, roles, self)
        for item in self.role_select_view.children:
            self.add_item(item)

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

        if not self.selected_role_id:
            await interaction.response.send_message("ロールが選択されていません。", ephemeral=True)
            return

        view = ParticipationView(self)

        embed = discord.Embed(
            title="🎮 募集中",
            description=f"{interaction.user.mention}が<@&{self.selected_role_id}> の募集を開始しました！",
            color=discord.Color.blue()
        )
        embed.add_field(name="👥 募集人数", value=f"0/{self.人数}人", inline=False)
        embed.add_field(name="✅ 参加者", value="なし", inline=False)
        embed.add_field(name="👀 観戦者", value="なし", inline=False)
        embed.add_field(name="📝 詳細", value=self.詳細 or "なし", inline=False)

        await interaction.response.send_message(embed=embed, view=view, allowed_mentions=discord.AllowedMentions(roles=True))
        view.message = await interaction.original_response()
        self.stop()

class ParticipationView(discord.ui.View):
    def __init__(self, bosyu_view: BosyuUI):
        super().__init__(timeout=None)
        self.bosyu_view = bosyu_view
        self.joined_users = {}
        self.watching_users = {}
        self.message = None

    async def update_embed(self):
        embed = discord.Embed(
            title="🎮 募集中",
            description=f"<@&{self.bosyu_view.selected_role_id}> の募集が行われています！",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="👥 募集人数",
            value=f"{len(self.joined_users)}/{int(self.bosyu_view.人数)}人",
            inline=False
        )
        embed.add_field(
            name="✅ 参加者",
            value="\n".join(self.joined_users.values()) or "なし",
            inline=False
        )
        embed.add_field(
            name="👀 観戦者",
            value="\n".join(self.watching_users.values()) or "なし",
            inline=False
        )
        embed.add_field(
            name="📝 詳細",
            value=self.bosyu_view.詳細 or "なし",
            inline=False
        )
        await self.message.edit(embed=embed, view=self)

    @discord.ui.button(label="参加する", style=discord.ButtonStyle.primary)
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id == self.bosyu_view.owner_id:
            await interaction.response.send_message("募集者は参加できません。", ephemeral=True)
            return
        if user_id in self.joined_users:
            await interaction.response.send_message("すでに参加しています。", ephemeral=True)
            return
        if user_id in self.watching_users:
            await interaction.response.send_message("観戦と参加は同時にできません。", ephemeral=True)
            return

        self.joined_users[user_id] = interaction.user.mention
        self.bosyu_view.remaining -= 1

        await interaction.response.send_message("参加しました！", ephemeral=True)
        await self.update_embed()

        if self.bosyu_view.remaining <= 0:
            button.disabled = True
            await self.update_embed()

    @discord.ui.button(label="観戦する", style=discord.ButtonStyle.secondary)
    async def watch(self, button: discord.ui.Button, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id == self.bosyu_view.owner_id:
            await interaction.response.send_message("募集者は観戦できません。", ephemeral=True)
            return
        if user_id in self.watching_users:
            await interaction.response.send_message("すでに観戦しています。", ephemeral=True)
            return
        if user_id in self.joined_users:
            await interaction.response.send_message("観戦と参加は同時にできません。", ephemeral=True)
            return

        self.watching_users[user_id] = interaction.user.mention
        await interaction.response.send_message("観戦希望として登録しました。", ephemeral=True)
        await self.update_embed()

    @discord.ui.button(label="募集終了", style=discord.ButtonStyle.danger)
    async def end(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.bosyu_view.owner_id:
            await interaction.response.send_message("このボタンは募集者のみが使用できます。", ephemeral=True)
            return

        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.label == "参加する":
                child.disabled = True

        embed = discord.Embed(
            title="🛑 募集終了",
            description=f"<@&{self.bosyu_view.selected_role_id}> の募集が終了されました。",
            color=discord.Color.red()
        )
        embed.add_field(name="👥 参加者", value="\n".join(self.joined_users.values()) or "なし", inline=False)
        embed.add_field(name="👀 観戦者", value="\n".join(self.watching_users.values()) or "なし", inline=False)
        embed.add_field(name="📝 詳細", value=self.bosyu_view.詳細 or "なし", inline=False)

        await self.message.edit(embed=embed, view=self)
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

        view = BosyuUI(interaction=ctx.interaction, roles=guild.roles)
        await ctx.respond("募集内容を入力してください：", view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(BosyuCog(bot))
    print(f"✅ {BosyuCog.__name__} loaded")