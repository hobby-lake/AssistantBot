from discord import ApplicationContext
import random as rd


async def roll(ctx: ApplicationContext, amount:int, type:int):
    results = []
    for i in range(amount):
        result = rd.randint(1,type)
        results.append(result)

    total = sum(results)

    await ctx.respond(f"{type}面ダイスを{amount}個振ります。\n**結果:{results}**\n**合計:{total}**")