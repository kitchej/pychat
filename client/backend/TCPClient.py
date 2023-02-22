import socket
import threading

from backend.exceptions import UserIDTaken, ServerFull, UserIDTooLong


class TCPClient:
    def __init__(self, window):
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
        try:
            self.soc.connect((self.host, self.port))
        except TimeoutError as e:
            self.soc.close()
            self.soc = None
            self.host = None
            self.port = None
            self.is_connected = False
            return e
        except ConnectionRefusedError as e:
            self.soc.close()
            self.soc = None
            self.host = None
            self.port = None
            self.is_connected = False
            return e
        except socket.gaierror as e:
            self.soc.close()
            self.soc = None
            self.host = None
            self.port = None
            self.is_connected = False
            return e

        self.soc.settimeout(None)
        server_response = self.receive()
        print(f"HANDSHAKE: {bytes(server_response, 'utf-8')}")
        server_response = server_response.strip('\0')
        if server_response == "SERVER FULL":
            self.is_connected = False
            return ServerFull()
        if server_response == "SEND USER ID":
            self.send(self.user_id)
            server_response = self.receive()
            print(f"HANDSHAKE: {bytes(server_response, 'utf-8')}")
            server_response = server_response.strip('\0')
            if server_response == "USERID TAKEN":
                self.is_connected = False
                return UserIDTaken()
            elif server_response == "USERID TOO LONG":
                self.is_connected = False
                return UserIDTooLong()
            elif server_response == "CONNECTING":
                print("Connecting")
                threading.Thread(target=self.receive_loop).start()
                return True

    def close_connection(self):
        if self.soc is not None:
            self.soc.close()
            self.soc = None
            self.is_connected = False
            self.host = None
            self.port = None
            return True
        return False

    def send(self, msg):
        msg = msg.strip('\n')
        try:
            self.soc.sendall(bytes(msg + '\0', 'utf-8'))
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
        print("Receiving...")
        while True:
            msg = self.receive()
            if msg is None:
                return
            print(f"RECEIVED: {bytes(msg, 'utf-8')}")
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
