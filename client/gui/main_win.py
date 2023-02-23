import tkinter as tk
from tkinter import messagebox, font as tk_font
import random
import os
import re

import socket
from gui.menu_bar import MenuBar
from backend.TCPClient import TCPClient
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
        self.default_bg = "#f2f2f2"
        self.default_fg = '#0d0d0d'

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

        self.chat_frame = tk.Frame(self, background=self.app_bg)
        self.input_frame = tk.Frame(self, background=self.app_bg)

        self.chat_box_frame = tk.Frame(self.chat_frame, width=800, height=500)
        self.chat_box_frame.pack_propagate(0)
        self.chat_box = tk.Text(self.chat_box_frame, wrap=tk.WORD, background=self.default_bg,
                                foreground=self.default_fg, font=self.font, relief=tk.FLAT,
                                insertbackground=self.default_bg, state=tk.DISABLED)

        self.chat_scroll = tk.Scrollbar(self.chat_frame, command=self.chat_box.yview)
        self.chat_box.configure(yscrollcommand=self.chat_scroll.set, relief=tk.FLAT)

        self.user_input = tk.Entry(self.input_frame, background=self.default_bg, foreground=self.default_fg,
                                   font=self.font, relief=tk.FLAT, insertbackground=self.default_fg)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_msg,
                                     background="#f2f2f2", foreground=self.default_fg,
                                     relief=tk.FLAT, activebackground="#f2f2f2", activeforeground=self.default_fg,
                                     height=2, width=10)

        self.input_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.user_input.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=self.padx, pady=(0, self.pady))
        self.send_button.pack(fill=tk.X, side=tk.RIGHT, pady=(0, self.pady), padx=(0, 5))

        self.chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.chat_box_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(self.padx, 0), pady=self.pady)
        self.chat_box.pack(fill=tk.BOTH, expand=True)
        self.chat_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, self.padx), pady=self.pady)

        self.user_input.bind("<Return>", self.send_msg)
        self.bind("<Control-C>", self.menubar.copy)
        self.bind("<Control-X>", self.menubar.cut)
        self.bind("<Control-V>", self.menubar.paste)
        self.bind("<Control-Up>", self.increase_font_size)
        self.bind("<Control-Down>", self.decrease_font_size)

        for color in self.available_colors:
            self.chat_box.tag_configure(color, foreground=color)

        if connection_info is not None:
            self.connect(connection_info[0], connection_info[1], connection_info[2])

    def read_config(self):
        if os.path.exists('.config'):
            with open('.config', 'r') as file:
                lines = file.readlines()
            try:
                self.font_family = lines[0].split(':')[1].strip('\n')
                if self.font_family not in self.fonts:
                    print(self.font_family)
                    self.font_family = 'Arial'
                else:
                    print("WHAT THE FUCK")

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

    def clear_chat_box(self):
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
        if not self.tcp_client.is_connected:
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

        if isinstance(result, UserIDTaken):
            messagebox.showwarning(message=f"Username {user_id} has been taken")
            self.chat_box.delete(0.0, tk.END)
        elif isinstance(result, UserIDTooLong):
            messagebox.showwarning(message=f"Username {user_id} is too long")
            self.chat_box.delete(0.0, tk.END)
        elif isinstance(result, ServerFull):
            messagebox.showwarning(message=f"Room {host} at port {port} is full")
            self.chat_box.delete(0.0, tk.END)
        elif isinstance(result, TimeoutError):
            messagebox.showerror(title="Error", message=f"Connection to {host} at port {port} has timed out")
            self.chat_box.delete(0.0, tk.END)
        elif isinstance(result, ConnectionAbortedError) or isinstance(result, ConnectionResetError):
            messagebox.showerror(title="Error", message=f"Could not connect to {host} at port {port}")
            self.chat_box.delete(0.0, tk.END)
        elif isinstance(result, socket.gaierror):
            messagebox.showerror(title="Error", message=f"Host address {host} is invalid")
            self.chat_box.delete(0.0, tk.END)
        elif isinstance(result, ConnectionRefusedError):
            messagebox.showerror(title="Error", message=f"Host {host} at port {port} refused to connect")
            self.chat_box.delete(0.0, tk.END)
        else:
            self.title(f"Connected to {host} at port {port} | Username: {user_id}")

    def disconnect(self):
        if self.tcp_client.is_connected:
            answer = messagebox.askyesno('Disconnect?',
                                         f'Are you sure you want to disconnect from the current chatroom?')
            if answer:
                old_host = self.tcp_client.host
                old_port = self.tcp_client.port
                self.tcp_client.close_connection()
                self.write_to_chat_box(tk.END, f"Disconnected from {old_host} at port {old_port}\n")
                self.title("Pychat")
                return True
            else:
                return False
        else:
            return None

    def send_msg(self, *args):
        if not self.tcp_client.is_connected:
            return
        text = self.user_input.get()
        self.user_input.delete(0, tk.END)
        result = self.tcp_client.send(text)
        if not result:
            messagebox.showerror(title="Error", message=f"Host closed connection")
            self.write_to_chat_box(tk.END, f"Disconnected from {self.tcp_client.host} at port {self.tcp_client.port}\n")
            self.tcp_client.close_connection()

    def process_msg(self, sender, msg):
        self.write_to_chat_box(f"{sender}", self.member_colors[sender])
        self.write_to_chat_box(f": {msg}\n")

    def process_info_msg(self, msg):
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

