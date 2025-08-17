"""
Pychat Client
Written by Joshua Kitchen - 2023
"""
import argparse
import logging

from client.gui.main_win import MainWin
import log_util

logger = logging.getLogger()
logger.handlers = []

def main():
    parser = argparse.ArgumentParser(description="Starts the pychat client")
    parser.add_argument("-ip", "--ip_addr", type=str,
                        help="The ip address (IPv4) of the chat room to connect to on startup", default="127.0.0.1")
    parser.add_argument("-p", "--port", type=int, help="The port of the chat room to connect to on startup",
                        default=5000)
    parser.add_argument("-u", "--username", type=str, help="Username to connect to the chat room with")
    parser.add_argument("-d", '--debug', action="store_true",
                        help="Add debug messages to the client log")

    args = vars(parser.parse_args())

    if args['debug']:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger.setLevel(log_level)
    log_util.toggle_file_handler(logger, ".client_log", log_level, "pychat-client-file-handler")

    if args['ip_addr'] and args['port'] and args['username']:
        win = MainWin((args['ip_addr'], args['port'], args['username']))
    else:
        win = MainWin()

    win.mainloop()


if __name__ == '__main__':
    main()
