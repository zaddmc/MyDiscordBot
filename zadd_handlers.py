import discord


async def always_respond_to(message: discord.Message, author: str, response: str):
    if str(message.author) == author:
        await message.channel.send(response)


async def zadd_backdoor(message: discord.Message):
    if (
        str(message.author) == "zaddmc"
        and str(message.guild) == "None"
        and str(message.channel) == "Direct Message with Unknown User"
    ):
        channel = discord.utils.get(
            client.get_guild(COMTEK_P3_GUILD_ID).text_channels, name="general"
        )
        await channel.send(message.content)
