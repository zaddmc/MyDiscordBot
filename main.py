import logging
import os
import subprocess
import sys

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import zadd_handlers as zh
from file_manager import VarStoreEnum, get_varstore
from utils import get_guilds, init

lg = logging.getLogger(__name__)


class MyBot(commands.Bot):
    async def setup_hook(self):
        await init(self)

        await self.load_extension("cogs.voice")
        await self.load_extension("cogs.todo")
        await self.load_extension("cogs.meet")
        await self.load_extension("cogs.waifu")
        await self.load_extension("cogs.backdoor")
        await self.load_extension("cogs.minecraft")


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

global bot
bot = MyBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    for g in get_guilds():
        await bot.tree.sync(guild=g)
    lg.info("Bot is ready to rumble")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    if (
        await zh.zadd_backdoor(bot, message)
        or await zh.agreed(bot, message)
        or await zh.microslop(bot, message)
    ):
        return

    await zh.always_react_to_list(message)
    await zh.always_respond_to_list(message)

    if message.content.startswith("echo"):
        print("Recieved:", message.content.split())
        await message.channel.send(
            subprocess.check_output(message.content.split()).decode("utf-8").strip()
        )
    # This line should be last to process the commands as specified in class MyBot
    await bot.process_commands(message)


if __name__ == "__main__":
    load_dotenv()
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

    bot.run(DISCORD_TOKEN, root_logger=True)
