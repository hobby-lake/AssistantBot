import discord
from datetime import datetime
import re

# チケット機能の根幹
class Ticket(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketCreateButton())

    @staticmethod
    def is_ticket_channel(name: str) -> bool:
        return name.startswith("ticket-")

    async def get_or_create_category(self, guild, name):
        category = discord.utils.get(guild.categories, name=name)
        return category or await guild.create_category(name)

# チケット作成ボタン
class TicketCreateButton(discord.ui.View):
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
            view=TicketCloseButton()
        )

        await interaction.response.send_message(
            f"チケットを作成しました: {ticket_channel.mention}",
            ephemeral=True
        )

# チケットを閉じるボタン
class TicketCloseButton(discord.ui.View):
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

def setup(bot: discord.Bot):
    bot.add_cog(Ticket(bot))
    print("✅ Ticket loaded")