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
