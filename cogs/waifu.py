import discord
import requests
from discord import app_commands
from discord.ext import commands


class WaifuHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.command(name="waifu")
    async def get_waifu(self, ctx: commands.Context):
        url = "https://api.waifu.im/search"
        params = {}

        response = requests.get(url, params)

        if response.status_code == 200:
            data = response.json()
            await ctx.send(data["images"][0]["url"])
        else:
            await ctx.send("Failed to get image")

    @commands.command(name="joke")
    async def get_joke(self, ctx: commands.Context):
        url = "https://icanhazdadjoke.com/"
        headers = {"Accept": "text/plain"}

        response = requests.get(url,headers=headers)

        if response.status_code == 200:
            data = response.text
            await ctx.send(data)
        else:
            await ctx.send("You...")



from utils import get_guilds


async def setup(bot):
    test_server_id = 593152900063297557
    await bot.add_cog(WaifuHandler(bot), guilds=get_guilds())
