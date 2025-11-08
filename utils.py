import discord


async def init(ebot: discord.ext.commands.Bot):
    global bot, test_server, log_channel
    bot = ebot
    test_server = await bot.fetch_guild(593152900063297557)  # Server-usage
    log_channel = await bot.fetch_channel(1425561165802770492)  # Server-usage  bot-logs


def get_guilds() -> list[discord.Guild]:
    return [
        discord.Object(id=593152900063297557),  # Server-usage
        discord.Object(id=1412345322968977450),  # Comtekp3
        discord.Object(id=1425443931319046195),  # REPO -- William
    ]
