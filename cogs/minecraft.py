import discord
from discord import app_commands as ac
from discord.ext import commands, tasks
from mcstatus import JavaServer

import utils
from utils import get_guilds


class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot
        self.server: JavaServer = JavaServer.lookup(utils.get_server_ip())

    @tasks.loop(minutes=5)
    async def task_get_players():
        players = self.server.status().players.online

        await self.bot.change_presence(activity=discord.Game(name=f"{players} Players"))

    @ac.command(
        name="get_players", description="Get current players in Minecraft Server"
    )
    async def get_players(self, intr: discord.Interaction):
        respond = intr.response.send_message

        status = self.server.status()
        respone = f"There is currently {status.players.online} player in game"
        for player in status.players.sample:
            respone += f"\n- {player.name}"

        await respond(respone)


async def setup(bot):
    await bot.add_cog(Minecraft(bot), guilds=get_guilds())
