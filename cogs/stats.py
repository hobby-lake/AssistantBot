import discord
from discord.ext import commands, tasks
from discord.commands import SlashCommandGroup
from src.commands import STATS
from src.core import CONSOLE, BASE
from src.tasks import DEV_STATS_UPDATE

class DevelopStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()

    stats = SlashCommandGroup("stats", "開発状況管理コマンドグループ")

    @stats.command(name="init",description="開発ステータス表を設置する")
    async def init_embed(self, ctx: discord.ApplicationContext):
        embed = await STATS.set_embed(data=STATS.get_data(guild_id=ctx.guild_id))
        message = await ctx.channel.send(embed=embed)
        await ctx.respond("✅ 統計メッセージを送信し、追跡を開始しました。", ephemeral=True)

        config_path = BASE.get_json_path(ctx.guild_id, "embed")
        try:
            config = BASE.dataload(config_path)
        except:
            BASE.datasave({}, config_path)
            config = BASE.dataload(config_path)
        
        config["Share_dev_stats"] = {
            "channel_id": ctx.channel.id,
            "message_id": message.id
        }

        BASE.datasave(config, config_path)

    @tasks.loop(hours=2)
    async def update_stats(self):
        """定期的に統計情報を更新するタスク"""
        for guild_id in BASE.GUILD_IDS:
            config_path = BASE.get_json_path(guild_id, "embed")
            try:
                config = BASE.dataload(config_path)
            except:
                BASE.datasave({}, config_path)
                config = BASE.dataload(config_path)
            await DEV_STATS_UPDATE.run(self.bot, config=config)
        CONSOLE.text(text="開発状況を共有しました！", pattern=CONSOLE.Log)

def setup(bot: discord.Bot):
    bot.add_cog(DevelopStats(bot))
    print(f"✅ {DevelopStats.__name__} loaded")