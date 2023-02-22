import tkinter as tk
from tkinter import messagebox
import random

import socket
from gui.menu_bar import MainMenu
from backend.TCPClient import TCPClient
from backend.exceptions import UserIDTaken, ServerFull, UserIDTooLong


class MainWin(tk.Tk):
    def __init__(self, connection_info=None):
        tk.Tk.__init__(self)
        self.title("Pychat")
        self.tcp_client = TCPClient(self)

        self.room_members = []
        self.available_colors = ['#000066', '#0000ff', '#0099cc', '#006666',
                                 '#006600', '#003300', '#669900',
                                 '#e68a00', '#ff471a', '#ff8080',
                                 '#b30000', '#660000', '#e6005c',
                                 '#d966ff', '#4d004d', '#8600b3'
                                 ]
        self.member_colors = {}

        self.default_bg = "#f2f2f2"
        self.default_fg = '#0d0d0d'
        self.accent_color = "#001a4d"
        self.font_family = 'Monospace'
        self.font_size = 12
        self.font = (self.font_family, self.font_size)
        self.padx = 8
        self.pady = 8

        self.protocol('WM_DELETE_WINDOW', self.close)

        self.menubar = MainMenu(self)

        self.configure(menu=self.menubar)

        self.chat_frame = tk.Frame(self, background=self.accent_color)
        self.input_frame = tk.Frame(self, background=self.accent_color)
        self.chat_box = tk.Text(self.chat_frame, wrap=tk.WORD, background=self.default_bg, foreground=self.default_fg,
                                font=self.font, relief=tk.FLAT, insertbackground=self.default_bg)

        self.chat_scroll = tk.Scrollbar(self.chat_frame, command=self.chat_box.yview)
        self.chat_box.configure(yscrollcommand=self.chat_scroll.set, relief=tk.FLAT)

        for color in self.available_colors:
            self.chat_box.tag_configure(color, foreground=color)

        self.user_input = tk.Text(self.input_frame, height=5, background=self.default_bg, foreground=self.default_fg,
                                  font=self.font, relief=tk.FLAT, insertbackground=self.default_fg)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_msg,
                                     background="#f2f2f2", foreground=self.default_fg, font=(self.font_family, 12),
                                     relief=tk.FLAT, activebackground="#f2f2f2", activeforeground=self.default_fg)

        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        self.input_frame.pack(fill=tk.BOTH, expand=True)
        self.chat_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(self.padx, 0), pady=self.pady)
        self.chat_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, self.padx), pady=self.pady)
        self.user_input.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=self.padx, pady=(0, self.pady))
        self.send_button.pack(fill=tk.BOTH, side=tk.RIGHT, pady=(0, self.pady), padx=(0, 5))

        self.chat_box.bind("<Key>", lambda e: "break")
        self.bind("<Control-C>", self.menubar.copy)
        self.bind("<Control-X>", self.menubar.cut)
        self.bind("<Control-V>", self.menubar.paste)

        if connection_info is not None:
            self.connect(connection_info[0], connection_info[1], connection_info[2])

    def connect(self, host, port, user_id):
        self.chat_box.insert(tk.END, f"Connecting to {host} at port {port}\n")
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
        else:
            self.title(f"Connected to {host} at port {port} | Username: {user_id}")

    def close(self):
        if self.tcp_client.soc is not None:
            self.tcp_client.soc.close()
        self.quit()

    def send_msg(self):
        text = self.user_input.get(0.0, tk.END)
        self.user_input.delete(0.0, tk.END)
        self.tcp_client.send(text)

    def process_msg(self, sender, msg):
        self.chat_box.insert(tk.END, f"{sender}", self.member_colors[sender])
        self.chat_box.insert(tk.END, f": {msg}\n")
        self.update_idletasks()

    def process_info_msg(self, msg):
        data = msg.split(':')
        if data[0] == 'joined':
            self.chat_box.insert(tk.END, f"-- {data[1]} joined the server --\n")
            if data[1] not in self.room_members:
                self.room_members.append(data[1])
                color = random.choice(self.available_colors)
                self.available_colors.remove(color)
                self.member_colors.update({data[1]: color})
        elif data[0] == 'left':
            self.chat_box.insert(tk.END, f"-- {data[1]} left the server --\n")
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

