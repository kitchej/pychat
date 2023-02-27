"""
TODO:
    - Send a blank INFO message at regular intervals to see if a client is still connected
    - Commands:
        - View all clients
        - Monitor chat
            - GUI window to monitor chat?
        - Kick a client
        - Mute a client
        - Send a server message
        - System for scheduling server messages?
"""
import argparse

from TCP_server import TCPServer
from server_manager import ServerInterface


def main():
    parser = argparse.ArgumentParser(description="Starts a server for pychat")
    parser.add_argument("host", type=str, help="The ip address (IPv4) to host the chat server on")
    parser.add_argument("port", type=int, help="The port for the server")
    parser.add_argument("-b", '--buffer_size', type=int, default=4096,
                        help="The default size of the socket buffer. Must be between 1024 and 65535")
    parser.add_argument("-mc", '--max_clients', type=int, default=16,
                        help="The maximum number of clients allowed in the server by default")
    parser.add_argument("-ul", '--max_userid_len', type=int, default=16,
                        help="The maximum length of a client's username by default")
    parser.add_argument("-d", '--debug', action="store_true",
                        help="Add debug messages to the server log")

    args = vars(parser.parse_args())
    tcp_server = TCPServer(args['host'], args['port'], args['buffer_size'], args['max_clients'],
                           args['max_userid_len'], args['debug'])

    interface = ServerInterface(tcp_server)
    interface.mainloop()


if __name__ == '__main__':
    main()
