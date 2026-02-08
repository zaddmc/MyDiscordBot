import logging

import discord
from discord import app_commands as ac
from discord.ext import commands, tasks
from mcstatus import JavaServer

import utils
from utils import get_guilds

lg = logging.getLogger(__name__)


class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.server: JavaServer = JavaServer.lookup(utils.get_server_ip())
        self.task_update_status.start()

    def cog_unload(self):
        lg.info("Stopping cog Minecraft")
        self.task_update_status.cancel()

    async def update_status(self):
        players = self.server.status().players.online

        lg.info(f"Updating status cur {players}")

        if players:
            activity = discord.Game(name=f"{players} Players")
            await self.bot.change_presence(activity=activity)
        else:
            await self.bot.change_presence(activity=None)

    @tasks.loop(minutes=5)
    async def task_update_status(self):
        await self.update_status()

    @task_update_status.before_loop
    async def before_task_update_status(self):
        await self.bot.wait_until_ready()
        lg.info("Starting auto status updater")

    @ac.command(name="update_status", description="manually start updating status")
    async def manual_update_status(self, intr: discord.Interaction):
        respond = intr.response.send_message
        await self.update_status()
        await respond("Updated the status", ephemeral=True)

    @ac.command(
        name="get_players", description="Get current players in Minecraft Server"
    )
    async def get_players(self, intr: discord.Interaction):
        respond = intr.response.send_message

        status = self.server.status().players
        respone = f"There is currently {status.online} player in game"
        if status.online:
            for player in status.sample:
                respone += f"\n- {player.name}"

        await respond(respone)


async def setup(bot: commands.Bot):
    await bot.add_cog(Minecraft(bot), guilds=get_guilds())
