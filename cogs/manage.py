import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
from discord import ApplicationContext
from src.core import BASE
from src.commands import GET_MEMBERS, TICKET, LINK_VC_ROLE, ADD_STREAMER
from datetime import date

today = date.today()

class ManagerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    mng = SlashCommandGroup("mng", "管理者用初期設定コマンド")

    @mng.command(name="get_members", description="このサーバーのメンバー情報をJSONに保存します")
    async def get_members(self, ctx: ApplicationContext):
        await GET_MEMBERS.run(self, ctx)

    @mng.command(name="link", description="ロールとボイスチャンネルをカテゴリごとに紐づけ")
    async def link(self, ctx: ApplicationContext):
        await LINK_VC_ROLE.run(ctx)

    @mng.command(name="set_ticket_channel", description="チケット作成用チャンネルを設定します。")
    async def set_ticket_channel(self, ctx: ApplicationContext):
        await TICKET.set(ctx)

    @mng.command(name="addstreamer", description="新しい配信者（登録名）を追加します")
    async def add_streamer(
        self,
        ctx: ApplicationContext,
        name: Option(str, "登録用の英数字ID（例: Asaha_Yuria）"),  # type: ignore
        display_name: Option(str, "表示名（日本語など自由）"),  # type: ignore
        youtube_channel_id: Option(str, "YouTubeのチャンネルID（任意）", required=False),  # type: ignore
        twitch_username: Option(str, "TwitchのユーザーID（ログイン名・任意）", required=False)  # type: ignore
    ):
        await ADD_STREAMER.run(self, ctx, name, display_name, youtube_channel_id, twitch_username)

def setup(bot):
    bot.add_cog(ManagerCommands(bot))
    print(f"✅ {ManagerCommands.__name__} loaded")