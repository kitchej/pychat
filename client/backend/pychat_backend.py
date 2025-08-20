"""
pychat_backend.py
Written by Joshua Kitchen - 2024

PYCHAT APPLICATION MESSAGE STRUCTURE

 ------------------------ HEADER ----------------------------  -- MSG BODY --
|                                                            |               |
|                                                            |               |
[username_size (4 bytes)][data_size (4 bytes)][flags (1 byte)][username][data]

FLAGS:
    1 = Text
    2 = Multimedia
    4 = Information
    8 = Disconnect

If the message is a multimedia message, an additional header is included in the message body (flags should always be 2):
[Filename Length (4 bytes)][Filename]

The information flag is used when the server and the client need to pass along information.
Possible info messages are:
- JOINED:<user id>
- LEFT:<user id>
- MEMBERS:<list of connected users>
- KICKED:<no message body>
- SERVERMSG:<message>
"""
import logging
import socket

from TCPLib.tcp_client import TCPClient
import client.backend.exceptions as exc
import utils

logger = logging.getLogger(__name__)


class PychatClient:
    """
    Backend for the pychat client.
    """
    def __init__(self, window, timeout):
        self.tcp_client = TCPClient(timeout=timeout)
        self.window = window
        self.username = ""

    def send_chat_msg(self, data: bytes, flags: int):
        return self.tcp_client.send(utils.encode_msg(bytes(self.username, 'utf-8'), data, flags))

    def send_multimedia_msg(self, filename, data):
        """
        Additional multimedia message header included in the message body:
        [Filename Length (4 bytes)][Filename]
        """
        msg = bytearray()
        msg.extend(len(filename).to_bytes(4, byteorder="big"))
        msg.extend(bytes(filename, "utf-8"))
        msg.extend(data)
        return self.send_chat_msg(msg, flags=2)

    def set_username(self, username):
        self.username = username

    def is_connected(self):
        return self.tcp_client.is_connected

    def init_connection(self, addr):
        """
        Overview of the handshake that takes place between the server and the client:
            1.) Client sends it's requested username
            2.) The server can respond in four ways:
                     a.) "USERNAME TAKEN" if requested username is taken
                     b.) "USERNAME TOO LONG" if requested usernames exceeds 256 characters
                     c.) "SERVER IS FULL" if the server cannot accept any more connections
                     d.) "MEMBERS:" along with a list of all other users in the chatroom if
                          all other checks have passed.
            3.) If the server response is "USERNAME TAKEN", "USERNAME TOO LONG", or "SERVER IS FULL" the connection is
                immediately closed by the server.

        This method raises an exception if any of the checks fail or there was a problem. See exceptions.py for a
        list of exceptions specific to this app.
        """
        try:
            self.tcp_client.connect(addr)
        except ConnectionError:
            return False
        except ValueError: # Bad address
            return False
        except socket.gaierror: # Unresolvable address
            return False
        self.tcp_client.send(bytes(self.username, "utf-8"))
        server_response = self.tcp_client.receive()
        server_response = bytearray.decode(server_response, "utf-8")
        logger.debug(f"Server Response={server_response}")
        if server_response == "USERNAME TAKEN":
            self.tcp_client.disconnect()
            raise exc.UserIDTaken()
        elif server_response == "USERNAME TOO LONG":
            self.tcp_client.disconnect()
            raise exc.UserIDTooLong()
        elif server_response == "SERVER IS FULL":
            self.tcp_client.disconnect()
            raise exc.ServerFull()
        elif server_response[0:8] == "MEMBERS:":
            self.window.create_member_list(server_response[8:])
            return True
        else:
            self.tcp_client.disconnect()
            return False

    def disconnect(self):
        self.tcp_client.disconnect()
        self.window.show_disconnect_msg()

    def msg_loop(self):
        while self.tcp_client.is_connected:
            try:
                msg = self.tcp_client.receive()
            except ConnectionError:
                self.disconnect()
                return
            if msg == b'':
                self.disconnect()
                return
            msg_contents = utils.decode_msg(msg)
            logger.debug(f"MESSAGE FROM {msg_contents['username']}:"
                          f"    DATA SIZE: {msg_contents['data_size']}"
                          f"        FLAGS: {msg_contents['flags']}")
            if msg_contents['flags'] == 1:
                self.window.process_msg(msg_contents['username'], str(msg_contents['data'], 'utf-8'))
            elif msg_contents['flags'] == 2:
                self.window.process_multimedia_msg(msg_contents['username'], msg_contents['data'])
            elif msg_contents['flags'] == 4:
                self.window.process_info_msg(str(msg_contents['data'], 'utf-8'))
            elif msg_contents['flags'] == 8:
                self.tcp_client.disconnect()

