"""
Server Interface
Written by Joshua Kitchen - 2023
"""

from backend import TCP_server
import logging
import os
import sys
import shlex

logging.getLogger(__name__)


class ServerInterface:
    def __init__(self, server_obj: TCP_server.TCPServer, auto_start=True):
        self.server_obj = server_obj
        self.auto_start = auto_start
        self.commands = {
            "quit": self.quit,
            "help": self.list_commands,
            "viewLog": self.view_log,
            "info": self.info,
            "shutdown": self.shutdown_server,
            "restart": self.restart_server,
            "start": self.start_server,
            "viewClients": self.view_clients,
            "kick": self.kick,
            "broadcastMsg": self.broadcast_server_message,
            "blacklistIp": self.blacklist_ip,
            "unBlacklistIp": self.un_blacklist_ip,
            "viewBlacklist": self.view_ip_blacklist
        }

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

    def quit(self, args):
        confirm = input("Are you sure you want to quit? If the server is running, it will be shutdown. y/n: ")
        if confirm == 'y':
            self.server_obj.close_server()
            self.server_obj.save_ip_blacklist()
            sys.exit()
        else:
            return

    @staticmethod
    def list_commands(args):
        print(
            "COMMANDS:\n"
            "quit - exit the program. If a server is running, it will be shutdown\n"
            "help - list all available commands\n"
            "info - list general information about the server\n"
            "viewLog - print logged messages to the console\n"
            "start - starts the server\n"
            "shutdown - shuts down the server\n"
            "restart - restarts the server\n"
            "viewClients - View all clients currently connected\n"
            "broadcastMsg <\"message\"> - Broadcast a message as the server\n"
            "kick <user_id> - Kick a client\n"
            "blacklistIp <ip_address> - Blacklists an ip\n"
            "unBlacklistIp <ip_address> - Un-blacklists an ip\n"
            "viewBlacklist - View all IP address that have been blacklisted"
        )

    @staticmethod
    def view_log(args):
        if os.path.exists("server_log"):
            with open("server_log", 'r') as file:
                print(file.read())
        else:
            print("No server log file")

    def info(self, args):
        if self.server_obj.is_running():
            print(f"---RUNNING---")
        else:
            print(f"---STOPPED---")

        print(f"\nSERVER IP ADDRESS: {self.server_obj.ip_addr()}")
        print(f"SERVER PORT {self.server_obj.port()}")
        print(f"CAPACITY: {len(self.server_obj.get_connected_clients())}/{self.server_obj.max_clients()}")

    def shutdown_server(self, args):
        if self.server_obj.is_running():
            confirm = input("Are you sure you want to shut down the server? y/n: ")
            if confirm == 'y':
                self.server_obj.close_server()
                print("Server has been shutdown")
            else:
                return
        else:
            print("The server is not running")

    def restart_server(self, args):
        if self.server_obj.is_running():
            confirm = input("Are you sure you want to restart the server? y/n: ")
            if confirm == 'y':
                self.server_obj.close_server()
                self.server_obj.start_server()
                print("Server has been restarted")
            else:
                return
        else:
            print("The server is not running")

    def start_server(self, args):
        if not self.server_obj.is_running():
            if self.server_obj.start_server():
                print("Server has been started")
            else:
                print(f"Could not bind to {self.server_obj.ip_addr()} at port {self.server_obj.port()}")
                sys.exit(-1)
        else:
            print("The server is already running")

    def view_clients(self, args):
        clients = self.server_obj.get_connected_clients()
        for client_key in clients.keys():
            client = clients[client_key]
            print(f"{client.user_id} @ {client.addr} on port {client.port}")

    def kick(self, args):
        try:
            result = self.server_obj.disconnect_client(args[0], True)
        except IndexError:
            print("No user provided")
            return
        if result:
            print(f"User {args[0]} was kicked")
        else:
            print(f"User {args[0]} is not connected")

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

    def mainloop(self):
        if os.path.exists(".logo"):
            with open(".logo") as file:
                logo = file.read()
        else:
            logo = "PYCHAT SERVER"

        print(logo)
        print(" ")
        print("To view commands, type \"help\"")
        if self.auto_start:
            self.start_server(None)
        while True:
            string = input("$: ")
            self._command_parser(string)
