"""
TCP server (for pychat)
Written by Joshua Kitchen - 2023

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
import os
import csv
import threading

from TCPLib.tcp_server import TCPServer
import utils

logger = logging.getLogger(__name__)


class PychatServer(TCPServer):
    def __init__(self, buff_size=4096, max_clients=16, max_userid_len=16, timeout=None, ip_blacklist_path=".ipblacklist"):
        TCPServer.__init__(self, max_clients, timeout)
        self._max_userid_len = max_userid_len
        self._blacklist_path = ip_blacklist_path
        self._ip_blacklist = []
        self._buff_size = buff_size
        self._user_names = {}
        self._user_names_lock = threading.Lock()
        self._on_connect = self.on_connect

        if self._max_userid_len <= 0 or not isinstance(self._max_userid_len, int):
            raise ValueError("max_userid_len must be a non-zero, positive integer")

        if not self.load_ip_blacklist(self._blacklist_path):
            logging.warning(f"Could not load {self._blacklist_path}")

    def on_connect(self, client, client_id):
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
        username = str(client.receive(), encoding="utf-8")
        if self.is_username_taken(username):
            logger.debug(f"Connection to {client.peer_addr} was denied because its username was taken")
            client.send(b"USERNAME TAKEN")
            return False
        elif self.is_full:
            logger.debug(f"Connection to {client.peer_addr} was denied due to server being full")
            client.send(b"SERVER IS FULL")
            return False
        elif len(username) > 256:
            logger.debug(f"Connection to {client.peer_addr} was denied due to server being full")
            client.send(b"USERNAME TOO LONG")
            return False
        else:
            members = ','.join(self.list_usernames())
            self.register_username(username, client_id)
            client.send(bytes(f"MEMBERS:{members}", "utf-8"))
            self.broadcast_msg(utils.encode_msg(bytes(username, 'utf-8'), bytes(f"JOINED:{username}", "utf-8"), 4))
            return True

    def is_username_taken(self, username):
        with self._user_names_lock:
            if username in self._user_names.values() or username == "SERVER":
                return True
            else:
                return False

    def register_username(self, username, client_id):
        with self._user_names_lock:
            self._user_names.update({client_id: username})


    def unregister_username(self, client_id):
        with self._user_names_lock:
            try:
                del self._user_names[client_id]
            except KeyError:
                return False
            return True

    def list_usernames(self):
        with self._user_names_lock:
            usernames = self._user_names.values()
            return usernames

    def get_username(self, client_id):
        with self._user_names_lock:
            try:
                username = self._user_names[client_id]
            except KeyError:
                return
            return username

    def save_ip_blacklist(self):
        with open(self._blacklist_path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(self._ip_blacklist)

    def load_ip_blacklist(self, path):
        if os.path.exists(path):
            with open(path, "r") as file:
                for row in csv.reader(file):
                    self._ip_blacklist.extend(row)
            return True
        elif path == ".ipblacklist":
            # If path is the default value, just create the file if it doesn't exist
            with open(path, 'a'):
                pass
            return True
        return False

    def max_userid_len(self):
        return self._max_userid_len

    def get_ip_blacklist(self):
        return self._ip_blacklist

    def blacklist_ip(self, ip_address: str):
        self._ip_blacklist.append(ip_address)

    def un_blacklist_ip(self, ip_address: str):
        if ip_address in self._ip_blacklist:
            self._ip_blacklist.remove(ip_address)
            return True
        return False

    def broadcast_msg(self, msg: bytes, flags: int = 1, is_server_msg: bool = False):
        if is_server_msg:
            for client_id in self.list_clients():
                self.send(client_id, utils.encode_msg(b"SERVER", msg, flags))
        else:
            for client_id in self.list_clients():
                self.send(client_id, msg)

    def process_msg_queue(self):
        while self.is_running:
            msg = self.pop_msg(block=True)
            if msg is None: # Queue was empty
                continue
            username = self.get_username(msg.client_id)
            if msg.size == 0: # Connection was closed
                self.unregister_username(msg.client_id)
                self.broadcast_msg(utils.encode_msg(b"", bytes(f"LEFT:{username}", "utf-8"), 4))
                continue
            msg_info = utils.decode_msg(msg.data)
            client_info = self.get_client_attributes(msg.client_id)
            logger.debug(f"MESSAGE FROM {username}@({client_info['addr'][0]}, {client_info['addr'][1]}):\n"
                         f"    DATA SIZE: {msg_info['data_size']}\n"
                         f"        FLAGS: {msg_info['flags']}\n")
            if msg_info["flags"] == 8:
                self.unregister_username(msg.client_id)
                self.disconnect_client(msg.client_id)
                self.broadcast_msg(utils.encode_msg(b"", bytes(f"LEFT:{username}", "utf-8"), 4))
            else:
                self.broadcast_msg(msg.data)
