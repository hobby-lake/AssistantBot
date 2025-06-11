import discord
from datetime import datetime

class Ticket(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketCreateButton())

    @discord.slash_command(name="ticket_close", description="チケットを閉じてアーカイブします")
    async def ticket_close(self, ctx: discord.ApplicationContext):
        channel = ctx.channel

        if not self.is_ticket_channel(channel.name):
            await ctx.respond("このチャンネルはチケットではありません。", ephemeral=True)
            return

        archive_category = await self.get_or_create_category(ctx.guild, "アーカイブ")

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        await channel.edit(category=archive_category, overwrites=overwrites)
        await ctx.respond(f"{channel.mention} をアーカイブしました。閲覧のみ可能です。")

    @staticmethod
    def is_ticket_channel(name: str) -> bool:
        return name.startswith("ticket-")

    async def get_or_create_category(self, guild, name):
        category = discord.utils.get(guild.categories, name=name)
        return category or await guild.create_category(name)

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
            topic=f"{user} さんのチケット（Botによって作成）"
        )

        await ticket_channel.send(
            f"{datetime.now()}\n{user.mention} さんのチケットを作成しました。サポートまでお待ちください。",
            view=TicketCloseButton()
        )

        await interaction.response.send_message(
            f"チケットを作成しました: {ticket_channel.mention}",
            ephemeral=True
        )

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

        await channel.edit(category=archive_category)

        # 👇 書き込み権限だけを剥奪（閲覧は変更しない）
        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = False  # 書き込み禁止
        # view_channel は None のまま（変更しない）
        await channel.set_permissions(guild.default_role, overwrite=overwrite)

        await interaction.response.send_message(
            f"{channel.mention} をアーカイブしました。閲覧のみ可能です。\n実行者：{interaction.user.mention}",
            ephemeral=False
        )

def setup(bot: discord.Bot):
    bot.add_cog(Ticket(bot))
    print("✅ Ticket loaded")