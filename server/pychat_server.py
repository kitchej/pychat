"""
Server for Pychat
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
import sys
import time

HOST = "127.0.0.1"
PORT = 5000
BUFF_SIZE = 4096

MAX_CLIENTS = 16
MAX_USERID_LEN = 16

CONNECTED_CLIENTS = {}
CLIENT_DICT_LOCK = threading.Lock()


def broadcast_msg(msg, sender):
    packet = f"{sender}\n{msg}\0"
    CLIENT_DICT_LOCK.acquire()
    for client_id in CONNECTED_CLIENTS.keys():
        CONNECTED_CLIENTS[client_id].sendall(bytes(packet, 'utf-8'))
    CLIENT_DICT_LOCK.release()


def send_msg(msg, sender, recipient):
    packet = f"{sender}\n{msg}\0"
    CONNECTED_CLIENTS[recipient].sendall(bytes(packet, 'utf-8'))


def receive_msg(soc):
    msg = ""
    while True:
        try:
            data = soc.recv(BUFF_SIZE)
        except ConnectionResetError:
            return None
        except ConnectionAbortedError:
            return None
        if data[-1] == 0:
            msg = msg + data.decode()
            return msg
        msg = msg + data.decode()


def process_client(client_soc, client_addr, user_id):
    print(f"Connected to {client_addr} | user_id = {user_id}")
    time.sleep(0.1)
    client_list = ','.join(CONNECTED_CLIENTS.keys())
    send_msg(f"members:{client_list}", "INFO", user_id)
    broadcast_msg(f"joined:{user_id}", "INFO")

    while True:
        msg = receive_msg(client_soc)
        if msg is None:
            print(f"Client: {client_addr} closed connection")
            CLIENT_DICT_LOCK.acquire()
            del CONNECTED_CLIENTS[user_id]
            CLIENT_DICT_LOCK.release()
            broadcast_msg(f"left:{user_id}", "INFO")
            client_soc.close()
            return
        print(f"Message from {user_id}: {bytes(msg , 'utf-8')}")
        broadcast_msg(msg.strip('\0'), user_id)


def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind((HOST, PORT))

    while True:
        print("Listening...")
        soc.listen()
        client_soc, client_addr = soc.accept()
        CLIENT_DICT_LOCK.acquire()
        num_clients = len(CONNECTED_CLIENTS.keys())
        CLIENT_DICT_LOCK.release()
        if num_clients == MAX_CLIENTS:
            client_soc.sendall(b'SERVER FULL\x00')
            client_soc.close()
            continue
        else:
            client_soc.sendall(b'SEND USER ID\x00')
        while True:
            user_id = receive_msg(client_soc)
            if user_id is None:
                print(f"Client: {client_addr} closed connection")
                client_soc.close()
                return
            print(f"HANDSHAKE: {bytes(user_id, 'utf-8')}")
            user_id = user_id.strip('\0')
            if user_id in CONNECTED_CLIENTS.keys():
                client_soc.sendall(b'USERID TAKEN\x00')
                client_soc.close()
                break
            elif len(user_id) > MAX_USERID_LEN:
                client_soc.sendall(b'USERID TOO LONG\x00')
                client_soc.close()
                break
            else:
                client_soc.sendall(b'CONNECTING\x00')
                CLIENT_DICT_LOCK.acquire()
                CONNECTED_CLIENTS.update({user_id: client_soc})
                CLIENT_DICT_LOCK.release()
                threading.Thread(target=process_client, args=[client_soc, client_addr, user_id]).start()
                break


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # allow HOST, PORT, and BUFF_SIZE to keep their default
        pass
    elif len(sys.argv) < 3 or len(sys.argv) > 4:
        print("USAGE: pychat_server.py <ip address> <port> [buffer size]")
        sys.exit(-1)
    else:
        HOST = sys.argv[1]
        try:
            PORT = int(sys.argv[2])
            if PORT < 1024 or PORT > 65535:
                print("Port number must be between 1024 and 65535")
                sys.exit(-2)
        except ValueError:
            print("USAGE: pychat_server.py <ip address> <port> [buffer size]")
            sys.exit(-3)

        if len(sys.argv) == 4:
            try:
                BUFF_SIZE = int(sys.argv[3])
                if BUFF_SIZE <= 0:
                    print("Buffer size must be greater than zero")
                    sys.exit(-4)
            except ValueError:
                print("USAGE: pychat_server.py <ip address> <port> [buffer size]")
                sys.exit(-5)
    main()
