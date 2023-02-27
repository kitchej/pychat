"""
TODO:
    - shutdown_server properly (TCP_server.__mainloop thread still runs until an error is encountered)
"""

import TCP_server
import os
import sys


class ServerInterface:
    """Interface for the pychat server"""

    def __init__(self, server_obj: TCP_server.TCPServer):
        self.server_obj = server_obj
        self.commands = {
            "quit": self.quit,
            "help": self.list_commands,
            "shutdown": self.shutdown_server,
            "restart": self.restart_server,
            "start": self.start_server,
            "viewAllClients": self.view_clients,
            "sendServerMsg": self.send_server_message,
            "monitorChat": self.monitor_chat,
            "kick": self.kick,
            "mute": self.mute,
            "send": self.send_server_message,
            "blacklistIp": self.blacklist_ip,
            "unBlacklistIp": self.un_blacklist_ip
        }

    def quit(self, args):
        confirm = input("Are you sure you want to quit? If the server is running, it will be shutdown. y/n: ")
        if confirm == 'y':
            self.server_obj.close_server()
            sys.exit()
        else:
            return

    def shutdown_server(self, args):
        if self.server_obj.is_running:
            confirm = input("Are you sure you want to shut down the server? y/n: ")
            if confirm == 'y':
                self.server_obj.close_server()
                print("Server has been shutdown")
            else:
                return
        else:
            print("The server is not running")

    def start_server(self, args):
        if not self.server_obj.is_running:
            self.server_obj.start_server()
            print("Server has been started")
        else:
            print("The server is already running")

    def restart_server(self, args):
        if self.server_obj.is_running:
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
        pass

    def monitor_chat(self, args):
        pass

    def kick(self, args):
        pass

    def mute(self, args):
        pass

    def send_server_message(self, args):
        pass

    def blacklist_ip(self, args):
        pass

    def un_blacklist_ip(self, args):
        pass

    @staticmethod
    def list_commands(*args):
        print(
            "COMMANDS:\n"
            "quit - exit the program. If a server is running, it will be shutdown\n"
            "start - starts the server\n"
            "shutdown - shuts down the server\n"
            "restart - restarts the server\n"
            "viewAllClients - View all clients currently connected\n"
            "sendServerMsg - Send a message as the server"
            "monitorChat - Pull up a GUI window showing the chat\n"
            "kick <user_id> - Kick a client\n"
            "mute <user_id> <time> - Mute a client for a specified time\n"
            "blacklistIp <ip_address> - Blacklists an ip\n"
            "unBlacklistIp <ip_address> - Un-blacklists an ip\n"
        )

    def __command_parser(self, string):
        if string == '':
            return
        string = string.split(' ')
        command = string[0]
        if len(string) > 1:
            args = string[1:-1]
        else:
            args = []
        args.insert(0, self)
        try:
            self.commands[command](args)
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
        while True:
            string = input("$: ")
            self.__command_parser(string)
