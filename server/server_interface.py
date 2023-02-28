"""
Server Interface
Written by Joshua Kitchen - 2023

Provides a command line interface for the pychat server
"""

import TCP_server
import os
import sys
import logging
logging.getLogger(__name__)


class ServerInterface:
    def __init__(self, server_obj: TCP_server.TCPServer):
        self.server_obj = server_obj
        self.commands = {
            "quit": self.quit,
            "help": self.list_commands,
            "viewLog": self.view_log,
            "shutdown": self.shutdown_server,
            "restart": self.restart_server,
            "start": self.start_server,
            "viewClients": self.view_clients,
            "kick": self.kick,
            "broadcastMsg": self.broadcast_server_message,
            "blacklistIp": self.blacklist_ip,
            "unBlacklistIp": self.un_blacklist_ip,
            "viewIpBlacklist": self.view_ip_blacklist
        }

    def quit(self, args):
        confirm = input("Are you sure you want to quit? If the server is running, it will be shutdown. y/n: ")
        if confirm == 'y':
            self.server_obj.close_server()
            sys.exit()
        else:
            return

    def view_log(self, args):
        if os.path.exists("server_log"):
            with open("server_log", 'r') as file:
                print(file.read())
        else:
            print("No server log file")

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

    def start_server(self, args):
        if not self.server_obj.is_running():
            self.server_obj.start_server()
            print("Server has been started")
        else:
            print("The server is already running")

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

    def view_clients(self, args):
        clients = self.server_obj.get_connected_clients()
        for client_key in clients.keys():
            client = clients[client_key]
            print(f"{client.user_id} @ {client.addr} on port {client.port}")

    def kick(self, args):
        try:
            result = self.server_obj.disconnect_client(args[1])
        except IndexError:
            print("No user provided")
            return
        if result:
            print(f"User {args[1]} was kicked")
        else:
            print(f"User {args[1]} is not connected")

    def broadcast_server_message(self, args):
        try:
            message = args[1]
        except IndexError:
            print("Cannot send message as no message was provided")
            return
        self.server_obj.broadcast_msg(message, "SERVER")

    def blacklist_ip(self, args):
        try:
            ip = args[1]
        except IndexError:
            print("No IP address provided")
            return
        if ip == "" or ip == " ":
            print("No IP address provided")
            return
        self.server_obj.black_list_ip(args[1])

    def un_blacklist_ip(self, args):
        try:
            ip = args[1]
        except IndexError:
            print("No IP address provided")
            return
        if ip == "" or ip == " ":
            print("No IP address provided")
            return
        result = self.server_obj.black_list_ip(args[1])
        if not result:
            print(f"IP address {args[1]} was not blacklisted")

    def view_ip_blacklist(self, args):
        blacklist = self.server_obj.get_ip_blacklist()
        if len(blacklist) == 0:
            print("None")
        else:
            for ip in blacklist:
                print(ip)

    @staticmethod
    def list_commands(args):
        print(
            "COMMANDS:\n"
            "quit - exit the program. If a server is running, it will be shutdown\n"
            "help - list all available commands\n"
            "viewLog - print logged messages to the console\n"
            "start - starts the server\n"
            "shutdown - shuts down the server\n"
            "restart - restarts the server\n"
            "viewClients - View all clients currently connected\n"
            "broadcastMsg - Broadcast a message as the server\n"
            "kick <user_id> - Kick a client\n"
            "blacklistIp <ip_address> - Blacklists an ip\n"
            "unBlacklistIp <ip_address> - Un-blacklists an ip\n"
        )

    def __command_parser(self, string):
        if string == '':
            return
        string = string.split(' ')
        command = string.pop(0)
        string.insert(0, self)
        try:
            self.commands[command](string)
        except KeyError:
            print(f"\"{command}\" - Command not recognized ")

    def mainloop(self):
        if os.path.exists(".logo"):
            with open(".logo") as file:
                logo = file.read()
        else:
            logo = "PYCHAT SERVER"

        print(logo)
        print(" ")
        print("To view commands, type \"help\"")
        self.start_server(None)
        while True:
            string = input("$: ")
            self.__command_parser(string)
