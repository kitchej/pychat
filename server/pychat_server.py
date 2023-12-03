"""
Pychat Server
Written by Joshua Kitchen - 2023
"""
import argparse
import logging

from backend.TCP_server import TCPServer
from server_interface import ServerInterface


def main():
    parser = argparse.ArgumentParser(description="Starts a server for pychat")
    parser.add_argument("-ip_addr", type=str, help="The ip address (IPv4) for the chat server", default= "127.0.0.1")
    parser.add_argument("-port", type=int, help="The port for the server", default=5000)
    parser.add_argument("-b", '--buffer_size', type=int, default=4096,
                        help="The default size of the socket buffer. Must be between 1024 and 65535")
    parser.add_argument("-mc", '--max_clients', type=int, default=16,
                        help="The maximum number of clients allowed in the server by default")
    parser.add_argument("-ul", '--max_userid_len', type=int, default=16,
                        help="The maximum length of a client's username by default")
    parser.add_argument("-d", '--debug', action="store_true",
                        help="Add debug messages to the server log")
    parser.add_argument("-a", '--auto_start', action="store_true",
                        help="Add debug messages to the server log")

    args = vars(parser.parse_args())

    if args['debug']:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(filename="server_log", filemode='w', level=log_level,
                        format="%(asctime)s - %(levelname)s: %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S %p")

    tcp_server = TCPServer(args['ip_addr'], args['port'], args['buffer_size'], args['max_clients'],
                           args['max_userid_len'])

    interface = ServerInterface(tcp_server, auto_start=args['auto_start'])
    interface.mainloop()


if __name__ == '__main__':
    main()
