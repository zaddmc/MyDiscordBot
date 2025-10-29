import discord
from discord import app_commands as ac
from discord.ext import commands


class MeetHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @ac.command(name="addmeet", description="Add a meeting")
    @ac.describe(name="Name or date of meeting", target="Who it is with")
    @ac.choices(
        target=[
            ac.Choice(name="Rasmus", value="rasmus"),
            ac.Choice(name="Anete", value="anete"),
        ]
    )
    async def add_meeting(
        self, action: discord.Interaction, name: str, target: ac.Choice[str]
    ):
        await action.response.send_message("Hello")


from utils import get_guilds


async def setup(bot):
    test_server_id = 593152900063297557
    await bot.add_cog(MeetHandler(bot), guilds=get_guilds())
