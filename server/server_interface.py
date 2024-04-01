"""
Server Interface
Written by Joshua Kitchen - 2023
"""

import shlex
import sys
import os
from pynput import keyboard
import threading
import logging

import log_util


class ServerInterface:
    def __init__(self, server_obj, logger=None, auto_start=False):
        self._console_logging = False
        self._console_logging_lock = threading.Lock()
        self.server_obj = server_obj
        self.auto_start = auto_start
        self.messages = []
        self.logger = logger
        self.commands = {
            "quit": self.quit,
            "help": self.list_commands,
            "viewLog": self.toggle_console_logging,
            "info": self.info,
            "shutdown": self.shutdown_server,
            "restart": self.restart_server,
            "start": self.start,
            "clients": self.view_clients,
            "send": self.send_message,
            "messages": self.view_messages,
            "checkMsg": self.query_messages,
            "kick": self.kick
        }

    @staticmethod
    def list_commands(args):
        print(
            "COMMANDS:\n"
            "quit - exit the program. If a server is running, it will be shutdown\n"
            "help - list all available commands\n"
            "info - list general information about the server\n"
            "viewLog - continually prints logged messages to the console. Press 'esc' to exit log mode\n"
            "start - starts the server\n"
            "shutdown - shuts down the server\n"
            "restart - restarts the server\n"
            "clients - View all clients currently connected\n"
            "send [client_id] [message] - Send message to a Client\n"
            "messages - View all messages\n"
            "checkMsg - Query server for new messages"
            "kick [client_id] - Disconnect a Client\n"
        )

    def _set_console_log(self, value):
        self._console_logging_lock.acquire()
        self._console_logging = value
        self._console_logging_lock.release()

    def _is_logging_to_console(self):
        self._console_logging_lock.acquire()
        result = self._console_logging
        self._console_logging_lock.release()
        return result

    def _command_parser(self, string):
        if string == '':
            return
        try:
            string = shlex.split(string)
        except ValueError:
            print(f"Invalid syntax. To view commands, type \"help\"")
        command = string.pop(0)
        try:
            self.commands[command](string)
        except KeyError:
            print(f"\"{command}\" is not a recognized command. To view commands, type \"help\"")

    def _on_press(self, key):
        if key == keyboard.Key.esc:
            self._console_logging = False

    def broadcast_server_message(self, args):
        try:
            message = args[0]
        except IndexError:
            print("Cannot send message as no message was provided")
            return
        self.server_obj.broadcast_msg(f"SERVERMSG:{message}", "INFO")

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

    def quit(self, args):
        confirm = input("Are you sure you want to quit? If the server is running, it will be shutdown. y/n: ")
        if confirm == 'y':
            self.server_obj.stop()
            sys.exit()
        else:
            return

    def toggle_console_logging(self, args):
        if not self.logger:
            return
        self._console_logging = True
        log_util.add_stream_handler(self.logger, logging.DEBUG, "server-stream-handler")
        with keyboard.Listener(on_press=self._on_press) as listener:
            while self._is_logging_to_console():
                pass

    def info(self, args):
        if self.server_obj.is_running():
            print(f"---RUNNING---")
        else:
            print(f"---STOPPED---")

        print(f"\nSERVER IP ADDRESS: {self.server_obj.addr()[0]}")
        print(f"SERVER PORT {self.server_obj.addr()[1]}")
        print(f"CAPACITY: {self.server_obj.client_count()}/{self.server_obj.max_clients()}")

    def shutdown_server(self, args):
        if self.server_obj.is_running():
            confirm = input("Are you sure you want to shut down the server? y/n: ")
            if confirm == 'y':
                self.server_obj.stop()
                print("Server has been shutdown")
            else:
                return
        else:
            print("The server is not running")

    def restart_server(self, args):
        if self.server_obj.is_running():
            confirm = input("Are you sure you want to restart the server? y/n: ")
            if confirm == 'y':
                self.server_obj.stop()
                self.server_obj.start()
                print("Server has been restarted")
            else:
                return
        else:
            print("The server is not running")

    def start(self, args):
        if not self.server_obj.is_running():
            if self.server_obj.start():
                threading.Thread(target=self.server_obj.process_msg_queue).start()
                print("Server has been started")
            else:
                print(f"Could not bind to {self.server_obj.addr()[0]} at port {self.server_obj.addr()[0]}")
                sys.exit(-1)
        else:
            print("The server is already running")

    def view_clients(self, args):
        client_list = self.server_obj.list_clients()
        for client_id in client_list:
            client_info = self.server_obj.get_client_info(client_id)
            print(f"{client_id} @ {client_info['host']} on port {client_info['port']}")

    def kick(self, args):
        try:
            result = self.server_obj.disconnect_client(args[0])
        except IndexError:
            print("No user provided")
            return
        if result:
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

    def mainloop(self):
        if os.path.exists(".logo"):
            with open(".logo") as file:
                logo = file.read()
        else:
            logo = "TCP SERVER"

        print(logo)
        print(" ")
        print("To view commands, type \"help\"")
        if self.auto_start:
            self.start(None)
        while True:
            string = input("$: ")
            self._command_parser(string)
