"""
Main Window
Written by Joshua Kitchen - 2023
"""
import tkinter as tk
from tkinter import messagebox, filedialog, font as tkfont
import random
import os
import re
import threading
import socket
import io
from PIL import Image, ImageTk

import utils
from .menu_bar import MenuBar
from client.backend.pychat_backend import PychatClient
from client.backend.exceptions import UserIDTaken, ServerFull, UserIDTooLong
from client.gui.notify_sound import NotificationSound
from client.gui.chat_box import ChatBox
from client.gui.input_box import InputBox
from client.gui.mp3_player import MP3Player


class MainWin(tk.Tk):
    def __init__(self, connection_info=None):
        tk.Tk.__init__(self)
        self.tcp_client = PychatClient(self, None)
        self.available_colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF",
            "#800000", "#008000", "#000080", "#808000", "#800080", "#008080",
            "#FFA500", "#A52A2A", "#2E8B57", "#4682B4", "#DA70D6", "#FFD700",
            "#DC143C", "#7FFF00", "#1E90FF", "#FF1493", "#20B2AA", "#FF6347",
            "#ADFF2F", "#40E0D0", "#BA55D3", "#FF4500", "#6A5ACD", "#9ACD32",
            "#FF69B4", "#87CEEB", "#32CD32", "#8B0000", "#006400", "#000000"
        ]
        self.notification_sounds = [
            NotificationSound('', None),
            NotificationSound('client/sounds/the-notification-email-143029.wav', 'Classic'),
            NotificationSound('client/sounds/notification-140376.wav', 'Outer Space'),
            NotificationSound('client/sounds/notification-126507.wav', 'Alert'),
            NotificationSound('client/sounds/message-13716.wav', 'Deep Sea')
        ]

        self.FONT_CHOOSE_WIN = None
        self.room_members = []
        self.member_colors = {}
        self.widget_bg = '#ffffff'
        self.widget_fg = '#000000'
        self.app_bg = "#001a4d"
        self.font_family = 'Arial'
        self.font_size = 12
        self.font = (self.font_family, self.font_size)
        self.padx = 8
        self.pady = 8
        self.notification_sound = self.notification_sounds[0]
        self.read_config()
        self.protocol('WM_DELETE_WINDOW', self.close_window)
        self.chat_area_frame = tk.Frame(self, background=self.app_bg)
        self.input_frame = InputBox(self, master=self.chat_area_frame, background=self.app_bg)
        self.chat_box_frame = ChatBox(self, master=self.chat_area_frame, width=800, height=500)
        self.menubar = MenuBar(self, self.font_family, self.notification_sound)
        self.configure(menu=self.menubar)
        self.images = []
        self.save_img_menu = tk.Menu(self.chat_box_frame, tearoff=False)
        self.save_img_menu.add_command(label="Save image", command=self.save_image)
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
        self.chat_box_frame.bind_all("<Button-3>", self.context_menu)
        if os.name == 'posix':
            self.chat_box_frame.bind_all("<Button-4>", self.on_mousewheel_linux)
            self.chat_box_frame.bind_all("<Button-5>", self.on_mousewheel_linux)
        elif os.name == 'nt':
            self.chat_box_frame.bind_all("<MouseWheel>", self.on_mousewheel_windows)
        else:
            print(f"This app does not support mouse scrolling on OS '{os.name}'")
        self.reset_gui()
        if connection_info is not None:
            threading.Thread(target=self.connect, daemon=True,
                             args=[connection_info[0], connection_info[1], connection_info[2]]).start()

    def on_mousewheel_windows(self, event):
        self.chat_box_frame.chat_box.yview("scroll", int(-1*(event.delta/120)), "units")
        return 'break'

    def on_mousewheel_linux(self, event):
        if event.num == 4:
            self.chat_box_frame.chat_box.yview("scroll", -1, "units")
        else:
            self.chat_box_frame.chat_box.yview("scroll", 1, "units")
        return 'break'

    def context_menu(self, event):
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

    def save_image(self):
        if self.last_img_clicked is None:
            return
        filename = self.last_img_clicked[0]
        img = self.last_img_clicked[1]
        path = filedialog.asksaveasfilename(initialfile=filename)
        utils.save_image(img, filename, path)

    def read_config(self):
        if os.path.exists('.config'):
            with open('.config', 'r') as file:
                lines = file.readlines()
            try:
                self.font_family = lines[0].split('=')[1].strip('\n')
                if self.font_family not in tkfont.families():
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
                notification = lines[3].split('=')[1].strip('\n')
                for sound in self.notification_sounds:
                    if sound.name == notification:
                        self.notification_sound = sound
                        break
            except IndexError:
                self.app_bg = "#001a4d"
                self.font_family = 'Arial'
                self.font_size = 12
                self.set_notification_sound(self.notification_sounds[0])
                self.write_config()
        else:
            self.write_config()

    def write_config(self):
        with open('.config', 'w') as file:
            file.write(f"font={self.font_family}\n"
                       f"fontsize={self.font_size}\n"
                       f"bg={self.app_bg}\n"
                       f"notify={self.notification_sound.name}")

    def reset_gui(self):
        self.title("Pychat")
        self.chat_box_frame.clear_chat_box()
        self.input_frame.user_input.configure(state=tk.DISABLED)

    def play_notification_sound(self):
        if self.notification_sound is None:
            return
        self.notification_sound.play()

    def set_notification_sound(self, playback_obj):
        self.notification_sound = playback_obj

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
            self.write_config()
            self.quit()
        else:
            answer = messagebox.askyesno('Disconnect?',
                                         f'Are you sure you want to disconnect from the current chatroom?')
            if answer:
                self.disconnect(warn=True)
                self.write_config()
                self.quit()
            else:
                return

    def connect(self, host, port, user_id):
        self.chat_box_frame.write_to_chat_box(f"-- Connecting to {host} at port {port} --", tags=["Center"])
        self.tcp_client.set_username(user_id)
        try:
            result = self.tcp_client.init_connection((host, port))
        except UserIDTaken:
            self.handle_error(f"Username {user_id} has been taken")
            return
        except UserIDTooLong:
            self.handle_error(f"Username {user_id} is too long")
            return
        except ServerFull:
            self.handle_error(f"Room {host} at port {port} is full")
            return
        except TimeoutError:
            self.handle_error(f"Connection to {host} at port {port} has timed out")
            return
        except ConnectionError:
            self.handle_error(f"Could not connect to {host} at port {port}")
            return
        except socket.gaierror:
            self.handle_error(f"Host address {host} is invalid")
            return

        if not result:
            self.handle_error(f"Could not connect to {host} at port {port}")
            return

        self.title(f"Connected to {host} at port {port} | Username: {user_id}")
        self.chat_box_frame.write_to_chat_box(f"-- Connected to {host} at port {port} | Username: {user_id} --",
                                              tags=["Center"])
        threading.Thread(target=self.tcp_client.msg_loop, daemon=True).start()
        self.input_frame.user_input.configure(state=tk.NORMAL)

    def handle_error(self, err_msg):
        self.disconnect()
        self.reset_gui()
        messagebox.showerror(title="Error", message=err_msg)

    def disconnect(self, warn=False):
        if self.tcp_client.is_connected():
            self.tcp_client.disconnect(warn=warn)
            self.reset_gui()
            self.chat_box_frame.write_to_chat_box(f"-- Disconnected from host --", tags=["Center"])

    def send_msg(self, *args):
        if not self.tcp_client.is_connected():
            return
        text = self.input_frame.get_input()
        result = self.tcp_client.send_chat_msg(bytes(text, encoding='utf-8'), 1)
        if not result:
            messagebox.showerror(title="Error", message=f"Host closed connection")
            self.disconnect()

    def send_sound_msg(self, *args):
        if not self.tcp_client.is_connected():
            return

        path = filedialog.askopenfilename(filetypes=[(".mp3", "*.mp3")])
        if path == () or path == '':
            return

        try:
            with open(path, 'rb') as file:
                data = file.read()
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
        result = self.tcp_client.send_multimedia_msg(filename, data)
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
        result = self.tcp_client.send_multimedia_msg(filename, data.getvalue())
        if not result:
            messagebox.showerror(title="Error", message=f"Host closed connection")
            self.disconnect()

    def process_msg(self, sender, msg):
        if sender == "SERVER":
            self.chat_box_frame.write_to_chat_box("SERVER MSG", "red", newline=False)
        else:
            self.chat_box_frame.write_to_chat_box(f"{sender}", tags=[self.member_colors[sender]], newline=False)
        self.chat_box_frame.write_to_chat_box(f": {msg}")
        if sender != self.tcp_client.username:
            self.play_notification_sound()

    def process_multimedia_msg(self, sender, data):
        filename_len = int.from_bytes(data[0:4], byteorder='big')
        filename = str(data[4: filename_len + 4], 'utf-8')
        ext = filename.split('.')[-1]
        if ext.lower() == "mp3":
            self.show_sound_msg(sender, data[filename_len + 4:], filename)
        elif ext.lower() in ["jpg", "jpeg", "png", "gif"]:
            self.show_image_msg(sender, data[filename_len + 4:], filename)

    def show_sound_msg(self, sender, data, filename):
        with open(filename, 'wb') as file:
            file.write(data)
        player = MP3Player(self.font)
        player.load(filename)
        self.chat_box_frame.write_to_chat_box(f"{sender}: ", self.member_colors[sender], newline=True)
        self.chat_box_frame.chat_box.window_create(tk.END, window=player)
        self.chat_box_frame.write_to_chat_box("\n")

    def show_image_msg(self, sender, data , filename):
        file = io.BytesIO(data)
        image = ImageTk.PhotoImage(Image.open(file))
        self.images.append((filename, image))
        self.chat_box_frame.write_to_chat_box(f"{sender}: ", self.member_colors[sender], newline=False)
        self.chat_box_frame.write_to_chat_box(f"{filename}")
        self.chat_box_frame.chat_box.window_create(tk.END, window = tk.Label(self.chat_box_frame.chat_box, image=image, text=filename))
        self.chat_box_frame.write_to_chat_box("\n")

    def process_info_msg(self, msg):
        if msg == "":
            return
        data = msg.split(':')
        if data[0] == 'JOINED':
            self.chat_box_frame.write_to_chat_box(f"-- {data[1]} joined the server --", tags=["Center"])
            if data[1] not in self.room_members:
                self.room_members.append(data[1])
                color = random.choice(self.available_colors)
                self.available_colors.remove(color)
                self.member_colors.update({data[1]: color})
        elif data[0] == 'LEFT':
            self.chat_box_frame.write_to_chat_box(f"-- {data[1]} left the server --", tags=["Center"])
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
            self.chat_box_frame.write_to_chat_box(f"-- You were kicked from the chat room --", tags=["Center"])
            self.tcp_client.disconnect()
        elif data[0] == "SERVERMSG":
            self.chat_box_frame.write_to_chat_box(f"SERVER MESSAGE: {data[1]}", tags=["#a31f1f", "Center"])
                                                                                           # ^^^^
        else:                                                                              # For some reason tkinter
            return                                                                         # does not want to make the
        self.play_notification_sound()                                                     # damn text red no matter what
                                                                                           # I fucking put in there!