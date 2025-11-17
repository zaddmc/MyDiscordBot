import os
import random
from time import sleep

import discord
from discord import app_commands as ac
from discord.ext import commands

import main
from file_manager import get_filename


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def play_martin_song(self, voice_client: discord.VoiceClient):
        # Play Martin er en uran hjort
        voice_client.play(
            discord.FFmpegPCMAudio(
                executable="ffmpeg", source="songs/intro_song_martin.mp3"
            )
        )

    @commands.command(name="join", help="DEPRECATED")
    async def join(self, ctx: commands.Context):
        await ctx.send("This function is deprecated by **/join**")

    @ac.command(name="join", description="Tells the bot to join your vc")
    async def join(self, intr: discord.Interaction):
        respond = intr.response.send_message  # Just an alias
        if not intr.user.voice:
            await respond(
                f"{intr.user.name} is not connected to a voice channel",
                ephemeral=True,
            )
        else:
            await intr.user.voice.channel.connect()
            await respond("Connected to Voice channel", ephemeral=True)

            # Play Martin er en uran hjort
            self.play_martin_song(intr.guild.voice_client)

    @commands.command(name="leave", help="DEPRECATED")
    async def leave(self, ctx: commands.Context):
        await ctx.send("DEPRECATED, use /leave")

    @ac.command(name="leave", description="Make the bot leave")
    async def leave(self, intr: discord.Interaction):
        respond = intr.response.send_message  # Just an alias
        voice_client = intr.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            await respond("Bot has left", silent=True)
        else:
            await respond("Bot is not connected", ephemeral=True)

    @commands.command(name="play", help="DEPRECATED")
    async def play(self, ctx: commands.Context):
        ctx.send("DEPRECATED, use /play url")

    @ac.command(name="play", description="Give url to play")
    @ac.describe(url="A youtube url")
    async def play(self, intr: discord.Interaction, url: str):
        respond = intr.response.send_message  # Just an alias
        # Clean Url
        for tag in ["&list", "&pp"]:
            if tag in url:
                url = url[: url.find(tag)]
        try:
            filename = get_filename(url)
            intr.guild.voice_client.play(discord.FFmpegPCMAudio(filename))
            await respond("**Now Playing**", silent=True)
        except NameError as ne:
            await respond("Invalid URL", ephemeral=True)
        except Exception as e:
            print("Failure in getting filename", e, type(e))
            await respond("Failed to play song", ephemeral=True)

    @commands.command(name="pause", help="This command pauses the song")
    async def pause(self, ctx: commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name="resume", help="Resumes the song")
    async def resume(self, ctx: commands.Context):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send(
                "The bot was not playing anything before this. Use play_song command"
            )

    @commands.command(name="stop", help="DEPRECATED")
    async def stop(self, ctx: commands.Context):
        ctx.send("DEPRECATED, use /stop")

    @ac.command(name="stop", description="Stops playing")
    async def stop(self, intr: discord.Interaction):
        respond = intr.response.send_message  # Just an alias
        voice_client = intr.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await respond("Stopped playing", silent=True)
        else:
            await respond("Not playing", ephemeral=True)


from utils import get_guilds


async def setup(bot):
    await bot.add_cog(Voice(bot), guilds=get_guilds())
