import discord
from discord import app_commands as ac
from discord.ext import commands

import utils
from utils import get_guilds


class Backdoor(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @ac.command(name="execute", description="Execute some command")
    async def execute_any(self, interaction: discord.Interaction, cmd: str):
        if interaction.user.name != "zaddmc":
            await utils.log_channel.send(
                f"User: **{interaction.user.name}** Tried to execute a command"
            )
            await interaction.response.send_message("You do not have permission")
            return

        try:
            res = exec(cmd)
            await interaction.response.send_message(str(res))
        except Exception as e:
            await interaction.response.send_message(f"Command failed: {e}")


async def setup(bot):
    await bot.add_cog(Backdoor(bot), guilds=get_guilds())
