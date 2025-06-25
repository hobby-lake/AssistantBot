import discord
from cogs import ticket
from datetime import datetime
import re

async def set(ctx: discord.ApplicationContext):
    await ctx.defer(ephemeral=True)

    category = discord.utils.get(ctx.guild.categories, name="問い合わせフォーム")
    if category is None:
        category = await ctx.guild.create_category("問い合わせフォーム")
        channel = await ctx.guild.create_text_channel("チケットセンター",category=category,topic="問い合わせ用のチケットを発行するチャンネルです。")

        await channel.send(
            "🎫 管理者への問い合わせは以下のボタンからお願いします。\nチケットは管理者が「解決した」と判断した後に閉じます。\n閉じたチケットチャンネルはログとして別のカテゴリに移動させます。",
            view=CreateButton()
        )
    else:
        await ctx.respond("既にチケットセンターが存在しています",ephemeral=True)

    await ctx.respond("チケットセンターの設置を完了しました", ephemeral=False)

# チケット作成ボタン
class CreateButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 チケットを作成", style=discord.ButtonStyle.primary, custom_id="ticket_create_button")
    async def create(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        category = discord.utils.get(guild.categories, name="問い合わせフォーム")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        now_str = datetime.now().strftime("%Y%m%d%H%M%S")
        ticket_channel = await guild.create_text_channel(
            f"ticket-{user.name}-{now_str}",
            category=category,
            overwrites=overwrites,
            topic=f"{user} さんのチケット（Botによって作成） user_id:{user.id}"
        )

        await ticket_channel.send(
            f"{datetime.now()}\n{user.mention} さんのチケットを作成しました。サポートまでお待ちください。",
            view=CloseButton()
        )

        await interaction.response.send_message(
            f"チケットを作成しました: {ticket_channel.mention}",
            ephemeral=True
        )

# チケットを閉じるボタン
class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❌ チケットを閉じる", style=discord.ButtonStyle.danger, custom_id="ticket_close_button")
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = interaction.channel
        guild = interaction.guild

        if not channel.name.startswith("ticket-"):
            await interaction.response.send_message(
                "このチャンネルではチケットを閉じることはできません。",
                ephemeral=True
            )
            return

        archive_category = discord.utils.get(guild.categories, name="アーカイブ")
        if not archive_category:
            archive_category = await guild.create_category("アーカイブ")

        match = re.search(r"user_id:(\d+)", channel.topic or "")
        ticket_owner = guild.get_member(int(match.group(1))) if match else None

        await channel.edit(category=archive_category)

        await channel.set_permissions(guild.default_role, read_messages=False, send_messages=False)

        if ticket_owner:
            await channel.set_permissions(ticket_owner, read_messages=True, send_messages=False)

        await interaction.response.send_message(
            f"{channel.mention} をアーカイブしました（閲覧のみ可能）。\n実行者：{interaction.user.mention}",
            ephemeral=False
        )