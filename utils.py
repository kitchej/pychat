"""
PYCHAT APPLICATION PROTOCOL

 ------------------------ HEADER ----------------------------  -- MSG BODY --
|                                                            |               |
|                                                            |               |
[username_size (4 bytes)][data_size (4 bytes)][flags (1 byte)][username][data]

FLAGS:
    1 = Text
    2 = Image
    4 = Information
"""


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
