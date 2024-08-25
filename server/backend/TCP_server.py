"""
TCP server
Written by Joshua Kitchen - 2023
"""
import logging
import os
import csv
import threading

from TCPLib.tcp_server import TCPServer
from TCPLib.internals.utils import encode_msg, decode_header

logger = logging.getLogger(__name__)


class PychatServer(TCPServer):
    def __init__(self, host: str, port: int, buff_size=4096, max_clients=16, max_userid_len=16, timeout=None):
        TCPServer.__init__(self, host, port, max_clients, timeout)
        self._max_userid_len = max_userid_len
        self._blacklist_path = ".ipblacklist"
        self._ip_blacklist = []
        self._buff_size = buff_size
        self._user_names = {}
        self._user_names_lock = threading.Lock()

        if self._max_userid_len <= 0 or not isinstance(self._max_userid_len, int):
            raise ValueError("max_userid_len must be a non-zero, positive integer")

        if self.load_ip_blacklist(self._blacklist_path) is False:
            logging.warning(f"Could not find {self._blacklist_path}")
            self._blacklist_path = "../.ipblacklist"

    def _on_connect(self, *args, **kwargs):
        client_soc = args[0]
        client_id = args[1]
        header = client_soc.recv(5)
        size, flags = decode_header(header)
        if size >= 256:
            return False
        username = client_soc.recv(size)
        username = bytes.decode(username, "utf-8")
        if self.is_username_taken(username):
            logger.debug("Username was taken")
            client_soc.sendall(encode_msg(b"USERNAME TAKEN", 2))
            return False
        else:
            logger.debug("Username was available")
            members = ','.join(self.get_usernames())
            self.register_username(username, client_id)
            client_soc.sendall(encode_msg(bytes(f"MEMBERS:{members}", "utf-8"), 2))
            self.broadcast_msg(bytes(f"JOINED:{username}", "utf-8"))

    def is_username_taken(self, username):
        self._user_names_lock.acquire()
        if username in self._user_names.keys():
            result = True
        else:
            result = False
        self._user_names_lock.release()
        return result

    def register_username(self, username, client_id):
        self._user_names_lock.acquire()
        self._user_names.update({username: client_id})
        self._user_names_lock.release()

    def get_usernames(self):
        self._user_names_lock.acquire()
        usernames = self._user_names.keys()
        self._user_names_lock.release()
        return usernames

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

    def broadcast_msg(self, msg: bytes):
        for client_id in self.list_clients():
            self.send(client_id, msg)

    def process_msg_queue(self):
        while self.is_running():
            msg = self.pop_msg(block=True)
            if msg.flags == 2:  # Data
                self.broadcast_msg(msg.data)
            elif msg.flags == 4:  # Disconnect
                self.disconnect_client(msg.client_id, warn=False)
