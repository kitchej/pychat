"""
Main Window
Written by Joshua Kitchen - 2023

All messages are sent in this format:
    "[header]\n[message]\0"

The HANDSHAKE header is used to identify handshake messages

The INFO header is used when the server and the client need to pass along information. Messages with this header include
an additional header within the message indicating what kind of information was sent. The header and the message are
delimited by a colon. Possible INFO messages are:
- JOINED:<user id>
- LEFT:<user id>
- MEMBERS:<list of connected users>
- LEAVING:<no message body>
- KICKED:<no message body>
- SERVERMSG:<message>

If the header is neither of the above options, then the message is treated as a chat message and broadcast to all
connected clients
"""


import tkinter as tk
from tkinter import messagebox
import random
import os
import re
import threading
import playsound

import socket
from gui.menu_bar import MenuBar
from backend.TCP_Client import TCPClient
from backend.exceptions import UserIDTaken, ServerFull, UserIDTooLong


class MainWin(tk.Tk):
    def __init__(self, connection_info=None):
        tk.Tk.__init__(self)
        self.tcp_client = TCPClient(self)
        self.room_members = []
        self.available_colors = [
            '#000066', '#0000ff', '#0099cc', '#006666',
            '#006600', '#003300', '#669900', '#e68a00',
            '#ff471a', '#ff8080', '#b30000', '#660000',
            '#e6005c', '#d966ff', '#4d004d', '#8600b3'
        ]
        self.fonts = ['Arial', 'Calibri', 'Cambria', 'Comic Sans MS', 'Lucida Console', 'Segoe UI', 'Wingdings']
        self.notification_sounds = [
            (None, 'None'),
            ('sounds/the-notification-email-143029.wav', 'Classic'),
            ('sounds/notification-140376.wav', 'Outer Space'),
            ('sounds/notification-126507.wav', 'Alert'),
            ('sounds/message-13716.wav', 'Deep Sea')
        ]
        self.member_colors = {}
        self.widget_bg = '#ffffff'
        self.widget_fg = '#000000'
        self.app_bg = "#001a4d"
        self.font_family = 'Arial'
        self.font_size = 12
        self.notification_sound = None
        # self.set_notification_sound(self.notification_sounds[0][0])
        self._read_config()

        self.font = (self.font_family, self.font_size)
        self.padx = 8
        self.pady = 8

        self.title("Pychat")
        self.protocol('WM_DELETE_WINDOW', self.close_window)
        self.menubar = MenuBar(self, self.font_family, self.notification_sound)
        self.configure(menu=self.menubar)
        self.chat_area_frame = tk.Frame(self, background=self.app_bg)
        self.input_frame = tk.Frame(self, background=self.app_bg)
        self.chat_box_frame = tk.Frame(self.chat_area_frame, width=800, height=500)

        self.chat_box = tk.Text(self.chat_box_frame, wrap=tk.WORD, background=self.widget_bg,
                                foreground=self.widget_fg, font=self.font, insertbackground=self.widget_bg,
                                state=tk.DISABLED)

        self.chat_scroll = tk.Scrollbar(self.chat_area_frame, command=self.chat_box.yview, background=self.widget_bg)

        self.chat_box.configure(yscrollcommand=self.chat_scroll.set, relief=tk.FLAT)

        self.user_input = tk.Entry(self.input_frame, background=self.widget_bg, foreground=self.widget_fg,
                                   font=self.font, insertbackground=self.widget_fg)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_msg, background=self.widget_bg,
                                     foreground=self.widget_fg, relief=tk.FLAT, height=2, width=10)

        # The order in which these widgets are packed matters!
        # This order ensures proper widget resizing when the window is resized.
        self.chat_box_frame.pack_propagate(False)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.send_button.pack(fill=tk.X, side=tk.RIGHT, pady=(0, self.pady), padx=(0, 5))
        self.user_input.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=self.padx, pady=(0, self.pady))
        self.chat_area_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.chat_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, self.padx), pady=self.pady)
        self.chat_box_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(self.padx, 0), pady=self.pady)
        self.chat_box.pack(fill=tk.BOTH, expand=True)

        self.user_input.bind("<Return>", self.send_msg)
        self.bind("<Control-Delete>", self._clear_chat_box)
        self.bind("<Control_L>s", self.menubar.archive_chat)
        self.bind("<Control_L>c", self.menubar.copy)
        self.bind("<Control-Up>", self.increase_font_size)
        self.bind("<Control-Down>", self.decrease_font_size)
        self.bind("<Control_L>n", self.menubar.connect_to_room)
        self.bind("<Control-End>", self.menubar.disconnect_from_room)
        self.send_button.bind("<Enter>", self._on_btn_enter)
        self.send_button.bind("<Leave>", self._on_btn_leave)

        self.chat_box.tag_configure("Center", justify='center')
        for color in self.available_colors:
            self.chat_box.tag_configure(color, foreground=color)

        if connection_info is not None:
            threading.Thread(target=self.connect, daemon=True,
                             args=[connection_info[0], connection_info[1], connection_info[2]]).start()

    def _on_btn_enter(self, *args):
        self.send_button['background'] = "#bfbfbf"

    def _on_btn_leave(self, *args):
        self.send_button['background'] = self.widget_bg

    def _read_config(self):
        if os.path.exists('.config'):
            with open('.config', 'r') as file:
                lines = file.readlines()
            try:
                self.font_family = lines[0].split('=')[1].strip('\n')
                if self.font_family not in self.fonts:
                    self.font_family = 'Arial'
                try:
                    self.font_size = int(lines[1].split('=')[1].strip('\n'))
                except ValueError:
                    self.font_size = 12

                if self.font_size < 10 or self.font_size > 20:
                    self.font_size = 12

                self.app_bg = lines[2].split('=')[1].strip('\n')
                pattern = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
                if not re.match(pattern, self.app_bg):
                    self.app_bg = "#001a4d"

                print(self.set_notification_sound(lines[3].split('=')[1].strip('\n')))

            except IndexError:
                self.app_bg = "#001a4d"
                self.font_family = 'Arial'
                self.font_size = 12
                self.set_notification_sound(None)
                self._write_config()
        else:
            self._write_config()

    def _write_config(self):
        with open('.config', 'w') as file:
            file.write(f"font={self.font_family}\n"
                       f"fontsize={self.font_size}\n"
                       f"bg={self.app_bg}\n"
                       f"notify={self.notification_sound}")

    def _play_notification_sound(self):
        if self.notification_sound is None:
            return
        threading.Thread(target=lambda: playsound.playsound(self.notification_sound), daemon=True).start()

    def _reset_gui(self):
        self.title("Pychat")
        self.user_input.configure(state=tk.DISABLED)

    def _write_to_chat_box(self, text, tag=None, newline=True):
        self.chat_box.configure(state=tk.NORMAL)
        if newline:
            text = f"{text}\n"
        self.chat_box.insert(tk.END, text, tag)
        self.chat_box.see(tk.END)
        self.chat_box.configure(state=tk.DISABLED)

    def _clear_chat_box(self, *args):
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.delete(0.0, tk.END)
        self.chat_box.configure(state=tk.DISABLED)

    def set_notification_sound(self, path):
        if path is None:
            self.notification_sound = None
            return 0
        if not os.path.exists(path):
            return -1
        if os.path.splitext(path)[1].lower() != '.wav':
            return -2
        self.notification_sound = path
        return 0

    def increase_font_size(self, *args):
        if self.font_size == 20:
            return
        self.font_size += 1
        self.chat_box.configure(font=(self.font_family, self.font_size))
        self.user_input.configure(font=(self.font_family, self.font_size))
        self.update_idletasks()

    def decrease_font_size(self, *args):
        if self.font_size == 10:
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
            self._write_config()
            self.quit()
        else:
            answer = messagebox.askyesno('Disconnect?',
                                         f'Are you sure you want to disconnect from the current chatroom?')
            if answer:
                self.tcp_client.close_connection()
                self._write_config()
                self.quit()
            else:
                return

    def connect(self, host, port, user_id):
        self._write_to_chat_box(f"-- Connecting to {host} at port {port} --", tag="Center")
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
            self._clear_chat_box()
            self.tcp_client.close_connection(force=True)
        else:
            self.title(f"Connected to {host} at port {port} | Username: {user_id}")
            self.user_input.configure(state=tk.NORMAL)

    def disconnect(self):
        if self.tcp_client.is_connected():
            self.tcp_client.close_connection()
            self._write_to_chat_box(f"-- Disconnected from host --", tag="Center")
            self._reset_gui()
            return True
        else:
            self._write_to_chat_box(f"-- Disconnected from host --", tag="Center")
            self._reset_gui()
            return None

    def send_msg(self, *args):
        if not self.tcp_client.is_connected():
            return
        text = self.user_input.get()
        self.user_input.delete(0, tk.END)
        result = self.tcp_client.send(text)
        if not result:
            messagebox.showerror(title="Error", message=f"Host closed connection")
            self.disconnect()

    def process_msg(self, sender, msg):
        self._write_to_chat_box(f"{sender}", self.member_colors[sender], newline=False)
        self._write_to_chat_box(f": {msg}")
        if sender != self.tcp_client.get_user_id():
            self._play_notification_sound()

    def process_info_msg(self, msg):
        if msg == "":
            return
        data = msg.split(':')
        if data[0] == 'JOINED':
            self._write_to_chat_box(f"-- {data[1]} joined the server --", tag="Center")
            if data[1] not in self.room_members:
                self.room_members.append(data[1])
                color = random.choice(self.available_colors)
                self.available_colors.remove(color)
                self.member_colors.update({data[1]: color})
        elif data[0] == 'LEFT':
            self._write_to_chat_box(f"-- {data[1]} left the server --", tag="Center")
            if data[1] in self.room_members:
                self.room_members.remove(data[1])
                color = self.member_colors[data[1]]
                del self.member_colors[data[1]]
                self.available_colors.append(color)
        elif data[0] == 'MEMBERS':
            for user_id in data[1].split(','):
                if user_id not in self.room_members:
                    self.room_members.append(user_id)
                    color = random.choice(self.available_colors)
                    self.available_colors.remove(color)
                    self.member_colors.update({user_id: color})
        elif data[0] == "KICKED":
            self._write_to_chat_box(f"-- You were kicked from the chat room --", tag="Center")
            self.tcp_client.close_connection(force=True)
        elif data[0] == "SERVERMSG":
            self._write_to_chat_box(f"SERVER MESSAGE: {data[1]}", tag="Center")
        else:
            return
        self._play_notification_sound()

