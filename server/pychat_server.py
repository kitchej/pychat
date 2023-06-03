"""
Pychat Server
Written by Joshua Kitchen - 2023

Serves as the entry point for the Pychat server
"""
import argparse
import logging

from server.backend.TCP_server import TCPServer
from server_interface import ServerInterface


def main():
    parser = argparse.ArgumentParser(description="Starts a server for pychat")
    parser.add_argument("_host", type=str, help="The ip address (IPv4) to _host the chat server on")
    parser.add_argument("_port", type=int, help="The _port for the server")
    parser.add_argument("-b", '--buffer_size', type=int, default=4096,
                        help="The default size of the socket buffer. Must be between 1024 and 65535")
    parser.add_argument("-mc", '--__max_clients', type=int, default=16,
                        help="The maximum number of clients allowed in the server by default")
    parser.add_argument("-ul", '--__max_userid_len', type=int, default=16,
                        help="The maximum length of a client's username by default")
    parser.add_argument("-d", '--debug', action="store_true",
                        help="Add debug messages to the server log")

    args = vars(parser.parse_args())

    if args['debug']:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(filename="server_log", filemode='w', level=log_level,
                        format="%(asctime)s - %(levelname)s: %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S %p")

    tcp_server = TCPServer(args['_host'], args['_port'], args['buffer_size'], args['__max_clients'],
                           args['__max_userid_len'])

    interface = ServerInterface(tcp_server)
    interface.mainloop()


if __name__ == '__main__':
    main()
