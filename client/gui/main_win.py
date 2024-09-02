"""
Main Window
Written by Joshua Kitchen - 2023

All messages are sent in this format:
    "[header]\n[message]"

The INFO header is used when the server and the client need to pass along information. Messages with this header include
an additional header within the message indicating what kind of information was sent. The header and the message are
delimited by a colon. Possible INFO messages are:
- JOINED:<user id>
- LEFT:<user id>
- MEMBERS:<list of connected users>
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

from .menu_bar import MenuBar
from client.backend.pychat_client import PychatClient
from client.backend.exceptions import UserIDTaken, ServerFull, UserIDTooLong
from client.gui.chat_box import ChatBox

class MainWin(tk.Tk):
    def __init__(self, connection_info=None):
        tk.Tk.__init__(self)
        self._tcp_client = PychatClient(self, None)
        self.notification_sounds = [
            (None, 'None'),
            ('sounds/the-notification-email-143029.wav', 'Classic'),
            ('sounds/notification-140376.wav', 'Outer Space'),
            ('sounds/notification-126507.wav', 'Alert'),
            ('sounds/message-13716.wav', 'Deep Sea')
        ]
        self.fonts = ['Arial', 'Calibri', 'Cambria', 'Comic Sans MS', 'Lucida Console', 'Segoe UI', 'Wingdings']
        self.widget_bg = '#ffffff'
        self.widget_fg = '#000000'
        self.app_bg = "#001a4d"
        self.font_family = 'Arial'
        self.font_size = 12
        self.font = (self.font_family, self.font_size)
        self.padx = 8
        self.pady = 8
        self.notification_sound = None
        self._read_config()
        self.protocol('WM_DELETE_WINDOW', self.close_window)
        self.chat_area_frame = tk.Frame(self, background=self.app_bg)
        self.input_frame = tk.Frame(self, background=self.app_bg)
        self.chat_box_frame = ChatBox(self, master=self.chat_area_frame, width=800, height=500)
        self.menubar = MenuBar(self, self.font_family, self.notification_sound)
        self.configure(menu=self.menubar)

        vcmd = (self.register(self._on_key_release), '%P')
        self.user_input = tk.Entry(self.input_frame, background=self.widget_bg, foreground=self.widget_fg,
                                   font=self.font, insertbackground=self.widget_fg, disabledbackground=self.widget_bg,
                                   relief=tk.FLAT, validate="key", validatecommand=vcmd)
        self.char_count_var = tk.StringVar()
        self.char_count_var.set("0/150")
        self.char_limit_label = tk.Label(self.input_frame, textvariable=self.char_count_var, background=self.widget_bg,
                                         foreground=self.widget_fg, font=self.font)
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_msg, background=self.widget_bg,
                                     foreground=self.widget_fg, relief=tk.FLAT, height=2, width=10)

        # The order in which these widgets are packed matters! This order ensures proper widget resizing when the
        # window is resized.
        self.chat_box_frame.pack_propagate(False)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.send_button.pack(fill=tk.X, side=tk.RIGHT, pady=(0, self.pady), padx=(5, 5))
        self.char_limit_label.pack(fill=tk.BOTH, side=tk.RIGHT, pady=(0, self.pady))
        self.user_input.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(self.padx, 0), pady=(0, self.pady))
        self.chat_area_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.chat_box_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(self.padx, 0), pady=self.pady)
        self.chat_box_frame.pack_widgets()

        self.user_input.bind("<Return>", self.send_msg)
        self.bind("<Control-Delete>", self.chat_box_frame._clear_chat_box)
        self.bind("<Control_L>s", self.menubar.archive_chat)
        self.bind("<Control_L>c", self.menubar.copy)
        self.bind("<Control-Up>", self.increase_font_size)
        self.bind("<Control-Down>", self.decrease_font_size)
        self.bind("<Control_L>n", self.menubar.connect_to_room)
        self.bind("<Control-End>", self.menubar.disconnect_from_room)
        self.send_button.bind("<Enter>", self._on_btn_enter)
        self.send_button.bind("<Leave>", self._on_btn_leave)

        self._reset_gui()
        if connection_info is not None:
            threading.Thread(target=self.connect, daemon=True,
                             args=[connection_info[0], connection_info[1], connection_info[2]]).start()

    def _on_key_release(self, text):
        if len(text) == 151:
            return False
        else:
            self.char_count_var.set(f"{len(text)}/150")
            return True

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




    def create_member_list(self, data):
        data = data.split(',')
        data.append(self._tcp_client.username)
        for user_id in data:
            if user_id == '':
                continue
            if user_id not in self.chat_box_frame._room_members:
                self.chat_box_frame._room_members.append(user_id)
                color = random.choice(self.chat_box_frame._available_colors)
                self.chat_box_frame._available_colors.remove(color)
                self.chat_box_frame._member_colors.update({user_id: color})

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
        self.chat_box_frame.chat_box.configure(font=(self.font_family, self.font_size))
        self.user_input.configure(font=(self.font_family, self.font_size))
        self.update_idletasks()

    def decrease_font_size(self, *args):
        if self.font_size == 10:
            return
        self.font_size -= 1
        self.chat_box_frame.chat_box.configure(font=(self.font_family, self.font_size))
        self.user_input.configure(font=(self.font_family, self.font_size))
        self.update_idletasks()

    def change_font(self, new_font):
        self.font_family = new_font
        self.chat_box_frame.chat_box.configure(font=(self.font_family, self.font_size))
        self.user_input.configure(font=(self.font_family, self.font_size))
        self.update_idletasks()

    def close_window(self):
        if not self._tcp_client.is_connected():
            self._write_config()
            self.quit()
        else:
            answer = messagebox.askyesno('Disconnect?',
                                         f'Are you sure you want to disconnect from the current chatroom?')
            if answer:
                self.disconnect()
                self._write_config()
                self.quit()
            else:
                return

    def connect(self, host, port, user_id):
        self.chat_box_frame._write_to_chat_box(f"-- Connecting to {host} at port {port} --", tag="Center")
        self._tcp_client.set_addr(host, port)
        self._tcp_client.set_username(user_id)
        result = self._tcp_client.init_connection()
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
            self.chat_box_frame._clear_chat_box()
            self._tcp_client.disconnect()
            self.show_error(error_msg)
        else:
            self.title(f"Connected to {host} at port {port} | Username: {user_id}")
            self.chat_box_frame._write_to_chat_box(f"-- Connected to {host} at port {port} | Username: {user_id} --", tag="Center")
            threading.Thread(target=self._tcp_client.msg_loop).start()
            self.user_input.configure(state=tk.NORMAL)

    def show_error(self, message):
        self._reset_gui()
        messagebox.showerror(title="Error", message=message)

    def disconnect(self):
        if self._tcp_client.is_connected():
            self._tcp_client.disconnect(warn=True)
            self._reset_gui()
            self.chat_box_frame._write_to_chat_box(f"-- Disconnected from host --", tag="Center")

    def send_msg(self, *args):
        if not self._tcp_client.is_connected():
            return
        self.char_count_var.set("0/250")
        self.char_limit_label = 0
        text = self.user_input.get()
        self.user_input.delete(0, tk.END)
        result = self._tcp_client.send_chat_msg(bytes(text, encoding='utf-8'), 1)
        if not result:
            messagebox.showerror(title="Error", message=f"Host closed connection")
            self.disconnect()

    def process_msg(self, sender, msg):
        self.chat_box_frame._write_to_chat_box(f"{sender}", self.chat_box_frame._member_colors[sender], newline=False)
        self.chat_box_frame._write_to_chat_box(f": {msg}")
        if sender != self._tcp_client.username:
            self._play_notification_sound()

    def process_info_msg(self, msg):
        if msg == "":
            return
        data = msg.split(':')
        if data[0] == 'JOINED':
            self.chat_box_frame._write_to_chat_box(f"-- {data[1]} joined the server --", tag="Center")
            if data[1] not in self.chat_box_frame._room_members:
                self.chat_box_frame._room_members.append(data[1])
                color = random.choice(self.chat_box_frame._available_colors)
                self.chat_box_frame._available_colors.remove(color)
                self.chat_box_frame._member_colors.update({data[1]: color})
        elif data[0] == 'LEFT':
            self.chat_box_frame._write_to_chat_box(f"-- {data[1]} left the server --", tag="Center")
            if data[1] in self.chat_box_frame._room_members:
                self.chat_box_frame._room_members.remove(data[1])
                color = self.chat_box_frame._member_colors[data[1]]
                del self.chat_box_frame._member_colors[data[1]]
                self.chat_box_frame._available_colors.append(color)
        elif data[0] == 'MEMBERS':
            for user_id in data[1].split(','):
                if user_id not in self.chat_box_frame._room_members:
                    self.chat_box_frame._room_members.append(user_id)
                    color = random.choice(self.chat_box_frame._available_colors)
                    self.chat_box_frame._available_colors.remove(color)
                    self.chat_box_frame._member_colors.update({user_id: color})
        elif data[0] == "KICKED":
            self.chat_box_frame._write_to_chat_box(f"-- You were kicked from the chat room --", tag="Center")
            self._tcp_client.disconnect()
        elif data[0] == "SERVERMSG":
            self.chat_box_frame._write_to_chat_box(f"SERVER MESSAGE: {data[1]}", tag="Center")
        else:
            return
        self._play_notification_sound()
