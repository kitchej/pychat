"""
Pychat Server
Written by Joshua Kitchen - 2023
"""
import argparse
import logging

from server.backend.TCP_server import PychatServer
from server.server_interface import ServerInterface
import log_util

logger = logging.getLogger()


def main():
    parser = argparse.ArgumentParser(description="Starts a server for pychat")
    parser.add_argument("-ip_addr", type=str, help="The ip address (IPv4) for the chat server",
                        default="127.0.0.1")
    parser.add_argument("-port", type=int, help="The port for the server", default=5000)
    parser.add_argument("-b", '--buffer_size', type=int, default=4096,
                        help="The default size of the socket buffer. Must be between 1024 and 65535")
    parser.add_argument("-mc", '--max_clients', type=int, default=16,
                        help="The maximum number of clients allowed in the server by default. Setting to zero will "
                             "allow infinite client connections")
    parser.add_argument("-ul", '--max_userid_len', type=int, default=16,
                        help="The maximum length of a client's username by default")
    parser.add_argument("-d", '--debug', action="store_true",
                        help="Add debug messages to the server log")
    parser.add_argument("-a", '--auto_start', action="store_true",
                        help="Automatically start the server on application startup")
    parser.add_argument("-l", '--log_mode', action="store_true",
                        help="Start the server in logging mode")

    args = vars(parser.parse_args())

    if args['debug']:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger.setLevel(log_level)
    log_util.toggle_file_handler(logger, ".server_log", log_level, "server-file-handler")

    tcp_server = PychatServer(args['ip_addr'], args['port'], args['buffer_size'], args['max_clients'],
                              args['max_userid_len'])

    interface = ServerInterface(tcp_server, logger, auto_start=args['auto_start'])
    interface.mainloop(log_mode=args['log_mode'])


if __name__ == '__main__':
    main()
