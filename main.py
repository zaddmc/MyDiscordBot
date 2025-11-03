import asyncio
import os
import subprocess
import threading

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import zadd_handlers as zh
from file_manager import VarStoreEnum, get_varstore
from utils import get_guilds


class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.voice")
        await self.load_extension("cogs.todo")
        await self.load_extension("cogs.meet")
        await self.load_extension("cogs.waifu")


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

from flask import Flask, request

app = Flask(__name__)


@app.route("/github", methods=["POST"])
def github_webhook():
    if request.method != "POST":
        return

    payload = request.json
    if payload.get("ref"):
        repo = payload["repository"]["name"]
        pusher = payload["pusher"]["name"]
        commits = payload["commits"]

        commit_messages = "\n".join(
            [
                f"- [{c['id'][:7]}] {c['message']} by {c['author']['name']}"
                for c in commits
            ]
        )
        message = f"New push to {repo} by {pusher}\n{commit_messages}"

        cha = bot.get_channel(1425561165802770492)  # Server Usage - bot logs
        if cha:
            asyncio.run_coroutine_threadsafe(channel.send(message), bot.loop)
    return "OK", 200


def start_socket():
    app.run(host="0.0.0.0", port=25565)


bot = MyBot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    for g in get_guilds():
        await bot.tree.sync(guild=g)
    print("I am ready to fight")


@bot.tree.command(name="hell", description="I am dis")
async def slash_command(interaction: discord.Interaction):
    await interaction.response.send_message("Command")


@bot.event
async def on_voice_state_update(member, before, after: discord.VoiceState):
    if str(member) == str(bot.user):
        return
    if not (before.channel is None and after.channel):
        return
    channel: discord.VoiceChannel = after.channel

    await channel.connect()
    # Play Martin er en uran hjort
    after.channel.guild.voice_client.play(
        discord.FFmpegPCMAudio(
            executable="ffmpeg", source="songs/intro_song_martin.mp3"
        )
    )


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if str(message.channel) in ["udviklings-kanal"]:
        return

    if await zh.zadd_backdoor(bot, message) or await zh.agreed(bot, message):
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

    threading.Thread(target=start_socket).start()
    bot.run(DISCORD_TOKEN)
