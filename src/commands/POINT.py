from src.core import BASE, CONSOLE, SECURITY

async def check(self, ctx, target):
    await ctx.defer()
    guild=ctx.guild
    data_path = str(BASE.get_json_path(guild_id=guild.id,category="member"))
    data = BASE.dataload(data_path)

    if target == None:
        result = data[str(str(ctx.author.id))]["point"]
        await ctx.respond(f"ポイント残高は{result}です。\n（実行者: {ctx.author.mention}）")
    else:
        result = data[str(target.id)]["point"]
        await ctx.respond(f"{target.display_name}のポイント残高は{result}です。\n（実行者: {ctx.author.mention}）")
    
async def plus(self, ctx, target, amount):
    await ctx.defer()
    if await SECURITY.Restrict(ctx) == False:
        return
    guild=ctx.guild
    data_path = str(BASE.get_json_path(guild_id=guild.id,category="member"))
    data = BASE.dataload(data_path)

    data[str(target.id)]["point"] = data[str(target.id)]["point"] + amount
    BASE.datasave(data, data_path)
    await ctx.respond(f"{target.display_name}に{amount}ポイントを付与しました。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）")
    CONSOLE.text(f"{target.display_name}に{amount}ポイントを付与しました。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）",CONSOLE.Log)

async def minus(self, ctx, target, amount):
    await ctx.defer()
    if await SECURITY.Restrict(ctx) == False:
        return
    guild=ctx.guild
    data_path = str(BASE.get_json_path(guild_id=guild.id,category="member"))
    data = BASE.dataload(data_path)
    
    if not data[str(target.id)]["point"] < amount:
        data[str(target.id)]["point"] = data[str(target.id)]["point"] - amount
        BASE.datasave(data, data_path)
        await ctx.respond(f"{target.display_name}のポイントを{amount}ポイント減らしました。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）")
        CONSOLE.text(f"{target.display_name}のポイントを{amount}ポイント減らしました。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）", CONSOLE.Log)
    else:
        await ctx.respond(f"{target.display_name}のポイントが足りません。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）")
        CONSOLE.text(f"{target.display_name}のポイントが足りません。\nポイント残高は{data[str(target.id)]['point']}です。\n（実行者: {ctx.author.mention}）", CONSOLE.WARN)
