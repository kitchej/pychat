import tkinter as tk
from tkinter import messagebox
import random
import os
import re
import threading

import socket
from gui.menu_bar import MenuBar
from backend.TCP_Client import TCPClient
from backend.exceptions import UserIDTaken, ServerFull, UserIDTooLong


class MainWin(tk.Tk):
    def __init__(self, connection_info=None):
        tk.Tk.__init__(self)
        self.tcp_client = TCPClient(self)
        self.room_members = []
        self.available_colors = ['#000066', '#0000ff', '#0099cc', '#006666',
                                 '#006600', '#003300', '#669900',
                                 '#e68a00', '#ff471a', '#ff8080',
                                 '#b30000', '#660000', '#e6005c',
                                 '#d966ff', '#4d004d', '#8600b3'
                                 ]

        self.fonts = ['Arial', 'Calibri', 'Cambria', 'Comic Sans MS', 'Lucida Console', 'Segoe UI', 'Wingdings']
        self.member_colors = {}
        self.widget_bg = '#ffffff'
        self.widget_fg = '#000000'

        self.app_bg = "#001a4d"
        self.font_family = 'Arial'
        self.font_size = 12
        self.read_config()

        self.font = (self.font_family, self.font_size)
        self.padx = 8
        self.pady = 8

        self.title("Pychat")
        self.protocol('WM_DELETE_WINDOW', self.close_window)

        self.menubar = MenuBar(self)
        self.configure(menu=self.menubar)

        self.chat_area_frame = tk.Frame(self, background=self.app_bg)
        self.input_frame = tk.Frame(self, background=self.app_bg)

        self.chat_box_frame = tk.Frame(self.chat_area_frame, width=800, height=500)
        self.chat_box_frame.pack_propagate(False)
        self.chat_box = tk.Text(self.chat_box_frame, wrap=tk.WORD, background=self.widget_bg,
                                foreground=self.widget_fg, font=self.font,
                                insertbackground=self.widget_bg, state=tk.DISABLED)

        self.chat_scroll = tk.Scrollbar(self.chat_area_frame, command=self.chat_box.yview, background=self.widget_bg)
        self.chat_box.configure(yscrollcommand=self.chat_scroll.set, relief=tk.FLAT)

        self.user_input = tk.Entry(self.input_frame, background=self.widget_bg, foreground=self.widget_fg,
                                   font=self.font, insertbackground=self.widget_fg)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_msg,
                                     background=self.widget_bg, foreground=self.widget_fg,
                                     relief=tk.FLAT, height=2, width=10)

        self.input_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.send_button.pack(fill=tk.X, side=tk.RIGHT, pady=(0, self.pady), padx=(0, 5))
        self.user_input.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=self.padx, pady=(0, self.pady))

        self.chat_area_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.chat_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, self.padx), pady=self.pady)
        self.chat_box_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(self.padx, 0), pady=self.pady)
        self.chat_box.pack(fill=tk.BOTH, expand=True)

        self.user_input.bind("<Return>", self.send_msg)
        self.bind("<Control-Delete>", self.clear_chat_box)
        self.bind("<Control_L>s", self.menubar.archive_chat)
        self.bind("<Control_L>c", self.menubar.copy)
        self.bind("<Control_L>x", self.menubar.cut)
        self.bind("<Control_L>v", self.menubar.paste)
        self.bind("<Control-Up>", self.increase_font_size)
        self.bind("<Control-Down>", self.decrease_font_size)
        self.bind("<Control_L>n", self.menubar.connect_to_room)
        self.bind("<Control-End>", self.menubar.disconnect_from_room)
        self.send_button.bind("<Enter>", self.on_enter)
        self.send_button.bind("<Leave>", self.on_leave)

        for color in self.available_colors:
            self.chat_box.tag_configure(color, foreground=color)

        if connection_info is not None:
            threading.Thread(target=self.connect,
                             args=[connection_info[0], connection_info[1], connection_info[2]]).start()

    def on_enter(self, *args):
        self.send_button['background'] = "#bfbfbf"

    def on_leave(self, *args):
        self.send_button['background'] = self.widget_bg

    def read_config(self):
        if os.path.exists('.config'):
            with open('.config', 'r') as file:
                lines = file.readlines()
            try:
                self.font_family = lines[0].split(':')[1].strip('\n')
                if self.font_family not in self.fonts:
                    print(self.font_family)
                    self.font_family = 'Arial'
                try:
                    self.font_size = int(lines[1].split(':')[1].strip('\n'))
                except ValueError:
                    self.font_size = 12

                if self.font_size < 10 or self.font_size > 20:
                    self.font_size = 12

                self.app_bg = lines[2].split(':')[1].strip('\n')
                pattern = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
                if not re.match(pattern, self.app_bg):
                    self.app_bg = "#001a4d"
            except IndexError:
                self.app_bg = "#001a4d"
                self.font_family = 'Arial'
                self.font_size = 12
                self.write_config()
        else:
            self.write_config()

    def write_config(self):
        with open('.config', 'w') as file:
            file.write(f"font:{self.font_family}\nfontsize:{self.font_size}\nbg:{self.app_bg}")

    def write_to_chat_box(self, text, tag=None):
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.insert(tk.END, text, tag)
        self.chat_box.configure(state=tk.DISABLED)

    def clear_chat_box(self, *args):
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.delete(0.0, tk.END)
        self.chat_box.configure(state=tk.DISABLED)

    def increase_font_size(self, *args):
        if self.font_size == 20:
            print(self.font_size)
            return
        self.font_size += 1
        self.chat_box.configure(font=(self.font_family, self.font_size))
        self.user_input.configure(font=(self.font_family, self.font_size))
        self.update_idletasks()

    def decrease_font_size(self, *args):
        if self.font_size == 10:
            print(self.font_size)
            return
        self.font_size -= 1
        self.chat_box.configure(font=(self.font_family, self.font_size))
        self.user_input.configure(font=(self.font_family, self.font_size))
        self.update_idletasks()

    def change_font(self, new_font):
        self.font_family = new_font
        self.chat_box.configure(font=(self.font_family, self.font_size))
        self.user_input.configure(font=(self.font_family, self.font_size))
        self.update_idletasks()

    def close_window(self):
        if not self.tcp_client.is_connected():
            self.write_config()
            self.quit()
        else:
            answer = messagebox.askyesno('Disconnect?',
                                         f'Are you sure you want to disconnect from the current chatroom?')
            if answer:
                self.tcp_client.close_connection()
                self.write_config()
                self.quit()

    def connect(self, host, port, user_id):
        self.write_to_chat_box(f"Connecting to {host} at port {port}\n")
        result = self.tcp_client.init_connection(host, port, user_id)
        if isinstance(result, Exception):
            if isinstance(result, UserIDTaken):
                error_msg = f"Username {user_id} has been taken"
            elif isinstance(result, UserIDTooLong):
                error_msg = f"Username {user_id} is too long"
            elif isinstance(result, ServerFull):
                error_msg = f"Room {host} at port {port} is full"
            elif isinstance(result, TimeoutError):
                error_msg = f"Connection to {host} at port {port} has timed out"
            elif isinstance(result, ConnectionAbortedError) or isinstance(result, ConnectionResetError):
                error_msg = f"Could not connect to {host} at port {port}"
            elif isinstance(result, socket.gaierror):
                error_msg = f"Host address {host} is invalid"
            elif isinstance(result, ConnectionRefusedError):
                error_msg = f"Host {host} at port {port} refused to connect"
            else:
                error_msg = f"Could not connect to {host} at port {port}"
            messagebox.showwarning(title="Error", message=error_msg)
            self.clear_chat_box()
            self.tcp_client.close_connection(force=True)
        else:
            self.title(f"Connected to {host} at port {port} | Username: {user_id}")
            self.user_input.configure(state=tk.NORMAL)

    def disconnect(self):
        if self.tcp_client.is_connected():
            answer = messagebox.askyesno('Disconnect?',
                                         f'Are you sure you want to disconnect from the current chatroom?')
            if answer:
                old_host, old_port = self.tcp_client.get_host_addr()
                self.tcp_client.close_connection()
                self.write_to_chat_box(f"Disconnected from {old_host} at port {old_port}\n")
                self.title("Pychat")
                self.user_input.configure(state=tk.DISABLED)
                return True
            else:
                return False
        else:
            return None

    def send_msg(self, *args):
        if not self.tcp_client.is_connected():
            return
        text = self.user_input.get()
        self.user_input.delete(0, tk.END)
        result = self.tcp_client.send(text)
        if not result:
            messagebox.showerror(title="Error", message=f"Host closed connection")
            host = self.tcp_client.get_host_addr
            self.write_to_chat_box(f"Disconnected from {host[0]} at port {host[1]}\n")
            self.tcp_client.close_connection()

    def process_msg(self, sender, msg):
        self.write_to_chat_box(f"{sender}", self.member_colors[sender])
        self.write_to_chat_box(f": {msg}\n")

    def process_info_msg(self, msg):
        if msg == "":
            return
        data = msg.split(':')
        if data[0] == 'joined':
            self.write_to_chat_box(f"-- {data[1]} joined the server --\n")
            if data[1] not in self.room_members:
                self.room_members.append(data[1])
                color = random.choice(self.available_colors)
                self.available_colors.remove(color)
                self.member_colors.update({data[1]: color})
        elif data[0] == 'left':
            self.write_to_chat_box(f"-- {data[1]} left the server --\n")
            if data[1] in self.room_members:
                self.room_members.remove(data[1])
                color = self.member_colors[data[1]]
                del self.member_colors[data[1]]
                self.available_colors.append(color)
        elif data[0] == 'members':
            for user_id in data[1].split(','):
                if user_id not in self.room_members:
                    self.room_members.append(user_id)
                    color = random.choice(self.available_colors)
                    self.available_colors.remove(color)
                    self.member_colors.update({user_id: color})
        elif data[0] == "KICKED":
            self.write_to_chat_box(f"-- You were kicked from the chat room --\n")
            self.tcp_client.close_connection(force=True)

