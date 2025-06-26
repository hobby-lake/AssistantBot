import discord
from src.core import BASE

class BugReportModal(discord.ui.Modal):
    subject = discord.ui.InputText(
        label="件名",
        style=discord.InputTextStyle.short,
        placeholder="バグの簡単な説明を入力してください。",
        required=True,
    )
    description = discord.ui.InputText(
        label="詳細",
        style=discord.InputTextStyle.long,
        placeholder="起こった不具合について詳しく教えてください。",
        required=True,
    )

    def __init__(self):
        super().__init__(title="バグレポート")
        self.add_item(self.subject)
        self.subject.placeholder = "例: インタラクションに失敗しました。"
        self.add_item(self.description)
        self.description.placeholder = "例: /bosyu コマンドを実行した際に、インタラクションに失敗しました。と返されます。"

    async def callback(self, interaction: discord.Interaction):
        data = {
            "subject": self.subject.value,
            "description": self.description.value,
        }
        path = BASE.get_json_path(guild_id=interaction.guild_id, category="report")
        BASE.datasave(data, path)
        await interaction.response.send_message("ご協力ありがとうございます！", ephemeral=True)