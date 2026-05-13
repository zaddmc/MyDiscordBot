import json
import random

import discord
import requests
from discord import app_commands as ac
from discord.ext import commands

import utils

URL_BASE = "https://api.waifu.im/"


def get_tags() -> dict[str, str]:
    # This will only get 30 tags, but that is fine as the bot can only show 30 or 25. As of current it only has 19
    resp = requests.get(URL_BASE + "tags")
    if resp.status_code != 200:
        return {"no-tags": "Sorry, failed to fetch tags"}
    tags = {}
    for item in resp.json()["items"]:
        if item["totalCount"] == 0:
            continue
        desc = item["name"] + " - " + item["description"]
        if len(desc) > 100:
            desc = desc[:96] + "..."
        tags[item["slug"]] = desc
    return tags


class WaifuHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @ac.command(name="waifu", description="Get a waifu")
    @ac.describe(tag="The desired tag", is_nsfw="Do you want Not Safe For Work Content? Any value is fine")
    @ac.choices(tag=[ac.Choice(name=v, value=k) for k, v in get_tags().items()])
    async def get_waifu_v3(self, intr: discord.Interaction, tag: ac.Choice[str] | None, is_nsfw: str | None = None):
        params = {}

        is_cha_nsfw = getattr(intr.channel, "is_nsfw", lambda: False)()
        if is_cha_nsfw and is_nsfw:
            params["IsNsfw"] = "True"

        if tag:
            params["IncludedTags"] = tag.value

        resp = requests.get(URL_BASE + "images", params)
        if resp.status_code != 200 or len(resp.json()["items"]) == 0:
            await intr.response.send_message("Failed to find an image matching your request", ephemeral=True)
        else:
            await intr.response.send_message(resp.json()["items"][0]["url"])

    @ac.command(name="summonwilliam", description="Gurateed to summon william within 2 min")
    async def william101(self, intr: discord.Interaction):
        await intr.response.send_message(
            "Sadly the new api does not have the Trap tag, thereby rendering this command useless"
        )

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

    @ac.command(name="waifu_quote", description="Simple anime quotes")
    async def get_waifu_quote(self, intr: discord.Interaction):
        respond = intr.response.send_message
        url = "https://api.animechan.io/v1/quotes/random"

        response = requests.get(url)

        if response.status_code == 200:
            data = json.loads(response.content)["data"]
            quote = data["content"]
            person = data["character"]["name"]
            anime = data["anime"]["name"]
            string = f"*{quote}* -{person} -- {anime}"
            await respond(string)
        else:
            await respond("rimuru is best GIRL")


from utils import get_guilds


async def setup(bot):
    await bot.add_cog(WaifuHandler(bot), guilds=get_guilds())
