import discord
import requests
import random
from discord import app_commands
from discord.ext import commands


class WaifuHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.command(name="waifu")
    async def get_waifu(self, ctx: commands.Context, *args):
        """I am not proud of this function, it was commissioned by William Bjerglund"""

        versatile_tag = [
            "maid",
            "waifu",
            "marin-kitagawa",
            "mori-calliope",
            "raiden-shogun",
            "oppai",
            "selfies",
            "uniform",
            "kamisato-ayaka",
        ]
        nsfw_tag = ["ass", "hentai", "milf", "oral", "paizuri", "ecchi", "ero"]

        url = "https://api.waifu.im/search"
        params = {}

        is_channel_nsfw = getattr(ctx.channel, "is_nsfw", lambda: False)()

        all_tags = versatile_tag.copy()
        if is_channel_nsfw:
            all_tags.extend(nsfw_tag.copy())

        valid_tags = [b for b in map(lambda a: a.lower(),args) if b in all_tags]

        params["included_tags"] = ",".join(valid_tags)
        params["nsfw"] = "true" if is_channel_nsfw else "false"    

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            await ctx.send(data["images"][0]["url"])
        else:
            await ctx.send("Failed to get image")

    @commands.command(name="waifu2")
    async def get_waifu2(self, ctx: commands.Context, *args):
        """I am not proud of this function, it was commissioned by William Bjerglund"""

        versatile_tag = [
         "waifu",
        "neko",
        "shinobu",
        "megumin",
        "bully",
        "cuddle",
        "cry",
        "hug",
        "awoo",
        "kiss",
        "lick",
        "pat",
        "smug",
        "bonk",
        "yeet",
        "blush",
        "smile",
        "wave",
        "highfive",
        "handhold",
        "nom",
        "bite",
        "glomp",
        "slap",
        "kill",
        "kick",
        "happy",
        "wink",
        "poke",
        "dance",
        ]
        nsfw_tag = [
             "waifu",
        "neko",
        "trap",
        "blowjob",
        ]


        is_channel_nsfw = getattr(ctx.channel, "is_nsfw", lambda: False)()

        all_tags = versatile_tag.copy()
        if is_channel_nsfw:
            all_tags.extend(nsfw_tag.copy())

        if len(args) == 1:
            tag = args[0].lower()
        tag = tag if tag in all_tags else random.choice(versatile_tag)

        url = f"https://api.waifu.pics/{"nsfw" if tag in nsfw_tag else "sfw"}/{tag}"

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            await ctx.send(data["url"])
        else:
            await ctx.send("Failed to get image")

    @commands.command(name="joke")
    async def get_joke(self, ctx: commands.Context):
        url = "https://icanhazdadjoke.com/"
        headers = {"Accept": "text/plain"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.text
            await ctx.send(data)
        else:
            await ctx.send("You...")


from utils import get_guilds


async def setup(bot):
    test_server_id = 593152900063297557
    await bot.add_cog(WaifuHandler(bot), guilds=get_guilds())
