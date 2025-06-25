import discord
from src.commands import TICKET

class TicketManager(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TICKET.CreateButton())

    @staticmethod
    def is_ticket_channel(name: str) -> bool:
        return name.startswith("ticket-")

    async def get_or_create_category(self, guild, name):
        category = discord.utils.get(guild.categories, name=name)
        return category or await guild.create_category(name)

def setup(bot: discord.Bot):
    bot.add_cog(TicketManager(bot))
    print(f"✅ {TicketManager.__name__} loaded")