"""
TCP client for Pychat
Written by Joshua Kitchen - 2023

NOTES:
    - Only ipv4 is supported (for now)
    - NULL is used to separate messages. It is also used to mark the end of transmission.
    - Normal messages sent between clients have this format: [sender]\n[message]\0
        - Since a newline is used as a delimiter, it is important to ensure that any newlines are stripped from messages
        before transmission.
    - Informational messages always have INFO as the sender. These messages are processed differently by the client.
        - Informational messages have this format: INFO\n[header]:[message]\0
"""
import socket
import threading
import logging

from backend.exceptions import UserIDTaken, ServerFull, UserIDTooLong


class TCPClient:
    def __init__(self, window):
        logging.basicConfig(filename=".client_log", level=logging.DEBUG,
                            format="%(asctime)s - %(levelname)s: %(message)s",
                            datefmt="%m/%d/%Y %I:%M:%S %p")
        self.window = window
        self.host = "127.0.0.1"
        self.port = 5000
        self.buff_size = 4096
        self.soc = None
        self.is_connected = False
        self.timeout = 10
        self.user_id = ""

    def init_connection(self, host, port, user_id):
        self.host = host
        self.port = int(port)
        self.user_id = user_id
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.settimeout(self.timeout)
        self.is_connected = True
        logging.info(f"Connecting to {self.host} at port {self.port}")
        try:
            self.soc.connect((self.host, self.port))
        except TimeoutError as e:
            self.close_connection()
            logging.debug("Connection timed out")
            return e
        except ConnectionRefusedError as e:
            self.close_connection()
            logging.debug("Connection was refused")
            return e
        except socket.gaierror as e:
            self.close_connection()
            logging.exception("Could not connect")
            return e
        logging.info(f"Connected to {self.host} at port {self.port}")
        self.soc.settimeout(None)
        server_response = self.receive()
        logging.debug(f"server_response = {bytes(server_response, 'utf-8')}")
        server_response = server_response.strip('\0')
        if server_response == "SERVER FULL":
            self.is_connected = False
            logging.debug(f"Denied connection due to server being full")
            return ServerFull()
        if server_response == "SEND USER ID":
            self.send(self.user_id)
            server_response = self.receive()
            server_response = server_response.strip('\0')
            if server_response == "USERID TAKEN":
                self.is_connected = False
                logging.debug(f"Denied connection due to provided user_id being taken | user_id = {user_id}")
                return UserIDTaken()
            elif server_response == "USERID TOO LONG":
                self.is_connected = False
                logging.debug(f"Denied connection due to provided user_id being too long | user_id = {user_id}")
                return UserIDTooLong()
            elif server_response == "CONNECTING":
                threading.Thread(target=self.receive_loop).start()
                logging.info(f"Handshake complete, starting receive loop")
                return True

    def close_connection(self):
        if self.soc is not None:
            self.soc.close()
            logging.info(f"Disconnected from host at {self.host} at port {self.port}")
            self.soc = None
            self.is_connected = False
            self.host = None
            self.port = None

            return True
        return False

    def send(self, msg):
        msg = bytes(msg.strip('\n') + '\0', 'utf-8')
        try:
            self.soc.sendall(msg)
            logging.debug(f"Sent a message: {msg}")
        except ConnectionResetError:
            self.is_connected = False
            return False
        except ConnectionAbortedError:
            self.is_connected = False
            return False
        except OSError:
            self.is_connected = False
            return False
        return True

    def receive(self):
        msg = ""
        while True:
            try:
                data = self.soc.recv(self.buff_size)
            except ConnectionResetError:
                return None
            except ConnectionAbortedError:
                return None
            if data[-1] == 0:
                msg = msg + data.decode()
                return msg
            msg = msg + data.decode()

    def receive_loop(self):
        logging.info("Receive loop started")
        while True:
            msg = self.receive()
            if msg is None:
                return
            logging.debug(f"RECEIVED: {bytes(msg, 'utf-8')}")
            msg = msg.split('\0')
            for m in msg:
                if m == '' or m == '\0':
                    continue
                m = m.split('\n')
                sender = m[0]
                message = m[1]
                if sender == "INFO":
                    self.window.process_info_msg(message)
                else:
                    self.window.process_msg(sender, message)
