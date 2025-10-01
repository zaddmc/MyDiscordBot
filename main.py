import os
import subprocess

import discord
from dotenv import load_dotenv

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

    await zadd_backdoor(message)
    await martjin_backdoor(message)
    await alehandre_backdoor(message)

    if message.content.startswith("echo"):
        print("Recieved:", message.content.split())
        await message.channel.send(
            subprocess.check_output(message.content.split()).decode("utf-8").strip()
        )


async def martjin_backdoor(message: discord.Message):
    if str(message.author) == "m4rt1n1955":
        await message.channel.send("Martin Martin er en uran hjort...")


async def alehandre_backdoor(message: discord.Message):
    if str(message.author) == "alehandre":
        await message.channel.send("Skibidi toilet sunset rizzler morning")


async def zadd_backdoor(message: discord.Message):
    if (
        str(message.author) == "zaddmc"
        and str(message.guild) == "None"
        and str(message.channel) == "Direct Message with Unknown User"
    ):
        channel = discord.utils.get(
            client.get_guild(COMTEK_P3_GUILD_ID).text_channels, name="general"
        )
        await channel.send(message.content)


if __name__ == "__main__":
    load_dotenv()
    client.run(os.getenv("DISCORD_TOKEN").strip("<>"))
