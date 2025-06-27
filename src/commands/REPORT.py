import discord
from src.core import BASE

class BugReportModal(discord.ui.Modal):
    subject = discord.ui.InputText(
        label="件名",
        style=discord.InputTextStyle.short,
        placeholder="不具合が起きたコマンドを教えてください。(10文字まで)",
        max_length=10,
        required=True
    )
    description = discord.ui.InputText(
        label="詳細",
        style=discord.InputTextStyle.long,
        placeholder="起こった不具合について詳しく教えてください。",
        required=True
    )

    def __init__(self):
        super().__init__(title="バグレポート")
        self.add_item(self.subject)
        self.subject.placeholder = "例: インタラクションに失敗しました。"
        self.add_item(self.description)
        self.description.placeholder = "例: /bosyu コマンドを実行した際に、インタラクションに失敗しました。と返されます。"

    async def callback(self, interaction: discord.Interaction):
        old_data = BASE.dataload(BASE.get_json_path(guild_id=interaction.guild_id, category="report"))
        
        if old_data:
            max_key = max(int(k) for k in old_data.keys())
            new_key = str(max_key + 1)
        else:
            new_key = "1"

        data = {
            new_key: {
                "type": "bug",
                "subject": self.subject.value,
                "description": self.description.value,
                "stats": "Scheduled",
            }
        }
        
        path = BASE.get_json_path(guild_id=interaction.guild_id, category="report")
        BASE.datasave(data, path)
        await interaction.response.send_message("ご協力ありがとうございます！", ephemeral=True)