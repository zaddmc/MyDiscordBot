import discord

from file_manager import VarStoreEnum, get_varstore, save_varstore

COMTEK_P3_GUILD_ID = 1412345322968977450


async def always_respond_to(message: discord.Message, author: str, response: str):
    if str(message.author) == author:
        await message.channel.send(response)


async def always_respond_to_list(message: discord.Message):
    author = str(message.author)
    exchanges = get_varstore(VarStoreEnum.RESPONSE_LIST)
    for key, value in exchanges.items():
        if author == key:
            await message.channel.send(value)


async def zadd_backdoor(bot, message: discord.Message):
    msg = message.content
    if str(message.author) == "zaddmc" and msg.startswith("zaddsays"):
        match msg.split()[1]:
            case "silence":
                exchanges = get_varstore(VarStoreEnum.RESPONSE_LIST)
                usr = msg.split()[2]
                res = exchanges.pop(usr, None)
                save_varstore(exchanges, VarStoreEnum.RESPONSE_LIST)
                if res:
                    await message.channel.send(
                        f"User: {str(usr)}, will no longer be mentioned"
                    )
                else:
                    await message.channel.send(f"Failed to silence user: {str(usr)}")
            case "bully":
                exchanges = get_varstore(VarStoreEnum.RESPONSE_LIST)
                usr = msg.split()[2]
                new_msg = " ".join(msg.split()[3:])
                exchanges[usr] = new_msg
                save_varstore(exchanges, VarStoreEnum.RESPONSE_LIST)
                await message.channel.send(
                    f"User: {str(usr)} will now be bullied with: {new_msg}"
                )
