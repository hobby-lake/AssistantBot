import discord
from discord.ext import commands, tasks
from discord.commands import SlashCommandGroup, Option
from discord import ApplicationContext
from src.commands import SCHEDULE
from src.tasks import SCHEDULE_UPDATE
from src.core import BASE

async def name_autocomplete(ctx: discord.AutocompleteContext):
    """登録配信者名のリスト化（サーバーあたり最大25名まで）"""
    guild_id = ctx.interaction.guild_id
    path = BASE.get_json_path(guild_id=guild_id, category="streamer")
    config = BASE.dataload(path)
    return list(config.keys())[:25]

class CalendarManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_calendar.start()

    calendar = SlashCommandGroup("calendar", "配信カレンダー管理コマンド")

    @calendar.command(
        name="init",
        description="指定チャンネルへ事前に登録した配信者のカレンダーを送信します。"
    )
    async def init(
        self,
        ctx: ApplicationContext,
        name: Option(str, "登録id", autocomplete=name_autocomplete),  # type: ignore
        channel: Option(discord.TextChannel, "配信予定を表示するチャンネル")  # type: ignore
    ):
        await SCHEDULE.initialize(ctx, name, channel)

    @tasks.loop(hours=1)
    async def update_calendar(self):
        await SCHEDULE_UPDATE.run(self)

def setup(bot: discord.Bot):
    bot.add_cog(CalendarManager(bot))
    print(f"✅ {CalendarManager.__name__} loaded")