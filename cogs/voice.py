import os

import discord
from discord.ext import commands

from file_manager import get_filename


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hello")
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Hello {ctx.author.mention}")

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
            crx.message.guild.voice_client.play(
                discord.FFmpegPCMAudio(
                    executable="ffmpeg", source="songs/vGzJct0OV8M.mp3"
                )
            )

    @commands.command(name="leave", help="Tells the bot to leave voice channels")
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel")

    @commands.command(name="play", help="gib url to play")
    async def play(self, ctx, url):
        try:
            server = ctx.message.guild
            voice_channel = server.voice_client

            async with ctx.typing():
                filename = get_filename(url)
                voice_channel.play(
                    discord.FFmpegPCMAudio(executable="ffmpeg", source=filename)
                )
            await ctx.send("**Now playing:**")
        except:
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
