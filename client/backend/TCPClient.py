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
        self.is_connecting = False
        self.timeout = 10
        self.user_id = ""

    def init_connection(self, host, port, user_id):
        self.host = host
        self.port = int(port)
        self.user_id = user_id
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.settimeout(self.timeout)
        self.is_connecting = True
        try:
            self.soc.connect((self.host, self.port))
        except TimeoutError as e:
            self.soc.close()
            self.soc = None
            self.host = None
            self.port = None
            self.is_connecting = False
            return e
        except socket.gaierror as e:
            self.soc.close()
            self.soc = None
            self.host = None
            self.port = None
            self.is_connecting = False
            return e

        self.soc.settimeout(None)
        msg = ""
        while True:
            try:
                data = self.soc.recv(self.buff_size)
            except ConnectionResetError as e:
                self.is_connecting = False
                return e
            except ConnectionAbortedError as e:
                self.is_connecting = False
                return e
            if data[-1] == 0:
                msg = msg + data.decode()
                print(f"HANDSHAKE: {bytes(msg, 'utf-8')}")
                msg = msg.strip('\0')
                if msg == "SERVER FULL":
                    self.is_connecting = False
                    return ServerFull()
                if msg == "SEND USER ID":
                    self.soc.sendall(bytes(self.user_id + '\0', 'utf-8'))
                    msg = ""
                    while True:
                        try:
                            data = self.soc.recv(self.buff_size)
                        except ConnectionResetError as e:
                            self.is_connecting = False
                            return e
                        except ConnectionAbortedError as e:
                            self.is_connecting = False
                            return e
                        if data[-1] == 0:
                            msg = msg + data.decode()
                            print(f"HANDSHAKE: {bytes(msg, 'utf-8')}")
                            msg = msg.strip('\0')
                            if msg == "USERID TAKEN":
                                self.is_connecting = False
                                return UserIDTaken()
                            elif msg == "USERID TOO LONG":
                                self.is_connecting = False
                                return UserIDTooLong()
                            elif msg == "CONNECTING":
                                print("Connecting")
                                threading.Thread(target=self.receive).start()
                                self.is_connecting = False
                                return True
            msg = msg + data.decode()

    def send(self, msg):
        msg = msg.strip('\n')
        self.soc.sendall(bytes(msg + '\0', 'utf-8'))

    def receive(self):
        print("Receiving...")
        while True:
            msg = ""
            while True:
                try:
                    data = self.soc.recv(self.buff_size)
                    print(f"DATA: {bytes(data)}")
                except ConnectionResetError:
                    print("Connection terminated")
                    return
                except ConnectionAbortedError:
                    print("Connection terminated")
                    return
                if data[-1] == 0:
                    msg = msg + data.decode()
                    print(f"RECEIVED: {bytes(msg, 'utf-8')}")
                    msg = msg.split('\0')
                    print(f"msg = {msg}")
                    for m in msg:
                        print(f"m = {m}")
                        if m == '' or m == '\0':
                            continue
                        m = m.split('\n')
                        sender = m[0]
                        message = m[1]
                        if sender == "INFO":
                            self.window.process_info_msg(message)
                        else:
                            self.window.process_msg(sender, message)
                    break
                msg = msg + data.decode()
