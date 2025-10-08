import asyncio
import os
import subprocess

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import zadd_handlers as zh
from file_manager import VarStoreEnum, get_varstore


class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.voice")


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = MyBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if str(message.channel) in ["udviklings-kanal"]:
        return

    if await zh.zadd_backdoor(bot, message):
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
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN").strip("<>")
    # client.run(DISCORD_TOKEN)

    bot.run(DISCORD_TOKEN)
