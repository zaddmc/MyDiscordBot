import logging
import re
import subprocess

import a2s
import discord
from discord import app_commands as ac
from discord.ext import commands, tasks
from mcstatus import JavaServer

import utils
from utils import get_guilds

lg = logging.getLogger(__name__)


def valheim_join_code():
    cmd = "docker logs --tail 500 valheim"
    rune = r"join code (\d+)"
    res = subprocess.check_output(cmd.split()).decode("utf-8").strip().splitlines()

    for line in res[::-1]:
        code = re.findall(rune, line)
        if code:
            return code[0]
    return "No Code"


class Minecraft(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.mc_server: JavaServer = JavaServer.lookup(utils.get_server_ip())
        self.se_addr: tuple[str, int] = ("127.0.0.1", 27912)
        self.task_update_status.start()

    def cog_unload(self):
        lg.info("Stopping cog Minecraft")
        self.task_update_status.cancel()

    async def update_status(self):
        try:
            mc_players = self.mc_server.status().players.online
        except:
            mc_players = None

        try:
            se_players = a2s.info(self.se_addr, timeout=3).player_count
        except:
            se_players = None

        try:
            val_code = valheim_join_code()
        except:
            val_code = None

        lg.info(f"Updating status")

        if val_code:
            activity = discord.Game(name=f"Valheim: {val_code}")
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

    @ac.command(name="get_players", description="Get current players in Minecraft Server")
    async def get_players(self, intr: discord.Interaction):
        respond = intr.response.send_message

        try:
            status = self.mc_server.status().players
            respone = f"There is currently {status.online} player in game"
            if status.online:
                for player in status.sample:
                    respone += f"\n- {player.name}"

            await respond(respone)
        except:
            await respond("Server is currently Down")


async def setup(bot: commands.Bot):
    await bot.add_cog(Minecraft(bot), guilds=get_guilds())
