"""
Client Processor
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
import logging
logging.getLogger(__name__)


class ClientProcessor:
    """Manges a specific Pychat client"""
    def __init__(self, server_obj, addr, port, soc, buff_size):
        self.server_obj = server_obj
        self.addr = addr
        self.port = port
        self.soc = soc
        self.user_id = None
        self.buff_size = buff_size

    def _init_connection(self):
        """
        Once a TCP connection has been established, this class and the TCPClient initiate a higher level
        handshake.

        On the server side, this handshake is as follows and all messages are sent with 'HANDSHAKE' as the header:
        - Receive the client's user id
            - If the user id is too long, send back 'USERID TOO LONG'
            - If the user id is taken, send back 'USERID TAKEN'
            - If the server is full, send back 'SERVER FULL'
        - If the above checks pass, send back 'HANDSHAKE COMPLETE'
        """
        user_id = self.receive_msg()
        if user_id is None:
            self.soc.close()
            logging.info(f"Client at {self.addr} at port {self.port} closed connection")
            return False
        user_id = user_id.strip('\0').split("\n")[1]

        if len(user_id) > self.server_obj.max_userid_len():
            self.send_msg("USERID TOO LONG", "HANDSHAKE")
            self.soc.close()
            logging.debug(f"Client at {self.addr} at port {self.port} was denied connection because it's username was "
                          f"too long")
            return False
        elif user_id in self.server_obj.get_connected_clients().keys():
            self.send_msg("USERID TAKEN", "HANDSHAKE")
            self.soc.close()
            logging.debug(f"Client at {self.addr} at port {self.port} was denied connection because the username "
                          f"requested was taken. USERNAME: {user_id}")
            return False
        elif self.server_obj.server_capacity():
            self.send_msg("SERVER FULL", "HANDSHAKE")
            self.soc.close()
            logging.debug(f"Client at {self.addr} on port {self.port} was denied connection due to "
                          f"the server being full")
            return False
        else:
            self.send_msg("HANDSHAKE COMPLETE", "HANDSHAKE")
            logging.debug(f"Client at {self.addr} at port {self.port} has completed the handshake")
            self.user_id = user_id
            self.server_obj.update_connected_clients(self)
            if self.server_obj.server_capacity():
                logging.warning(f"Server is at full capacity")
            client_list = ','.join(self.server_obj.get_connected_clients())
            self.send_msg(f"MEMBERS:{client_list}", "INFO")
            self.server_obj.broadcast_msg(f"JOINED:{self.user_id}", "INFO")
            return True

    def send_msg(self, msg: str, header: str):
        data = bytes(f"{header}\n{msg}\0", 'utf-8')
        try:
            self.soc.sendall(data)
        except ConnectionResetError:
            return False
        except ConnectionAbortedError:
            return False
        logging.debug(f"Sent a message: {data}")
        return True

    def receive_msg(self):
        msg = ""
        while True:
            try:
                data = self.soc.recv(self.buff_size)
            except ConnectionResetError:
                return None
            except ConnectionAbortedError:
                return None
            except OSError as e:
                logging.debug(f"Exception occurred while receiving from {self.addr} at port {self.port}\n{e}")
                return None
            try:
                if data[-1] == 0:
                    msg = msg + data.decode()
                    return msg
                msg = msg + data.decode()
            except IndexError:
                return None

    def process_client(self):
        result = self._init_connection()
        if not result:
            return
        while self.server_obj.is_running():
            msg = self.receive_msg()
            if msg is None:
                self.server_obj.disconnect_client(self.user_id)
                return
            logging.debug(f"Message from {self.user_id}: {bytes(msg, 'utf-8')}")
            msg = msg.strip('\0').split('\n')
            if msg[0] == "INFO":
                if msg[1] == "LEAVING":
                    self.server_obj.disconnect_client(self.user_id)
            else:
                self.server_obj.broadcast_msg(msg[1], self.user_id)
