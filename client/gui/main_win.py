"""
Main Window
Written by Joshua Kitchen - 2023
"""


import tkinter as tk
from tkinter import messagebox, filedialog
import random
import os
import re
import threading
import playsound
import socket
import io
from PIL import Image, ImageTk

import utils
from .menu_bar import MenuBar
from client.backend.pychat_client import PychatClient
from client.backend.exceptions import UserIDTaken, ServerFull, UserIDTooLong
from client.gui.chat_box import ChatBox
from client.gui.input_box import InputBox

class MainWin(tk.Tk):
    def __init__(self, connection_info=None):
        tk.Tk.__init__(self)
        self.tcp_client = PychatClient(self, None)
        self.available_colors = [
            '#000066', '#0000ff', '#0099cc', '#006666',
            '#006600', '#003300', '#669900', '#e68a00',
            '#ff471a', '#ff8080', '#b30000', '#660000',
            '#e6005c', '#d966ff', '#4d004d', '#8600b3'
        ]

        self.room_members = []
        self.member_colors = {}
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
        self.input_frame = InputBox(self, master=self.chat_area_frame, background=self.app_bg)
        self.chat_box_frame = ChatBox(self, master=self.chat_area_frame, width=800, height=500)
        self.menubar = MenuBar(self, self.font_family, self.notification_sound)
        self.configure(menu=self.menubar)
        self.images = []
        self.save_img_menu = tk.Menu(self.chat_box_frame, tearoff=False)
        self.save_img_menu.add_command(label="Save image", command=self._save_image)
        self.last_img_clicked = None # Tuple (img, filename)
        # The order in which these widgets are packed matters! This order ensures proper widget resizing when the
        # window is resized.
        self.chat_box_frame.pack_propagate(False)
        self.chat_area_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)
        self.input_frame.pack_widgets()
        self.chat_box_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(self.padx, 0), pady=self.pady)
        self.chat_box_frame.pack_widgets()

        self.bind("<Control-Delete>", self.chat_box_frame.clear_chat_box)
        self.bind("<Control_L>s", self.menubar.archive_chat)
        self.bind("<Control_L>c", self.menubar.copy)
        self.bind("<Control-Up>", self.increase_font_size)
        self.bind("<Control-Down>", self.decrease_font_size)
        self.bind("<Control_L>n", self.menubar.connect_to_room)
        self.bind("<Control-End>", self.menubar.disconnect_from_room)
        self.chat_box_frame.bind_all("<Button-3>", self._context_menu)
        if os.name == 'posix':
            self.chat_box_frame.bind_all("<Button-4>", self._on_mousewheel_linux)
            self.chat_box_frame.bind_all("<Button-5>", self._on_mousewheel_linux)
        elif os.name == 'nt':
            self.chat_box_frame.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        else:
            print(f"This app does not support OS '{os.name}'")
            self.quit()

        self._reset_gui()
        if connection_info is not None:
            threading.Thread(target=self.connect, daemon=True,
                             args=[connection_info[0], connection_info[1], connection_info[2]]).start()

    def _on_mousewheel_windows(self, event):
        self.chat_box_frame.chat_box.yview("scroll", int(-1*(event.delta/120)), "units")
        return 'break'

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.chat_box_frame.chat_box.yview("scroll", -1, "units")
        else:
            self.chat_box_frame.chat_box.yview("scroll", 1, "units")
        return 'break'

    def _context_menu(self, event):
        if isinstance(event.widget, tk.Label):
            filename = event.widget.cget("text")
            image = None
            for i in self.images:
                if i[0] == filename:
                    image = i[1]
                    break
            if not image:
                return
            self.last_img_clicked = (filename, ImageTk.getimage(image))
            self.save_img_menu.post(event.x_root, event.y_root)

    def _save_image(self):
        if self.last_img_clicked is None:
            return
        filename = self.last_img_clicked[0]
        img = self.last_img_clicked[1]
        path = filedialog.asksaveasfilename(initialfile=filename)
        utils.save_image(img, filename, path)

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
        self.input_frame.user_input.configure(state=tk.DISABLED)

    def create_member_list(self, data):
        data = data.split(',')
        data.append(self.tcp_client.username)
        for user_id in data:
            if user_id == '':
                continue
            if user_id not in self.room_members:
                self.room_members.append(user_id)
                color = random.choice(self.available_colors)
                self.available_colors.remove(color)
                self.member_colors.update({user_id: color})

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
        self.chat_box_frame.update_font()
        self.input_frame.update_font()
        self.update_idletasks()

    def decrease_font_size(self, *args):
        if self.font_size == 10:
            return
        self.font_size -= 1
        self.chat_box_frame.update_font()
        self.input_frame.update_font()
        self.update_idletasks()

    def change_font(self, new_font):
        self.font_family = new_font
        self.chat_box_frame.update_font()
        self.input_frame.update_font()
        self.update_idletasks()

    def close_window(self):
        if not self.tcp_client.is_connected():
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
        self.chat_box_frame.write_to_chat_box(f"-- Connecting to {host} at port {port} --", tag="Center")
        self.tcp_client.set_addr(host, port)
        self.tcp_client.set_username(user_id)
        result = self.tcp_client.init_connection()
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
            self.chat_box_frame.clear_chat_box()
            self.tcp_client.disconnect()
            self.show_error(error_msg)
        else:
            self.title(f"Connected to {host} at port {port} | Username: {user_id}")
            self.chat_box_frame.write_to_chat_box(f"-- Connected to {host} at port {port} | Username: {user_id} --", tag="Center")
            threading.Thread(target=self.tcp_client.msg_loop).start()
            self.input_frame.user_input.configure(state=tk.NORMAL)

    def show_error(self, message):
        self._reset_gui()
        messagebox.showerror(title="Error", message=message)

    def disconnect(self):
        if self.tcp_client.is_connected():
            self.tcp_client.disconnect(warn=True)
            self._reset_gui()
            self.chat_box_frame.write_to_chat_box(f"-- Disconnected from host --", tag="Center")

    def send_msg(self, *args):
        if not self.tcp_client.is_connected():
            return
        text = self.input_frame.get_input()
        result = self.tcp_client.send_chat_msg(bytes(text, encoding='utf-8'), 1)
        if not result:
            messagebox.showerror(title="Error", message=f"Host closed connection")
            self.disconnect()

    def send_image_msg(self, *args):
        if not self.tcp_client.is_connected():
            return

        path = filedialog.askopenfilename(filetypes=[(".jpg", "*.jpg *.jpeg"),  (".png", "*.png"), (".gif", "*.gif")])
        if path == () or path == '':
            return

        try:
            img = Image.open(path)
        except FileNotFoundError:
            messagebox.showerror(title='Error', message=f"Cannot open {path}")
            return
        except PermissionError:
            messagebox.showerror(title='Error', message=f"No permission to open {path}")
            return
        except OSError:
            messagebox.showerror(title='Error', message=f"Error opening {path}")
            return

        filename = os.path.split(path)[-1]
        data = io.BytesIO()
        img.thumbnail((600, 400))
        utils.save_image(img, filename, data)
        result = self.tcp_client.send_pic_msg(filename, data.getvalue())
        if not result:
            messagebox.showerror(title="Error", message=f"Host closed connection")
            self.disconnect()

    def process_msg(self, sender, msg):
        self.chat_box_frame.write_to_chat_box(f"{sender}", self.member_colors[sender], newline=False)
        self.chat_box_frame.write_to_chat_box(f": {msg}")
        if sender != self.tcp_client.username:
            self._play_notification_sound()

    def process_image_msg(self, sender, data):
        filename_len = int.from_bytes(data[0:4], byteorder='big')
        filename = str(data[4: filename_len + 4], 'utf-8')
        file = io.BytesIO(data[filename_len + 4:])
        image = ImageTk.PhotoImage(Image.open(file))
        self.images.append((filename, image))
        self.chat_box_frame.write_to_chat_box(f"{sender}: ", self.member_colors[sender], newline=False)
        self.chat_box_frame.write_to_chat_box(f"{filename}")
        self.chat_box_frame.chat_box.window_create(tk.END, window = tk.Label(self.chat_box_frame.chat_box, image=image, text=filename))
        self.chat_box_frame.write_to_chat_box("")

    def process_info_msg(self, msg):
        if msg == "":
            return
        data = msg.split(':')
        if data[0] == 'JOINED':
            self.chat_box_frame.write_to_chat_box(f"-- {data[1]} joined the server --", tag="Center")
            if data[1] not in self.room_members:
                self.room_members.append(data[1])
                color = random.choice(self.available_colors)
                self.available_colors.remove(color)
                self.member_colors.update({data[1]: color})
        elif data[0] == 'LEFT':
            self.chat_box_frame.write_to_chat_box(f"-- {data[1]} left the server --", tag="Center")
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
            self.chat_box_frame.write_to_chat_box(f"-- You were kicked from the chat room --", tag="Center")
            self.tcp_client.disconnect()
        elif data[0] == "SERVERMSG":
            self.chat_box_frame.write_to_chat_box(f"SERVER MESSAGE: {data[1]}", tag="Center")
        else:
            return
        self._play_notification_sound()
