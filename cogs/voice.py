import os
import random
from time import sleep

import discord
from discord.ext import commands

import main
from file_manager import get_filename


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playing = False

    @commands.command(name="hello")
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Hello {ctx.author.mention}")

    @main.bot.event
    async def on_voice_state_update(member, before, after: discord.VoiceState):
        if str(member) == str(bot.user):
            return
        if not (before.channel is None and after.channel):
            return
        channel: discord.VoiceChannel = after.channel

        await channel.connect()
        self.playing = True

        while self.playing:
            self.play_martin_song(after)
            sleep(random.randint(120, 600))

    def play_martin_song(after):
        # Play Martin er en uran hjort
        after.channel.guild.voice_client.play(
            discord.FFmpegPCMAudio(
                executable="ffmpeg", source="songs/intro_song_martin.mp3"
            )
        )

    @commands.command(name="join", help="Tells the bot to join your vc")
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send(
                "{} is not connected to a voice channel".format(ctx.message.author.name)
            )
            return
        else:
            channel = ctx.message.author.voice.channel
            await channel.connect()
            # Play Martin er en uran hjort
            ctx.message.guild.voice_client.play(
                discord.FFmpegPCMAudio(
                    executable="ffmpeg", source="songs/intro_song_martin.mp3"
                )
            )

    @commands.command(name="leave", help="Tells the bot to leave voice channels")
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            self.playing = False
            await voice_client.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel")

    @commands.command(name="play", help="gib url to play")
    async def play(self, ctx, url: str):
        if "&list" in url:
            url = url[: url.index("&list")]
        try:
            server = ctx.message.guild
            voice_channel = server.voice_client

            async with ctx.typing():
                filename = get_filename(url)
                voice_channel.play(
                    discord.FFmpegPCMAudio(executable="ffmpeg", source=filename)
                )
            await ctx.send("**Now playing:**")
        except Exception as e:
            print("Error in play command", e)
            await ctx.send("The bot is not connected to a voice channel.")

    @commands.command(name="pause", help="This command pauses the song")
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name="resume", help="Resumes the song")
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send(
                "The bot was not playing anything before this. Use play_song command"
            )

    @commands.command(name="stop", help="Stops the song")
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")


async def setup(bot):
    await bot.add_cog(Voice(bot))
