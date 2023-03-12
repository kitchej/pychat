"""
TCP server for Pychat
Written by Joshua Kitchen - 2023
"""
import logging
import socket
import threading
import os
import csv

from client_processor import ClientProcessor

logging.getLogger(__name__)


class TCPServer:
    """A TCP server for pychat"""
    def __init__(self, host, port, buff_size=4096, max_clients=16, max_userid_len=16, blacklist_path=".ipblacklist"):
        self.__is_running = False
        self.__host = host
        self.__port = port
        self.__buff_size = buff_size
        self.__max_clients = max_clients
        self.__max_userid_len = max_userid_len
        self.__blacklist_path = blacklist_path
        self.__ip_blacklist = []

        if self.__port < 1024 or self.__port > 65535:
            raise ValueError("Port must be between 1024 and 65535")

        if self.__buff_size <= 0 or not isinstance(self.__buff_size, int):
            raise ValueError("buff_size must be a non-zero, positive integer")

        if self.__max_clients <= 0 or not isinstance(self.__max_clients, int):
            raise ValueError("max_clients must be a non-zero, positive integer")

        if self.__max_userid_len <= 0 or not isinstance(self.__max_userid_len, int):
            raise ValueError("max_userid_len must be a non-zero, positive integer")

        if self.load_ip_blacklist(self.__blacklist_path) is False:
            logging.warning(f"Could not find {self.__blacklist_path}")
            self.__blacklist_path = ".ipblacklist"

        self.__soc = None
        self.__connected_clients = {}
        self.__connected_clients_lock = threading.Lock()

    def server_full(self):
        if len(self.get_connected_clients().values()) == self.__max_clients:
            return True
        return False

    def get_max_userid_len(self):
        return self.__max_userid_len

    def is_running(self):
        return self.__is_running

    def update_connected_clients(self, client):
        self.__connected_clients_lock.acquire()
        self.__connected_clients.update({client.user_id: client})
        self.__connected_clients_lock.release()

    def get_connected_clients(self):
        self.__connected_clients_lock.acquire()
        clients = self.__connected_clients
        self.__connected_clients_lock.release()
        return clients

    def disconnect_client(self, user_id, send_kicked_msg=False):
        self.__connected_clients_lock.acquire()
        try:
            client = self.__connected_clients[user_id]
        except KeyError:
            self.__connected_clients_lock.release()
            return False
        if send_kicked_msg:
            try:

                client.soc.sendall(b'INFO\nKICKED\x00')
            except ConnectionResetError:
                pass
            except ConnectionAbortedError:
                pass
        del self.__connected_clients[user_id]
        self.__connected_clients_lock.release()
        client.soc.close()
        logging.info(f"Client at {client.addr} on port {client.port} was disconnected")
        self.broadcast_msg(f"left:{user_id}", "INFO")
        return True

    def start_server(self):
        if not self.__is_running:
            self.__soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__soc.bind((self.__host, self.__port))
            self.__is_running = True
            threading.Thread(target=self.__mainloop).start()

    def close_server(self):
        if self.__is_running:
            self.__soc.close()
            self.__soc = None
            self.__is_running = False
            self.__connected_clients_lock.acquire()
            for client in self.__connected_clients.values():
                client.soc.close()
            self.__connected_clients.clear()
            self.__connected_clients_lock.release()

    def black_list_ip(self, ip_address):
        self.__ip_blacklist.append(ip_address)

    def un_blacklist_ip(self, ip_address):
        print(self.__ip_blacklist)
        if ip_address in self.__ip_blacklist:
            self.__ip_blacklist.remove(ip_address)
            return True
        return False

    def get_ip_blacklist(self):
        return self.__ip_blacklist

    def save_ip_blacklist(self):
        with open(self.__blacklist_path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(self.__ip_blacklist)

    def load_ip_blacklist(self, path):
        if os.path.exists(path):
            with open(path, "r") as file:
                for row in csv.reader(file):
                    self.__ip_blacklist.extend(row)
            return True
        return False

    def broadcast_msg(self, msg, header):
        data = bytes(f"{header}\n{msg}\0", "utf-8")
        self.__connected_clients_lock.acquire()
        for client in self.__connected_clients.values():
            try:
                client.soc.sendall(data)
            except ConnectionResetError:
                continue
            except ConnectionAbortedError:
                continue
        self.__connected_clients_lock.release()
        logging.debug(f"Broadcast a message: {data}")

    def __mainloop(self):
        logging.info("Server started")
        while self.__is_running:
            logging.debug("Listening for new connections...")
            try:
                self.__soc.listen()
                client_soc, client_addr = self.__soc.accept()
            except OSError as e:  # raised because the socket was probably closed
                logging.debug("Exception", exc_info=e)
                logging.info("Server shutdown")
                break
            if client_addr[0] in self.__ip_blacklist:
                logging.debug(f"Client at {client_addr[0]} on port {client_addr[1]} was denied connection due to "
                              f"being on the ip blacklist")
                client_soc.close()
                continue
            processor = ClientProcessor(self, client_addr[0], client_addr[1], client_soc, self.__buff_size)
            threading.Thread(target=processor.process_client).start()
        logging.info("Server shutdown")
