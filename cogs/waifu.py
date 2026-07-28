import json
import os
import random
from typing import Optional

import discord
import requests
from discord import app_commands as ac
from discord.ext import commands

import utils

URL_BASE = "https://api.nekosapi.com/v5"
TAG_CACHE: Optional[dict] = None


def get_tags() -> dict[str, str]:
    global TAG_CACHE
    if TAG_CACHE:
        return TAG_CACHE

    resp = requests.get(URL_BASE + "/tags")
    if resp.status_code != 200:
        return {"no-tags": "Sorry, failed to fetch tags"}
    tags = {}
    for item in resp.json()["items"]:
        desc = item["name"] + " - " + ("SFW" if item["is_nsfw"] else "NSFW")
        if len(desc) > 100:
            desc = desc[:96] + "..."
        tags[item["id"]] = desc
    TAG_CACHE = tags
    return tags


class WaifuHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def m_tag_autocomplete(self, intr: discord.Interaction, current: str) -> list[ac.Choice[str]]:
        return [ac.Choice(name=name, value=id) for id, name in get_tags().items() if current.lower() in name.lower()]

    @ac.command(name="nnwaifu", description="Get a waifu")
    @ac.describe(tag="The desired tag", rating="The rating of the content")
    @ac.choices(
        rating=[
            ac.Choice(name="Safe", value="safe"),
            ac.Choice(name="Suggestive", value="suggestive"),
            ac.Choice(name="Borderline", value="borderline"),
            ac.Choice(name="Explicit", value="explicit"),
        ]
    )
    @ac.autocomplete(tag=m_tag_autocomplete)
    async def get_waifu_v4(self, intr: discord.Interaction, tag: Optional[str], rating: ac.Choice[str] | None):
        params = "&".join((f"tag={tag}" if tag else "", f"rating={rating.value}" if rating else ""))
        query = URL_BASE + "/images/random" + ("?" + params if len(params) else "")

        resp = requests.get(query)
        if resp.status_code != 200:
            await intr.response.send_message("Failed to find an image matching your request", ephemeral=True)
        else:
            await intr.response.send_message(resp.json()["url"])

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

    @ac.command(name="waifu_spicy", description="Get the most spicy Waifu. Warning: only NSFW")
    async def get_spicy_waifu(self, intr: discord.Interaction):
        respond = intr.response.send_message
        url = "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&limit=1&json=1"
        api_key = os.getenv("R34_API_KEY")
        user_id = os.getenv("R34_USER_ID")

        if not (api_key and user_id):
            await respond("Failed to load API key", ephemeral=True)
            return

        url += "&api_key=" + api_key
        url += "&user_id=" + user_id
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()[0]
            img = data["file_url"]
            await respond(img)
        else:
            await respond("Failed to get image", ephemeral=True)


from utils import get_guilds


async def setup(bot):
    await bot.add_cog(WaifuHandler(bot), guilds=get_guilds())
