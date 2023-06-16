"""
TCP client
Written by Joshua Kitchen - 2023

All messages are sent in this format:
    "[header]\n[message]\0"

The HANDSHAKE header is used to identify handshake messages

The INFO header is used when the server and the client need to pass along information. Messages with this header include
an additional header within the message indicating what kind of information was sent. The header and the message are
delimited by a colon. Possible INFO messages are:
- JOINED:<user id>
- LEFT:<user id>
- MEMBERS:<list of connected users>
- LEAVING:<no message body>
- KICKED:<no message body>
- SERVERMSG:<message>

If the header is neither of the above options, then the message is treated as a chat message and broadcast to all
connected clients
"""
import socket
import threading
import logging

from backend.exceptions import UserIDTaken, ServerFull, UserIDTooLong


class TCPClient:
    """Sets up and manages a client connection to the Pychat server"""
    def __init__(self, window):
        logging.basicConfig(filename=".client_log", filemode='w', level=logging.DEBUG,
                            format="%(asctime)s - %(levelname)s: %(message)s",
                            datefmt="%m/%d/%Y %I:%M:%S %p")
        self._host = "127.0.0.1"
        self._port = 5000
        self._buff_size = 4096
        self._soc = None
        self._is_connected = False
        self._timeout = 10
        self._user_id = ""
        self.window = window

    def is_connected(self):
        return self._is_connected

    def get_host_addr(self):
        return self._host, self._port

    def get_user_id(self):
        return self._user_id

    def init_connection(self, host, port, user_id):
        """
        Once a TCP connection has been established, this class and the ClientProcessor class initiate a higher level
        handshake.

        On the client side, this handshake is as follows and all messages are sent with 'HANDSHAKE' as the header:
        - Send the user's chosen user id
            - If the user id is too long, the server will respond with 'USERID TOO LONG'
            - If the user id is taken, the server will respond with 'USERID TAKEN'
            - If the server is full, the server will respond with 'SERVER FULL'
        - If the above checks pass, the server will respond with 'HANDSHAKE COMPLETE'
        """
        self._host = host
        self._port = int(port)
        self._user_id = user_id
        self._soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._soc.settimeout(self._timeout)
        logging.info(f"Connecting to {self._host} at port {self._port}")

        try:
            self._soc.connect((self._host, self._port))
        except TimeoutError as e:
            self.close_connection(force=True)
            logging.debug("Connection timed out")
            return e
        except ConnectionRefusedError as e:
            self.close_connection(force=True)
            logging.debug("Connection was refused")
            return e
        except socket.gaierror as e:
            self.close_connection(force=True)
            logging.exception("Could not connect")
            return e
        self._soc.settimeout(None)
        self._is_connected = True
        logging.info(f"Connected to {self._host} at port {self._port}")

        self.send(self._user_id, "INFO")
        server_response = self.receive()
        if server_response is None:
            return ConnectionRefusedError()

        if server_response == "HANDSHAKE\nUSERID TOO LONG\0":
            self.close_connection(force=True)
            logging.info(f"Denied connection due to provided user_id being too long | user_id = {user_id}")
            return UserIDTooLong()
        elif server_response == "HANDSHAKE\nUSERID TAKEN\0":
            self.close_connection(force=True)
            logging.info(f"Denied connection due to provided user_id being taken | user_id = {user_id}")
            return UserIDTaken()
        if server_response == "HANDSHAKE\nSERVER FULL\0":
            self.close_connection(force=True)
            logging.info(f"Denied connection due to server being full")
            return ServerFull()
        elif server_response == "HANDSHAKE\nHANDSHAKE COMPLETE\0":
            threading.Thread(target=self.receive_loop).start()
            logging.info(f"Handshake complete")
            return True

    def close_connection(self, force=False):
        """
        If force=True, no warning will be given to the server before the connection is closed. Make sure this flag is
        set when disconnecting after an error, or you may enter an infinite loop.
        """
        if self._soc is not None:
            if not force:
                self.send("LEAVING", header="INFO")
            self._soc.close()
            logging.info(f"Disconnected from host {self._host} at port {self._port}")
            self._soc = None
            self._host = None
            self._port = None
            self._is_connected = False
            return True
        return False

    def send(self, msg, header="MESSAGE"):
        msg = msg.strip('\n')
        packet = bytes(f"{header}\n{msg}\0", 'utf-8')
        try:
            self._soc.sendall(packet)
            logging.debug(f"SENT: {packet}")
        except ConnectionResetError:
            self.close_connection(force=True)
            return False
        except ConnectionAbortedError:
            self.close_connection(force=True)
            return False
        except OSError:
            self.close_connection(force=True)
            return False
        return True

    def receive(self):
        msg = ""
        while self.is_connected():
            try:
                data = self._soc.recv(self._buff_size)
            except ConnectionResetError:
                return None
            except ConnectionAbortedError:
                return None
            except OSError:
                logging.exception(f"Exception occurred while receiving from {self._host} at "
                                  f"port {self._port}")
                return None
            try:
                if data[-1] == 0:
                    msg = msg + data.decode()
                    logging.debug(f"RECEIVED: {bytes(msg, 'utf-8')}")
                    return msg
            except IndexError:
                return None
            msg = msg + data.decode()

    def receive_loop(self):
        logging.info("Receive loop started")
        while self.is_connected():
            msg = self.receive()
            if msg is None:
                if self.is_connected():
                    self.close_connection(force=True)
                    self.window.show_error("Host closed connection")
                    return
                else:
                    return
            msg = msg.split('\0')
            for m in msg:
                if m == '' or m == '\0':
                    continue
                m = m.split('\n')
                header = m[0]
                message = m[1]
                if header == "INFO":
                    self.window.process_info_msg(message)
                else:
                    self.window.process_msg(header, message)
