import random

import discord
import requests
from discord import app_commands as ac
from discord.ext import commands

W2_SFW_TAGS = "waifu neko shinobu megumin cuddle cry hug awoo kiss lick pat smug bonk yeet blush smile wave highfive handhold nom bite happy wink poke dance".split()
W2_OTHER = "bully glomp slap kill kick".split()
W2_NSFW_TAGS = "waifu neko trap blowjob".split()


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

        if len(args) == 0:
            params["included_tags"] = random.choice(versatile_tag)

        else:
            is_channel_nsfw = getattr(ctx.channel, "is_nsfw", lambda: False)()

            all_tags = versatile_tag.copy()
            if is_channel_nsfw:
                all_tags.extend(nsfw_tag.copy())

            valid_tags = [b for b in map(lambda a: a.lower(), args) if b in all_tags]

            params["included_tags"] = ",".join(valid_tags)
            params["nsfw"] = "true" if is_channel_nsfw else "false"

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            await ctx.send(data["images"][0]["url"])
        else:
            await ctx.send("Failed to get image")

    @ac.command(
        name="summonwilliam", description="Gurateed to summon william within 2 min"
    )
    async def william101(self, intr: discord.Interaction):
        url = "https://api.waifu.pics/nsfw/trap"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            await intr.response.send_message(data["url"])
        else:
            await intr.response.send_message("Failed to get image")

    @ac.command(name="waifu2", description="Only choose one tag")
    @ac.describe(sfw_tag="This is sfw", nsfw_tag="This is not sfw")
    @ac.choices(
        sfw_tag=[ac.Choice(name=t, value=t) for t in W2_SFW_TAGS],
        nsfw_tag=[ac.Choice(name=t, value=t) for t in W2_NSFW_TAGS + W2_OTHER],
    )
    async def get_waifu2(
        self,
        interaction: discord.Interaction,
        sfw_tag: ac.Choice[str] | None,
        nsfw_tag: ac.Choice[str] | None,
    ):
        """I am not proud of this function, it was commissioned by William Bjerglund"""

        is_channel_nsfw = getattr(interaction.channel, "is_nsfw", lambda: False)()

        all_tags = W2_SFW_TAGS.copy()
        all_tags.extend(W2_OTHER.copy())
        if is_channel_nsfw:
            all_tags.extend(W2_NSFW_TAGS.copy())

        is_tag_nsfw = False
        tag = None
        if sfw_tag:
            tag = sfw_tag.value
        elif nsfw_tag:
            tag = nsfw_tag.value
            if tag in W2_NSFW_TAGS:
                is_tag_nsfw = True
        else:
            print("Unforseen tag")
            tag = "waifu"

        url = f"https://api.waifu.pics/{"nsfw" if is_tag_nsfw else "sfw"}/{tag}"

        response = requests.get(url)
        cha = self.bot.get_channel(1425561165802770492)  # Server Usage - bot logs

        if response.status_code == 200:
            data = response.json()
            await cha.send(f"{interaction.user.name} {url} <{data['url']}>")
            await interaction.response.send_message(data["url"])
        else:
            await interaction.response.send_message("Failed to get image")

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
    await bot.add_cog(WaifuHandler(bot), guilds=get_guilds())
