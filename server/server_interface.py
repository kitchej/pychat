"""
Server Interface
Written by Joshua Kitchen - 2023
"""

import shlex
import sys
import os
import threading
import logging

import log_util

logger = logging.getLogger(__name__)


class ServerInterface:
    def __init__(self, server_obj, addr, logger=None):
        self.server_obj = server_obj
        self.addr = addr
        self.messages = []
        self.logger = logger
        self.commands = {
            "help": (self.list_commands, "Show all available commands"),
            "logmode": (self.toggle_console_logging, "continually prints logged messages to the console. Press 'esc' to exit log mode"),
            "info": (self.info, "list general information about the server"),
            "shutdown": (self.shutdown_server, "shuts down the server and exits"),
            "restart": (self.restart_server, "restarts the server"),
            "clients": (self.view_clients, "View all clients currently connected"),
            "send": (self.send_message, "[client_id] [message] - Send message to a Client"),
            "broadcast_msg": (self.broadcast_server_message, "[message] - Broadcast a message to all clients"),
            "messages": (self.view_messages, "View all messages"),
            "check_msg": (self.query_messages, "Query server for new messages"),
            "kick": (self.kick, "[client_id] - Disconnect a Client")
        }

    def list_commands(self, args):
        for key in self.commands.keys():
            print(f"{key}: {self.commands[key][1]}")

    def _command_parser(self, string):
        if string == '':
            return
        try:
            string = shlex.split(string)
        except ValueError:
            print(f"Invalid syntax. To view commands, type \"help\"")
        command = string.pop(0)
        try:
            self.commands[command][0](string)
        except KeyError:
            print(f"\"{command}\" is not a recognized command. To view commands, type \"help\"")

    def broadcast_server_message(self, args):
        try:
            message = args[0]
        except IndexError:
            print("Cannot send message as no message was provided")
            return
        self.server_obj.broadcast_msg(bytes(f"SERVERMSG:{message}", 'utf-8'), flags=4, is_server_msg=True)

    def blacklist_ip(self, args):
        try:
            ip = args[0]
        except IndexError:
            print("No IP address provided")
            return
        if ip == "" or ip == " ":
            print("No IP address provided")
            return
        self.server_obj.blacklist_ip(args[0])

    def un_blacklist_ip(self, args):
        try:
            ip = args[0]
        except IndexError:
            print("No IP address provided")
            return
        if ip == "" or ip == " ":
            print("No IP address provided")
            return
        result = self.server_obj.un_blacklist_ip(args[0])
        if not result:
            print(f"IP address {args[0]} was not blacklisted")

    def view_ip_blacklist(self, args):
        blacklist = self.server_obj.get_ip_blacklist()
        if len(blacklist) == 0:
            print("None")
        else:
            for ip in blacklist:
                print(ip)

    def toggle_console_logging(self, args):
        if not self.logger:
            return
        log_util.toggle_stream_handler(self.logger, logging.DEBUG, "server-stream-handler")
        _ = input("Press enter to quit log mode")
        log_util.toggle_stream_handler(self.logger, logging.DEBUG, "server-stream-handler")

    def info(self, args):
        if self.server_obj.is_running:
            print(f"---RUNNING---")
        else:
            print(f"---STOPPED---")

        print(f"\nSERVER IP ADDRESS: {self.server_obj.addr[0]}")
        print(f"SERVER PORT {self.server_obj.addr[1]}")
        print(f"CAPACITY: {self.server_obj.client_count}/{self.server_obj.max_clients}")

    def shutdown_server(self, args):
        if self.server_obj.is_running:
            confirm = input("Are you sure you want to shut down the server? y/n: ")
            if confirm == 'y':
                self.server_obj.stop()
                print("Server has been shutdown")
                sys.exit(0)
            else:
                return

    def restart_server(self, args):
        if self.server_obj.is_running:
            confirm = input("Are you sure you want to restart the server? y/n: ")
            if confirm == 'y':
                self.server_obj.stop()
                self.server_obj.start(self.addr)
                print("Server has been restarted")
            else:
                return
        else:
            print("The server is not running")

    def start(self, args):
        if not self.server_obj.is_running:
            self.server_obj.start(self.addr)
            threading.Thread(target=self.server_obj.process_msg_queue).start()
            print("Server has been started")
        else:
            print("The server is already running")

    def view_clients(self, args):
        client_list = self.server_obj.list_clients()
        for client_id in client_list:
            client_info = self.server_obj.get_client_info(client_id)
            print(f"{client_id} @ {client_info['addr'][0]} on port {client_info['addr'][1]}")

    def kick(self, args):
        try:
            result = self.server_obj.disconnect_client(args[0])
        except IndexError:
            print("No user provided")
            return
        if result:
            self.server_obj.unregister_username(args[0])
            self.server_obj.broadcast_msg(b"KICKED:", flags=4)
            print(f"User {args[0]} was kicked")
        else:
            print(f"User {args[0]} is not connected")

    def send_message(self, args):
        if len(args) == 0:
            print("No args given")
            return
        if args[1] == "video":
            print("Sending video")
            with open("dummy_files/video1.mkv", 'rb') as file:
                msg = file.read()
        else:
            msg = bytes(args[1], 'utf-8')
        result = self.server_obj.send(args[0], msg)
        if result:
            print(f"Sent message to {args[0]}")
        else:
            print(f"No Client with id {args[0]}")

    def query_messages(self, args):
        i = 0
        for msg in self.server_obj.get_all_msg():
            self.messages.insert(0, msg)
            i += 1
        print(f"{i} new messages received")

    def view_messages(self, args):
        if len(self.messages) == 0:
            print("No messages")
            return
        for msg in self.messages:
            print(f"FROM: {msg.client_id}\n"
                  f"SIZE: {msg.size}\n"
                  f"TEXT: \n"
                  f"{msg.data}\n\n")

    def mainloop(self, log_mode=False):
        self.start(None)
        if os.path.exists(".logo"):
            with open(".logo") as file:
                logo = file.read()
        else:
            logo = "TCP SERVER"
        print(logo)
        print(" ")
        print("To view commands, type \"help\"")
        if log_mode:
            self.toggle_console_logging([])
        while True:
            string = input("$: ")
            self._command_parser(string)
