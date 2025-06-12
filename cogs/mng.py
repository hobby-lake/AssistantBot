import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from discord import ApplicationContext
from src import JSON, COLOR, SECURE
import os
from dotenv import load_dotenv
from datetime import date
from cogs.ticket import TicketCreateButton

today = date.today()
load_dotenv()
DEV = int(os.getenv("DEV"))

class RoleSelect(discord.ui.Select):
    def __init__(self, roles):
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in roles
        ]
        super().__init__(placeholder="ロールを選択してください", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

class VoiceSelect(discord.ui.Select):
    def __init__(self, voice_channels):
        options = [
            discord.SelectOption(label=vc.name, value=str(vc.id))
            for vc in voice_channels
        ]
        super().__init__(placeholder="ボイスチャンネルを選択してください", min_values=1,
                         max_values=min(len(options), 25), options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

# /mng linkのUIとそのメインプロセス
class PaginatedLinkRoleVC_UI(discord.ui.View):
    def __init__(self, roles, categorized_vcs, current_page=0):
        super().__init__(timeout=300)
        self.roles = roles
        self.categorized_vcs = categorized_vcs  # List of tuples: (category_name, [VCs])
        self.current_page = current_page

        self.role_select = RoleSelect(self.roles)
        self.add_item(self.role_select)

        self.update_voice_select()

        self.add_item(self.PreviousPageButton())
        self.add_item(self.CategoryLabel(self.categorized_vcs[self.current_page][0]))
        self.add_item(self.NextPageButton())

        self.add_item(self.CompleteButton())

    def update_voice_select(self):
        category_name, vcs = self.categorized_vcs[self.current_page]
        self.voice_select = VoiceSelect(vcs)
        self.add_item(self.voice_select)

    class PreviousPageButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="← 前", style=discord.ButtonStyle.secondary, row=2)

        async def callback(self, interaction: discord.Interaction):
            view = self.view
            if view.current_page > 0:
                view.current_page -= 1
                await view.refresh(interaction)

    class NextPageButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="次 →", style=discord.ButtonStyle.secondary, row=2)

        async def callback(self, interaction: discord.Interaction):
            view = self.view
            if view.current_page < len(view.categorized_vcs) - 1:
                view.current_page += 1
                await view.refresh(interaction)

    class CategoryLabel(discord.ui.Button):
        def __init__(self, category_name):
            super().__init__(label=f"カテゴリ: {category_name}", disabled=True, style=discord.ButtonStyle.gray, row=2)

    class CompleteButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="完了", style=discord.ButtonStyle.success, row=4)

        async def callback(self, interaction: discord.Interaction):
            view = self.view
            selected_role_id = int(view.role_select.values[0])
            selected_voice_ids = [int(v) for v in view.voice_select.values]

            guild_id = interaction.guild.id
            data_path = f".\\data\\role_data\\L{guild_id}.json"
            if os.path.exists(data_path):
                data = JSON.load(data_path)
            else:
                data = {}

            data[str(selected_role_id)] = selected_voice_ids
            JSON.save(data, data_path)

            await interaction.response.send_message(
                f"ロール: <@&{selected_role_id}>\n"
                f"ボイスチャンネル: {', '.join(f'<#{vid}>' for vid in selected_voice_ids)}",
                ephemeral=True
            )
            COLOR.text(f"✅ リンク情報を `L{selected_role_id}.json` に保存しました！", COLOR.Log)
            view.stop()

    async def refresh(self, interaction: discord.Interaction):
        self.clear_items()
        self.__init__(self.roles, self.categorized_vcs, self.current_page)
        await interaction.response.edit_message(view=self)

class ManageGroup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_channels = {} 

    mng = SlashCommandGroup("mng", "管理者用初期設定コマンド")

    @mng.command(name="get_members", description="このサーバーのメンバー情報をJSONに保存します")
    async def get_members(self, ctx: ApplicationContext):
        await ctx.defer()
        if await SECURE.Restrict(ctx) == False:
            return
        
        guild = ctx.guild
        if not os.path.exists(f".\\data\\member_data\\M{guild.id}.json"):
            members_data = {}
            async for member in guild.fetch_members(limit=None):
                if not member.bot and members_data.get(member.id) != {}:
                    members_data[member.id] = {
                        "name": member.name,
                        "point": 0,
                        "last_updated": today.strftime("%Y-%m-%d")
                    }
                    
            JSON.save(members_data, f".\\data\\member_data\\M{guild.id}.json")

            COLOR.text(f"✅ {len(members_data)}人のメンバー情報を `M{guild.id}.json` に保存しました！", COLOR.Log)
            await ctx.respond(f"{len(members_data)}人のメンバー情報をあらたに作成しました！\n（実行者: {ctx.author.mention}）")
        else:
            await ctx.respond(f"❌ メンバー情報は既に存在します！")

    @mng.command(name="link", description="ロールとボイスチャンネルをカテゴリごとに紐づけ")
    async def link(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)
        guild = ctx.guild
        if await SECURE.Restrict(ctx) == False:
            return

        # 管理者ロールを除外
        roles = [
            role for role in guild.roles
            if not role.managed and not role.permissions.administrator
        ]

        # カテゴリごとにVCを分類
        vcs_by_category = {}
        for vc in guild.voice_channels:
            key = vc.category.name if vc.category else "カテゴリなし"
            vcs_by_category.setdefault(key, []).append(vc)

        categorized_vcs = list(vcs_by_category.items())

        if not roles or not categorized_vcs:
            await ctx.respond("⚠️ 利用可能なロールまたはボイスチャンネルが見つかりませんでした。", ephemeral=True)
            return

        view = PaginatedLinkRoleVC_UI(roles, categorized_vcs)
        await ctx.respond("ロールとボイスチャンネル（カテゴリごと）を選択してください：", view=view, ephemeral=True)

    @mng.command(name="set_ticket_channel", description="チケット作成用チャンネルを設定します。")
    async def set_ticket_channel(
        self,
        ctx: discord.ApplicationContext,
    ):
        await ctx.defer(ephemeral=True)

        ticket_cog = self.bot.get_cog("Ticket")
        if not ticket_cog:
            await ctx.respond("❌ Ticketモジュールが読み込まれていません。", ephemeral=True)
            return

        category = discord.utils.get(ctx.guild.categories, name="問い合わせフォーム")
        if category is None:
            category = await ctx.guild.create_category("問い合わせフォーム")
            channel = await ctx.guild.create_text_channel("チケットセンター",category=category,topic="問い合わせ用のチケットを発行するチャンネルです。")

            await channel.send(
                "🎫 管理者への問い合わせは以下のボタンからお願いします。\nチケットは管理者が「解決した」と判断した後に閉じます。\n閉じたチケットチャンネルはログとして別のカテゴリに移動させます。",
                view=TicketCreateButton()
            )
        else:
            await ctx.respond("既にチケットセンターが存在しています",ephemeral=True)

        await ctx.respond("チケットセンターの設置を完了しました", ephemeral=True)

def setup(bot):
    bot.add_cog(ManageGroup(bot))
    print(f"✅ {ManageGroup.__name__} loaded")