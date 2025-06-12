from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
from discord import ApplicationContext, Member
from src import JSON, COLOR, SECURE
import os
from dotenv import load_dotenv

load_dotenv()
DEV = int(os.getenv("DEV"))

class PointManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    point = SlashCommandGroup("point", "ポイント管理コマンド")

    @point.command(name="check", description="ポイント残高を確認します。")
    async def plus(self, ctx: ApplicationContext, target: Option(Member, "対象ユーザー", required = False, default=None)): # type:ignore
        await ctx.defer()
        guild=ctx.guild
        data_path = f".\\data\\member_data\\M{guild.id}.json"
        data = JSON.load(data_path)

        if target == None:
            result = data[str(str(ctx.author.id))]["point"]
            await ctx.respond(f"ポイント残高は{result}です。\n（実行者: {ctx.author.mention}）")
        else:
            result = data[str(target.id)]["point"]
            await ctx.respond(f"{target.name}のポイント残高は{result}です。\n（実行者: {ctx.author.mention}）")
        
    @point.command(name="plus", description="ポイントを付与します。")
    async def plus(self, ctx: ApplicationContext, target: Member, amount: int):
        await ctx.defer()
        if await SECURE.Restrict(ctx) == False:
            return
        guild=ctx.guild
        data_path = f".\\data\\member_data\\M{guild.id}.json"
        data = JSON.load(data_path)

        data[str(target.id)]["point"] = data[str(target.id)]["point"] + amount
        JSON.save(data, data_path)
        await ctx.respond(f"{target.name}に{amount}ポイントを付与しました。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）")
        COLOR.text(f"{target.name}に{amount}ポイントを付与しました。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）",COLOR.Log)

    @point.command(name="minus", description="ポイントを減らします。")
    async def plus(self, ctx: ApplicationContext, target: Member, amount: int):
        await ctx.defer()
        if await SECURE.Restrict(ctx) == False:
            return
        guild=ctx.guild
        data_path = f".\\data\\member_data\\M{guild.id}.json"
        data = JSON.load(data_path)
        
        if not data[str(target.id)]["point"] < amount:
            data[str(target.id)]["point"] = data[str(target.id)]["point"] - amount
            JSON.save(data, data_path)
            await ctx.respond(f"{target.name}のポイントを{amount}ポイント減らしました。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）")
            COLOR.text(f"{target.name}のポイントを{amount}ポイント減らしました。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）", COLOR.Log)
        else:
            await ctx.respond(f"{target.name}のポイントが足りません。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）")
            COLOR.text(f"{target.name}のポイントが足りません。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）", COLOR.WARN)

def setup(bot):
    bot.add_cog(PointManager(bot))
    print(f"✅ {PointManager.__name__} loaded")