import base64
import io
import logging
import random

import discord
import segno
from discord import app_commands as ac
from discord.ext import commands, tasks

import utils
from utils import get_guilds

lg = logging.getLogger(__name__)


class Stuff(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @ac.command(name="gen_qr_code", description="Convert string to Qr code")
    @ac.describe(string_to_convert="The string to convert")
    async def gen_qr_code(self, intr: discord.Interaction, string_to_convert: str):
        respond = intr.response.send_message

        if random.randint(0, 10) == 1:
            string_to_convert = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        uri_data = segno.make_qr(string_to_convert).png_data_uri(scale=4)
        header, encoded = uri_data.split(",", 1)
        data = base64.b64decode(encoded)

        with io.BytesIO(data) as bin_tmp:
            file = discord.File(bin_tmp, filename="your_qr_code.png")
            await respond(file=file)
            return
        await respond("Failed to generate")


async def setup(bot: commands.Bot):
    await bot.add_cog(Stuff(bot), guilds=get_guilds())
