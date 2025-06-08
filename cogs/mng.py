import discord
from discord.ext import commands
from discord.commands import slash_command, SlashCommandGroup, Option
from discord import ApplicationContext
from src import JSON, COLOR
import os
from datetime import date

today = date.today()

class RoleSelect(discord.ui.Select):
    def __init__(self, roles):
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in roles if not role.managed
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
        super().__init__(placeholder="ボイスチャンネルを選択してください",
                         min_values=1,
                         max_values=len(voice_channels),
                         options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

# /mng linkのUIとそのメインプロセス
class LinkRoleVC_UI(discord.ui.View):
    def __init__(self, roles, voice_channels):
        super().__init__(timeout=300)

        self.role_select = RoleSelect(roles)
        self.voice_select = VoiceSelect(voice_channels)

        self.add_item(self.role_select)
        self.add_item(self.voice_select)

    @discord.ui.button(label="完了", style=discord.ButtonStyle.success)
    async def complete(self, button, interaction: discord.Interaction):
        selected_role_id = int(self.role_select.values[0])
        selected_voice_ids = [int(v) for v in self.voice_select.values]

        guild_id = interaction.guild.id

        data_path = f".\\data\\role_data\\L{guild_id}.json"
        if os.path.exists(data_path):
            output_data = JSON.load(data_path)
        else:
            output_data = {}
        output_data[str(selected_role_id)] = selected_voice_ids
        JSON.save(output_data,data_path)

        await interaction.response.send_message(
            f"ロール: <@&{selected_role_id}>\nボイスチャンネル: {', '.join(f'<#{vid}>' for vid in selected_voice_ids)}",
            ephemeral=True
        )
        COLOR.text(f"✅ リンク情報を `L{selected_role_id}.json` に保存しました！", COLOR.Log)
        self.stop()

class ManageGroup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    mng = SlashCommandGroup("mng", "管理者用初期設定コマンド")

    @mng.command(name="get_members", description="このサーバーのメンバー情報をJSONに保存します")
    async def get_members(self, ctx: ApplicationContext):
        await ctx.defer()
        if ctx.guild is None:
            await ctx.respond("このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
            return False
          
        guild = ctx.guild

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

    @mng.command(name="link", description="ロールとボイスチャンネルを紐づけ")
    async def link(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)
        guild = ctx.guild
        if guild is None:
            await ctx.respond("このコマンドはサーバー内でのみ使用できます。", ephemeral=True)
            return

        roles = guild.roles
        voice_channels = [vc for vc in guild.voice_channels]

        view = LinkRoleVC_UI(roles, voice_channels)
        await ctx.respond("紐づけるロールとボイスチャンネルを選択してください：", view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(ManageGroup(bot))
    print(f"✅ {ManageGroup.__name__} loaded")