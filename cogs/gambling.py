import logging

import discord
from discord import app_commands as ac
from discord.ext import commands

import utils
from utils import get_guilds

lg = logging.getLogger(__name__)

START_POINTS = 1000


class GameState:
    def __init__(self, cha_id: int):
        self.cha_id: int = cha_id
        # Players with their id and points
        self.players: dict[int, int] = {}
        self.pool: int = 0

    def place_bet(self, player_id: int, amount: int):
        if player_id not in self.players.keys():
            self.players[player_id] = START_POINTS

        if self.players[player_id] >= amount:
            self.pool += amount
            self.players[player_id] -= amount
            return True
        return False


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        # The dicts consist of the channel id and associated pool
        self.boards: dict[int, GameState] = {}
        self.players: dict = {}

    @ac.command(name="p_place_bet", description="Place a bet for poker")
    @ac.describe(amount="The amount to gamble, leave empty for call")
    async def place_bet(self, intr: discord.Interaction, amount: int | None):
        respond = intr.response.send_message
        cha_id: int = intr.channel_id
        if not amount:
            amount = 10

        if intr.channel_id not in self.boards.keys():
            self.boards[cha_id] = GameState(cha_id)

        board: GameState = self.boards[cha_id]

        if board.place_bet(intr.user.id, amount):
            await respond("Your bet has been placed")
        else:
            await respond("Failed to place your bet", ephemeral=True)

    @ac.command(
        name="p_check_board",
        description="Check if board status of board in current channel",
    )
    async def check_bets(self, intr: discord.Interaction):
        respond = intr.response.send_message

        if intr.channel_id in self.boards.keys():
            board = self.boards[intr.channel_id]
            await respond(f"{board.pool}   {board.players}")
        else:
            await respond("Board for this channel does not exist")


async def setup(bot: commands.Bot):
    await bot.add_cog(Gambling(bot), guilds=get_guilds())
