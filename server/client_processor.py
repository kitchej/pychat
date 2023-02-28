"""
Client Processor
Written by Joshua Kitchen - 2023
"""
import logging
logging.getLogger(__name__)


class ClientProcessor:
    def __init__(self, server_obj, addr, port, soc, buff_size):
        self.server_obj = server_obj
        self.addr = addr
        self.port = port
        self.soc = soc
        self.user_id = None
        self.buff_size = buff_size

    def send_msg(self, msg: str, header):
        try:
            self.soc.sendall(bytes(f"{header}\n{msg}\0", 'utf-8'))
        except ConnectionResetError:
            return False
        except ConnectionAbortedError:
            return False
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
            except OSError:
                logging.exception(f"Exception occurred while receiving from {self.addr} at "
                                  f"port {self.port}")
                return None
            try:
                if data[-1] == 0:
                    msg = msg + data.decode()
                    return msg
                msg = msg + data.decode()
            except IndexError:  # The message probably didn't get fully sent
                return None

    def __init_connection(self):
        # await user_id
        user_id = self.receive_msg()
        if user_id is None:
            self.soc.close()
            logging.info(f"Client at {self.addr} at port {self.port} closed connection")
            return False
        user_id = user_id.strip('\0').split("\n")[1]

        if len(user_id) > self.server_obj.get_max_userid_len():
            self.send_msg("USERID TOO LONG", "INFO")
            self.soc.close()
            logging.debug(f"Client at {self.addr} at port {self.port} was denied connection because it's username was "
                          f"too long")
            return False
        elif user_id in self.server_obj.get_connected_clients().keys():
            self.send_msg("USERID TAKEN", "INFO")
            self.soc.close()
            logging.debug(f"Client at {self.addr} at port {self.port} was denied connection because the username "
                          f"requested was taken. USERNAME: {user_id}")
            return False
        elif self.server_obj.server_full():
            self.send_msg("SERVER FULL", "INFO")
            self.soc.close()
            logging.debug(f"Client at {self.addr} on port {self.port} was denied connection due to "
                          f"the server being full")
            return False
        else:
            self.send_msg("JOINED", "INFO")
            logging.debug(f"Client at {self.addr} at port {self.port} has completed the handshake")
            self.user_id = user_id
            self.server_obj.update_connected_clients(self)
            if self.server_obj.server_full():
                logging.warning(f"Server is at full capacity")
            return True

    def process_client(self):
        result = self.__init_connection()
        if not result:
            return
        logging.info(f"Connected to {self.addr} at port {self.port} | user_id = {self.user_id}")
        client_list = ','.join(self.server_obj.get_connected_clients())
        self.send_msg(f"members:{client_list}", "INFO")
        self.server_obj.broadcast_msg(f"joined:{self.user_id}", "INFO")
        while self.server_obj.is_running():
            msg = self.receive_msg()
            if msg is None:
                self.server_obj.disconnect_client(self.user_id)
                return
            logging.debug(f"Message from {self.user_id}: {bytes(msg, 'utf-8')}")
            msg = msg.strip('\0')
            msg = msg.split('\n')
            if msg[0] == "INFO":
                if msg[1] == "LEAVING":
                    self.server_obj.disconnect_client(self.user_id)
            else:
                self.server_obj.broadcast_msg(msg[1], self.user_id)
