import os

import yt_dlp


def download(url: str):
    url_code = url.split("=")[1]
    if len(url_code) != 11:
        raise NameError(f"Url does not contain the 11 digits: {url}")

    output_path = f"songs/{url_code}"

    ydl_opts = {
        "format": "bestaudio/best",
        "extractaudio": True,
        "audioformat": "mp3",
        "outtmpl": output_path,  # filename template
        "noplaylist": True,  # just the single video
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",  # best quality
            },
            {
                "key": "FFmpegMetadata",  # embed metadata
            },
            {
                "key": "EmbedThumbnail",  # embed thumbnail if available
            },
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info_dict).rsplit(".", 1)[0] + ".mp3"


def get_filename(url: str) -> str:
    url_code = url.split("=")[1]
    url_code += ".mp3"

    if url_code in os.listdir("songs"):
        return f"songs/{url_code}"
    else:
        return download(url)


from enum import Enum


def __file_exists(file_path: str, default=dict) -> None:
    """If the given file does not exist, it will make one with an empty dict"""
    if not os.path.isfile(file_path):
        with open(file_path, "w") as file:
            file.write(str(default()))


class VarStoreEnum(Enum):
    """This Enum exists to make it clear which types of variable storages are available"""

    RESPONSE_LIST = "response_list"
    REACTIONS_LIST = "reactions_list"


def get_varstore(target: VarStoreEnum) -> dict | None:
    file_path = f"./varstore/{target.value}.txt"
    __file_exists(file_path)

    with open(file_path, "r") as file:
        data = file.read()
    return eval(data)


def save_varstore(mydict: dict, target: VarStoreEnum) -> None:
    with open(f"./varstore/{target.value}.txt", "w") as file:
        file.write(str(mydict))


def make_todo(
    contents: str,
    sender: str,
    sender_id: int,
    target: str,
    target_id: int,
    server_id: int,
):
    return {
        "contents": contents,
        "sender": sender,
        "sender_id": sender_id,
        "target": target,
        "target_id": target_id,
        "server": server_id,
    }


def get_todos() -> dict:
    file_path = "./varstore/todo_list.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write(str({"incomplete": [], "complete": []}))

    with open(file_path, "r") as file:
        data = file.read()
    return eval(data)


def save_todos(todos: dict) -> None:
    with open("./varstore/todo_list.txt", "w") as file:
        file.write(str(todos))
