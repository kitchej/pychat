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
        self.logger = logger # Even though we have the global 'logger' variable, I can't add any handlers to it unless
                             # it's referenced in an instance variable for reasons that I do not understand.
        self.commands = {
            "help": (self.list_commands, "Show all available commands"),
            "logmode": (self.toggle_console_logging, "Continually prints logged messages to the console. Press 'enter' to exit log mode"),
            "info": (self.info, "Lists general information about the server"),
            "shutdown": (self.shutdown_server, "Shuts down the server and exits"),
            "restart": (self.restart_server, "Restarts the server"),
            "clients": (self.view_clients, "View all clients currently connected"),
            "broadcast": (self.broadcast_server_message, "[message] - Broadcast a message to all clients"),
            "kick": (self.kick, "[client_id] - Disconnect a client")
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
        _ = input("Press enter to quit log mode\n")
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
                sys.exit()
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
            threading.Thread(target=self.server_obj.process_msg_queue, daemon=True).start()
            print("Server has been started")
        else:
            print("The server is already running")

    def view_clients(self, args):
        client_list = self.server_obj.list_clients()
        for client_id in client_list:
            client_info = self.server_obj.get_client_attributes(client_id)
            print(f"{client_id} @ {client_info['addr'][0]} on port {client_info['addr'][1]}")

    def kick(self, args):
        try:
            self.server_obj.disconnect_client(args[0])
        except IndexError:
            print("No user provided")
            return
        except KeyError:
            print(f"User {args[0]} is not connected")

        self.server_obj.unregister_username(args[0])
        self.server_obj.broadcast_msg(b"KICKED:", flags=4)
        print(f"User {args[0]} was kicked")

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
