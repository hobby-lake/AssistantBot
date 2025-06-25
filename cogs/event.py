from discord.ext import commands
from discord.commands import SlashCommandGroup
from discord import ApplicationContext
from src.commands import EVENT

class EventManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    event = SlashCommandGroup("event", "イベント管理コマンド")

    @event.command(name="create", description="新しいDiscordイベントを作成します")
    async def create(self, ctx: ApplicationContext):
        modal = EVENT.BasicInfoModal(bot=self.bot, author=ctx.author)
        await ctx.send_modal(modal)

def setup(bot):
    bot.add_cog(EventManager(bot))
    print(f"✅ {EventManager.__name__} loaded")