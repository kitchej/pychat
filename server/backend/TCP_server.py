"""
TCP server for Pychat
Written by Joshua Kitchen - 2023

Listens for, accepts and manages TCP connections
"""
import logging
import socket
import threading
import os
import csv

from client_processor import ClientProcessor

logging.getLogger(__name__)


class TCPServer:
    """Listens for, accepts, and manages TCP connections"""
    def __init__(self, host: str, port: int, buff_size=4096, max_clients=16, max_userid_len=16):
        self._is_running = False
        self._host = host
        self._port = port
        self._buff_size = buff_size
        self._max_clients = max_clients
        self._max_userid_len = max_userid_len
        self._blacklist_path = ".ipblacklist"
        self._ip_blacklist = []

        if self._port < 1024 or self._port > 65535:
            raise ValueError("Port must be between 1024 and 65535")

        if self._buff_size <= 0 or not isinstance(self._buff_size, int):
            raise ValueError("buff_size must be a non-zero, positive integer")

        if self._max_clients <= 0 or not isinstance(self._max_clients, int):
            raise ValueError("max_clients must be a non-zero, positive integer")

        if self._max_userid_len <= 0 or not isinstance(self._max_userid_len, int):
            raise ValueError("max_userid_len must be a non-zero, positive integer")

        if self._load_ip_blacklist(self._blacklist_path) is False:
            logging.warning(f"Could not find {self._blacklist_path}")
            self._blacklist_path = "../.ipblacklist"

        self._soc = None
        self._connected_clients = {}
        self._connected_clients_lock = threading.Lock()

    def _mainloop(self):
        logging.info("Server started")
        while self._is_running:
            logging.debug("Listening for new connections...")
            try:
                self._soc.listen()
                client_soc, client_addr = self._soc.accept()
            except OSError as e:
                logging.debug("Exception", exc_info=e)
                logging.info("Server shutdown")
                break
            if client_addr[0] in self._ip_blacklist:
                logging.debug(f"Client at {client_addr[0]} on port {client_addr[1]} was denied connection due to "
                              f"being on the ip blacklist")
                client_soc.close()
                continue
            processor = ClientProcessor(self, client_addr[0], client_addr[1], client_soc, self._buff_size)
            threading.Thread(target=processor.process_client, daemon=True).start()
        logging.info("Server shutdown")

    def _save_ip_blacklist(self):
        with open(self._blacklist_path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(self._ip_blacklist)

    def _load_ip_blacklist(self, path):
        if os.path.exists(path):
            with open(path, "r") as file:
                for row in csv.reader(file):
                    self._ip_blacklist.extend(row)
            return True
        return False

    def server_capacity(self):
        if len(self.get_connected_clients().values()) == self._max_clients:
            return True
        return False

    def max_userid_len(self):
        return self._max_userid_len

    def is_running(self):
        return self._is_running

    def get_ip_blacklist(self):
        return self._ip_blacklist

    def get_connected_clients(self):
        self._connected_clients_lock.acquire()
        clients = self._connected_clients
        self._connected_clients_lock.release()
        return clients

    def update_connected_clients(self, client: ClientProcessor):
        self._connected_clients_lock.acquire()
        self._connected_clients.update({client.user_id: client})
        self._connected_clients_lock.release()

    def blacklist_ip(self, ip_address: str):
        self._ip_blacklist.append(ip_address)

    def un_blacklist_ip(self, ip_address: str):
        if ip_address in self._ip_blacklist:
            self._ip_blacklist.remove(ip_address)
            return True
        return False

    def disconnect_client(self, user_id: str, send_kicked_msg=False):
        self._connected_clients_lock.acquire()
        try:
            client = self._connected_clients[user_id]
        except KeyError:
            self._connected_clients_lock.release()
            return False
        if send_kicked_msg:
            client.send_msg("KICKED", "INFO")
        del self._connected_clients[user_id]
        self._connected_clients_lock.release()
        client.soc.close()
        logging.info(f"Client at {client.addr} on port {client.port} was disconnected")
        self.broadcast_msg(f"left:{user_id}", "INFO")
        return True

    def start_server(self):
        if not self._is_running:
            self._soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._soc.bind((self._host, self._port))
            self._is_running = True
            threading.Thread(target=self._mainloop).start()

    def close_server(self):
        if self._is_running:
            self._soc.close()
            self._soc = None
            self._is_running = False
            self._connected_clients_lock.acquire()
            for client in self._connected_clients.values():
                client.soc.close()
            self._connected_clients.clear()
            self._connected_clients_lock.release()

    def broadcast_msg(self, msg: str, header: str):
        self._connected_clients_lock.acquire()
        for client in self._connected_clients.values():
            client.send_msg(msg, header)
        self._connected_clients_lock.release()
