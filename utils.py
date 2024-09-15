"""
utils.py
Written by Joshua Kitchen - 2024

PYCHAT APPLICATION PROTOCOL

 ------------------------ HEADER ----------------------------  -- MSG BODY --
|                                                            |               |
|                                                            |               |
[username_size (4 bytes)][data_size (4 bytes)][flags (1 byte)][username][data]

FLAGS:
    1 = Text
    2 = Image
    4 = Information
    8 = Disconnecting
"""
import io
import os
import logging

logger = logging.getLogger()


def encode_msg(username: bytes, data: bytes, flags: int):
    msg = bytearray()
    username_size = len(username).to_bytes(4, "big")
    data_size = len(data).to_bytes(4, "big")
    flags = flags.to_bytes(1, "big")
    msg.extend(username_size)
    msg.extend(data_size)
    msg.extend(flags)
    msg.extend(username)
    msg.extend(data)
    return msg


def decode_msg(msg: bytearray):
    header = msg[0:9]
    body = msg[9:]
    username_size = int.from_bytes(header[0:4])
    data_size = int.from_bytes(header[4:8])
    flags = header[-1]
    username = str(body[0:username_size], 'utf-8')
    data = body[username_size:]
    return {
        "username_size": username_size,
        "data_size": data_size,
        "flags": flags,
        "username": username,
        "data": data
    }

def save_image(img, filename, save_path: str | io.BytesIO):
    """
    From https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array:
    'format="jpg" saving to bytes does not work while "jpeg" works for both files and bytes and "jpg" works for files only.'
    """
    ext = filename.split('.')[-1]
    if isinstance(save_path, io.BytesIO):
        if ext == "jpg" or ext =="jpeg":
            ext = "jpeg"
        img.save(save_path, ext)
        return
    elif isinstance(save_path, str):
        if ext == "jpg" or ext == "jpeg": # <- Instead of figuring out what kind of file I've been given, which I could
            img = img.convert('RGB')      # totally do, I'm going to treat the file like whatever file extension says
        if filename in save_path:         # the file is....at least for now.
            img.save(save_path)
        else:
            img.save(os.path.join(save_path, filename))
        return True
    else:
        return False

