"""
TCP client
Written by Joshua Kitchen - 2023

PYCHAT APPLICATION MESSAGE STRUCTURE

 ------------------------ HEADER ----------------------------  -- MSG BODY --
|                                                            |               |
|                                                            |               |
[username_size (4 bytes)][data_size (4 bytes)][flags (1 byte)][username][data]

FLAGS:
    1 = Text
    2 = Image
    4 = Information

The information flag is used when the server and the client need to pass along information. Messages with this flag
include an additional flag within the message text indicating what kind of information was sent.
Possible info messages are:
- JOINED:<user id>
- LEFT:<user id>
- MEMBERS:<list of connected users>
- KICKED:<no message body>
- SERVERMSG:<message>
"""
import logging

from TCPLib.tcp_client import TCPClient
import client.backend.exceptions as excpt
import utils

logger = logging.getLogger()


class PychatClient(TCPClient):
    def __init__(self, window, timeout):
        TCPClient.__init__(self, timeout=timeout)
        self.window = window
        self.username = ""

    def send_chat_msg(self, data: bytes, flags: int):
        return self.send(utils.encode_msg(bytes(self.username, 'utf-8'), data, flags), 2)

    def set_username(self, username):
        self.username = username

    def init_connection(self):
        result = self.connect()
        if isinstance(result, Exception):
            return result
        elif not result:
            return Exception()
        self.send(bytes(self.username, "utf-8"))
        server_response = self.receive_all()
        server_response = bytearray.decode(server_response.data, "utf-8")
        logger.debug(f"Server Response={server_response}")
        if server_response == "USERNAME TAKEN":
            self.disconnect()
            return excpt.UserIDTaken()
        elif server_response == "USERNAME TOO LONG":
            self.disconnect()
            return excpt.UserIDTooLong()
        elif server_response == "SERVER IS FULL":
            self.disconnect()
            return excpt.ServerFull()
        elif server_response[0:13] == "INFO\nMEMBERS:":
            self.window.create_member_list(server_response[13:])
            return True
        else:
            self.disconnect()
            return Exception()

    def msg_loop(self):
        while self._is_connected:
            msg = self.receive_all()
            if msg.data is None:
                continue
            msg_contents = utils.decode_msg(msg.data)
            logger.debug(f"MESSAGE FROM {msg_contents['username']}:"
                          f"    DATA SIZE: {msg_contents['data_size']}"
                          f"        FLAGS: {msg_contents['flags']}"
                          f"          RAW: {msg.data}")
            if msg_contents['flags'] == 1:
                self.window.process_msg(msg_contents['username'], str(msg_contents['data'], 'utf-8'))
            elif msg_contents['flags'] == 2:
                pass
            elif msg_contents['flags'] == 4:
                self.window.process_info_msg(str(msg_contents['data'], 'utf-8'))

