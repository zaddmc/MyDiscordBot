import discord

from file_manager import VarStoreEnum as VSE
from file_manager import get_varstore, save_varstore

COMTEK_P3_GUILD_ID = 1412345322968977450


async def always_respond_to(message: discord.Message, author: str, response: str):
    if str(message.author) == author:
        await message.channel.send(response)


async def always_respond_to_list(message: discord.Message):
    author = str(message.author)
    exchanges = get_varstore(VSE.RESPONSE_LIST)
    for key, value in exchanges.items():
        if author == key:
            await message.channel.send(value)


async def always_react_to_list(message: discord.Message):
    author = str(message.author)
    exchanges = get_varstore(VSE.REACTIONS_LIST)
    for key, value in exchanges.items():
        if author == key:
            await message.add_reaction(value)


def __get_user(message: discord.Message) -> discord.Member:
    usr = message.content.split()[2]
    if "@" in usr:
        return message.guild.get_member(int(usr[2:-1]))
    if usr.isdigit():
        return message.guild.get_member(int(usr))
    return message.guild.get_member_named(usr)


async def add_to_varstore(
    message: discord.Message, usr: discord.User, msg: str, list_type: VSE
):
    exchanges = get_varstore(list_type)
    new_msg = " ".join(msg)
    exchanges[str(usr)] = new_msg
    save_varstore(exchanges, list_type)
    await message.channel.send(f"User: {str(usr)} will now be bullied with: {new_msg}")


async def remove_from_varstore(
    message: discord.Message, usr: discord.User, varstores: list[str] | None = None
):
    if varstores == None:
        varstores = VSE

    res = []
    for varstore in varstores:
        exchanges = get_varstore(varstore)
        res.append(exchanges.pop(str(usr), None))
        save_varstore(exchanges, varstore)

    if all(res):
        await message.channel.send(f"User: {str(usr)}, will no longer be mentioned")
    else:
        print("Some exception occurred during the silenceing process: ", res)
        await message.channel.send(f"Failed to silence user: {str(usr)}")


async def zadd_backdoor(bot, message: discord.Message):
    msg = message.content.split()
    if str(message.author) == "zaddmc" and msg[0] == "zaddsays":
        usr = __get_user(message)

        match msg[1]:
            case "silence":
                await remove_from_varstore(message, usr)

            case "bully":
                await add_to_varstore(message, usr, msg[3:], VSE.RESPONSE_LIST)

            case "react":
                await add_to_varstore(message, usr, msg[3:], VSE.REACTIONS_LIST)
        return True
    return False
