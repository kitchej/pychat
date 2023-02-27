"""
TCP server for Pychat
Written by Joshua Kitchen - 2023

NOTES:
    - Only ipv4 is supported (for now)
    - NULL is used to separate messages. It is also used to mark the end of transmission.
    - Normal messages sent between clients have this format: [sender]\n[message]\0
        - Since a newline is used as a delimiter, it is important to ensure that any newlines are stripped from messages
        before transmission.
    - Informational messages always have INFO as the sender. These messages are processed differently by the client.
        - Informational messages have this format: INFO\n[header]:[message]\0

TODO:
    - Encapsulate all send functionality into one function
"""
import logging
import socket
import threading
import time


class ClientInfo:
    def __init__(self, addr, port, soc, user_id):
        self.addr = addr
        self.port = port
        self.soc = soc
        self.user_id = user_id



class TCPServer:
    """A TCP server for pychat"""
    def __init__(self, host, port, buff_size=4096, max_clients=16, max_userid_len=16, debug_mode=False):
        if debug_mode:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        logging.basicConfig(filename="server_log", level=log_level,
                            format="%(asctime)s - %(levelname)s: %(message)s",
                            datefmt="%m/%d/%Y %I:%M:%S %p")

        self.black_listed_ips = []
        self.host = host
        self.port = port
        self.buff_size = buff_size
        self.max_clients = max_clients
        self.max_userid_len = max_userid_len
        self.is_running = False

        if self.port < 1024 or self.port > 65535:
            raise ValueError("Port must be between 1024 and 65535")

        if self.buff_size <= 0 or not isinstance(self.buff_size, int):
            raise ValueError("buff_size must be a non-zero, positive integer")

        if self.max_clients <= 0 or not isinstance(self.max_clients, int):
            raise ValueError("max_clients must be a non-zero, positive integer")

        if self.max_userid_len <= 0 or not isinstance(self.max_userid_len, int):
            raise ValueError("max_userid_len must be a non-zero, positive integer")

        self.client_count = 0
        self.soc = None
        self.connected_clients = {}
        self.client_dict_lock = threading.Lock()

    def start_server(self):
        if not self.is_running:
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.bind((self.host, self.port))
            threading.Thread(target=self.__mainloop).start()
            self.is_running = True

    def close_server(self):
        if self.is_running:
            self.soc.close()
            self.soc = None
            self.is_running = False

    def black_list_ip(self, ip_address):
        self.black_listed_ips.append(ip_address)

    def un_blacklist_ip(self, ip_address):
        if ip_address in self.black_listed_ips:
            self.black_listed_ips.remove(ip_address)

    def get_connected_clients(self):
        self.client_dict_lock.acquire()
        clients = self.connected_clients
        self.client_dict_lock.release()
        return clients

    def disconnect_client(self, user_id):
        self.client_dict_lock.acquire()
        client = self.connected_clients[user_id]
        del self.connected_clients[user_id]
        self.client_count -= 1
        self.client_dict_lock.release()

        client.soc.close()
        logging.info(f"Client: {client.addr} closed connection")
        self.broadcast_msg(f"left:{user_id}", "INFO")

    def send_msg(self, msg, sender, recipient):
        packet = f"{sender}\n{msg}\0"
        self.connected_clients[recipient].soc.sendall(bytes(packet, 'utf-8'))
        logging.debug(f"Sent a message: {bytes(packet, 'utf-8')}")

    def broadcast_msg(self, msg, sender):
        packet = f"{sender}\n{msg}\0"
        self.client_dict_lock.acquire()
        for client in self.connected_clients.values():
            client.soc.sendall(bytes(packet, 'utf-8'))
        self.client_dict_lock.release()
        logging.debug(f"Broadcast a message: {bytes(packet, 'utf-8')}")

    def receive_msg(self, soc):
        msg = ""
        while True:
            try:
                data = soc.recv(self.buff_size)
            except ConnectionResetError:
                return None
            except ConnectionAbortedError:
                return None
            if data[-1] == 0:
                msg = msg + data.decode()
                return msg
            msg = msg + data.decode()

    def __process_client(self, client_info):
        logging.info(f"Connected to {client_info.addr} at port {client_info.port} | user_id = {client_info.user_id}")
        time.sleep(0.1)  # Buys the client some time to initialize itself before we start sending it stuff
        client_list = ','.join(self.connected_clients.keys())
        self.send_msg(f"members:{client_list}", "INFO", client_info.user_id)
        self.broadcast_msg(f"joined:{client_info.user_id}", "INFO")

        while True:
            msg = self.receive_msg(client_info.soc)
            if msg is None:
                self.client_dict_lock.acquire()
                if client_info not in self.connected_clients.values():
                    return
                else:
                    del self.connected_clients[client_info.user_id]
                    self.client_count -= 1
                self.client_dict_lock.release()
                self.broadcast_msg(f"left:{client_info.user_id}", "INFO")
                client_info.soc.close()
                logging.info(f"Client: {client_info.addr} closed connection")
                return
            logging.debug(f"Message from {client_info.user_id}: {bytes(msg, 'utf-8')}")
            self.broadcast_msg(msg.strip('\0'), client_info.user_id)

    def __check_client_connections(self, interval: float):  # interval is in seconds
        while True:
            time.sleep(interval)
            self.client_dict_lock.acquire()
            for client_id in self.connected_clients.keys():
                client = self.connected_clients[client_id]
                try:
                    client.soc.sendall(bytes("INFO\n\0", 'utf-8'))
                except ConnectionResetError:
                    self.connected_clients[client_id].soc.close()
                    logging.info(f"Client: {client.addr} closed connection")
                    del self.connected_clients[client_id]
                except ConnectionAbortedError:
                    self.connected_clients[client_id].soc.close()
                    logging.info(f"Client: {client.addr} closed connection")
                    del self.connected_clients[client_id]
                except OSError:  # socket was closed
                    return
            self.client_dict_lock.release()

    def __mainloop(self):
        logging.info("Server started")
        threading.Thread(target=self.__check_client_connections, args=[30.0]).start()
        while True:
            logging.debug("Listening for new connections...")
            try:
                self.soc.listen()
                client_soc, client_addr = self.soc.accept()
            except OSError:  # socket was closed
                logging.info("Server shutdown")
                return
            self.client_dict_lock.acquire()
            self.client_dict_lock.release()
            if self.client_count == self.max_clients:
                client_soc.sendall(b'SERVER FULL\x00')
                client_soc.close()
                logging.debug(f"Client at {client_addr} was denied connection due to the server being full")
                continue
            else:
                client_soc.sendall(b'SEND USER ID\x00')
            while True:
                user_id = self.receive_msg(client_soc)
                if user_id is None:
                    client_soc.close()
                    logging.info(f"Client at {client_addr} closed connection")
                    return
                user_id = user_id.strip('\0')
                if user_id in self.connected_clients.keys():
                    client_soc.sendall(b'USERID TAKEN\x00')
                    client_soc.close()
                    logging.debug(f"Client at {client_addr} was denied connection because the username requested "
                                  f"was taken. USERNAME: {user_id}")
                    break
                elif len(user_id) > self.max_userid_len:
                    client_soc.sendall(b'USERID TOO LONG\x00')
                    client_soc.close()
                    logging.debug(f"Client at {client_addr} was denied connection because it's username was too long")
                    break
                else:
                    client_soc.sendall(b'CONNECTING\x00')
                    logging.debug(f"Client at {client_addr} has completed the handshake")
                    client_info = ClientInfo(client_addr[0], client_addr[1], client_soc, user_id)
                    self.client_dict_lock.acquire()
                    self.connected_clients.update({user_id: client_info})
                    self.client_count += 1
                    self.client_dict_lock.release()
                    if self.client_count == self.max_clients:
                        logging.warning(f"Server is at full capacity | {self.client_count}/{self.max_clients}")
                    threading.Thread(target=self.__process_client, args=[client_info]).start()
                    break
