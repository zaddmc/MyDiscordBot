import logging

import discord
from discord import app_commands as ac
from discord.ext import commands

import utils
from utils import get_guilds

lg = logging.getLogger(__name__)


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @ac.command(name="p_place_bet", description="Place a bet for poker")
    @ac.describe(amount="The amount to gamble, leave empty for call")
    @ac.choices([ac.Choice(name="amount")])
    async def place_bet(self, intr: discord.Interaction, amount: ac.Choice[int] | None):
        respond = intr.response.send_message
        if not amount:
            amount = 10

        await respond(f"You have gamled {amount}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Gambling(bot), guilds=get_guilds())
