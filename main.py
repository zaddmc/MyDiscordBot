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
        await self.load_extension("cogs.gambling")
        await self.load_extension("cogs.stuff")


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True


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

    await zh.zadd_backdoor(bot, message)
    await zh.agreed(bot, message)
    await zh.microslop(bot, message)
    await zh.nogipity(bot, message)
    await zh.delete(bot, message)

    await zh.always_react_to_list(message)
    await zh.always_respond_to_list(message)

    if message.content.startswith("echo"):
        print("Recieved:", message.content.split())
        await message.channel.send(subprocess.check_output(message.content.split()).decode("utf-8").strip())
    # This line should be last to process the commands as specified in class MyBot
    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.emoji.name != "❌":
        return
    if bot.user and payload.message_author_id != bot.user.id:
        return

    channel = bot.get_channel(payload.channel_id)
    if channel is None:
        channel = await bot.fetch_channel(payload.channel_id)

    if isinstance(channel, discord.TextChannel):
        message = await channel.fetch_message(payload.message_id)

    cha = bot.get_channel(1425561165802770492)  # Server Usage - bot logs
    if isinstance(cha, discord.TextChannel):
        await cha.send(content=f"This has been deleted by {message.author}:\n" + message.content)

    await message.delete()


if __name__ == "__main__":
    load_dotenv()
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    if DISCORD_TOKEN:
        bot.run(DISCORD_TOKEN, root_logger=True)
