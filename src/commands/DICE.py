import discord
from discord import ApplicationContext
import random as rd


async def roll(ctx: ApplicationContext, amount:int, type:int):
    results = []
    for i in range(amount):
        result = rd.randint(1,type)
        results.append(result)

    total = sum(results)

    await ctx.respond(f"{type}面ダイスを{amount}個振ります。\n**結果:{results}**\n**合計:{total}**")


class Kujibiki():
    class Modal(discord.ui.Modal):
        def __init__(self, items_callback):
            super().__init__(title="くじびき作成")
            self.items_callback = items_callback

            # 入力欄: くじの中身
            self.kuji_items = discord.ui.InputText(
                label="くじの中身（カンマ区切りで入力）",
                placeholder="例: 大吉,中吉,小吉,凶"
            )
            self.add_item(self.kuji_items)

            # 入力欄: 趣旨
            self.purpose = discord.ui.InputText(
                label="くじの趣旨",
                placeholder="例: 新年会の景品抽選"
            )
            self.add_item(self.purpose)

        async def callback(self, interaction: discord.Interaction):
            items = [i.strip() for i in self.kuji_items.value.split(",") if i.strip()]
            purpose = self.purpose.value

            if not items:
                await interaction.response.send_message("もうくじがないよ！", ephemeral=True)
                return

            # ボタン付きビューを作成
            view = Kujibiki.View(items)

            embed = discord.Embed(
                title="くじびき",
                description=f"**{purpose}**",
                color=discord.Color.blurple()
            )
            embed.set_footer(text="ボタンを押してくじを引いてね！")

            await interaction.response.send_message(embed=embed, view=view)


    # --- ボタン付きビュー ---
    class View(discord.ui.View):
        def __init__(self, items: list[str]):
            super().__init__(timeout=None)
            self.items = items

        @discord.ui.button(label="くじを引く", style=discord.ButtonStyle.green)
        async def draw_button(self, button: discord.ui.Button, interaction: discord.Interaction):
            if not self.items:
                await interaction.response.send_message(
                    f"**もうくじがないよ！**", ephemeral=False
                )
            else:
                result = rd.choice(self.items)
                self.items.remove(result)
                await interaction.response.send_message(
                    f"🎯 {interaction.user.mention} の結果: **{result}**", ephemeral=False
                )