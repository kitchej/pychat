"""
Menu Bar
Written by Joshua Kitchen - 2023
"""

import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, font as tkfont
from datetime import datetime
import os
from PIL import ImageTk

import utils
from client.gui.connect_dialog import ConnectDialog
from client.gui.font_chooser import FontChooser
from client.gui.about_dialog import AboutDialog


class MenuBar(tk.Menu):

    def __init__(self, parent, notification_sound):
        tk.Menu.__init__(self)
        self.parent = parent
        self.FONT_CHOOSE_WIN = None
        self.CONNECT_WIN = None
        self.ABOUT_WIN = None
        self.file_menu = tk.Menu(self.parent, tearoff=0)
        self.edit_menu = tk.Menu(self.parent, tearoff=0)
        self.connect_menu = tk.Menu(self.parent, tearoff=0)
        self.options_menu = tk.Menu(self.parent, tearoff=0)
        self.font_menu = tk.Menu(self.parent, tearoff=0)
        self.sound_menu = tk.Menu(self.parent, tearoff=0)

        self.file_menu.add_command(label="Clear chat", command=self.parent.chat_box_frame.clear_chat_box, accelerator="Ctrl+Del")
        self.file_menu.add_command(label="Archive chat", command=self.archive_chat, accelerator="Ctrl+S")
        self.edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Cut", command=lambda: self.parent.user_input.event_generate('<<Cut>>'),
                                   accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Paste", command=lambda: self.parent.user_input.event_generate('<<Paste>>'),
                                   accelerator="Ctrl+V")
        self.connect_menu.add_command(label="Connect to new chatroom", command=self.connect_to_room,
                                      accelerator="Ctrl+N")
        self.connect_menu.add_command(label="Disconnect from chatroom", command=self.disconnect_from_room,
                                      accelerator="Ctrl+End")
        self.options_menu.add_command(label="Increase font size", command=self.parent.increase_font_size,
                                      accelerator="Ctrl+Up Arrow")
        self.options_menu.add_command(label="Decrease font size", command=self.parent.decrease_font_size,
                                      accelerator="Ctrl+Down Arrow")
        self.options_menu.add_command(label="Change font", command=self.change_font)
        self.options_menu.add_cascade(label="Change Notification Sound", menu=self.sound_menu)
        self.options_menu.add_command(label="Change background color", command=self.change_bg)
        self.notification_radio_var = tk.IntVar()

        for i, sound in enumerate(self.parent.notification_sounds):
            self.sound_menu.add_radiobutton(label=sound.name, var=self.notification_radio_var, value=i,
                                            command=lambda s=sound: self.change_notification_sound(s))
            if sound is notification_sound:
                self.notification_radio_var.set(i)

        self.add_cascade(menu=self.file_menu, label="File")
        self.add_cascade(menu=self.edit_menu, label="Edit")
        self.add_cascade(menu=self.options_menu, label="Options")
        self.add_cascade(menu=self.connect_menu, label="Connect")
        self.add_command(label="About", command=self.show_about)


    def change_font(self):
        if isinstance(self.FONT_CHOOSE_WIN, tk.Toplevel):
            self.FONT_CHOOSE_WIN.destroy()
        self.FONT_CHOOSE_WIN = tk.Toplevel()
        self.FONT_CHOOSE_WIN.resizable(False, False)
        _ = FontChooser(self.FONT_CHOOSE_WIN, self.parent)
        self.FONT_CHOOSE_WIN.focus_set()

    def change_notification_sound(self, sound):
        self.parent.set_notification_sound(sound)
        self.parent.play_notification_sound()

    def archive_chat(self, *args):
        chat_text = self.parent.chat_box_frame.get_chat_contents()
        chosen_filepath = filedialog.askdirectory()
        if chosen_filepath == () or chosen_filepath == '':
            return
        date = datetime.now()
        with open(os.path.join(chosen_filepath, f"text_log_{date.strftime('%d-%m-%y--%I-%M-%S-%p')}.txt"), 'a+') as file:
            file.write(chat_text)
        for filename, pic in self.parent.images:
            utils.save_image(ImageTk.getimage(pic), filename, chosen_filepath)

    def copy(self, *args):
        widget = self.parent.focus_get()
        if widget is self.parent.chat_box or widget is self.parent.user_input:
            widget.event_generate('<<Copy>>')

    def change_bg(self):
        color = colorchooser.askcolor()
        if color is None:
            return
        self.parent.app_bg = color[1]
        self.parent.chat_area_frame.configure(background=self.parent.app_bg)
        self.parent.input_frame.configure(background=self.parent.app_bg)

    def connect_to_room(self, *args):
        if self.parent.client.is_connected():
            if messagebox.askyesno('Disconnect?', f'Are you sure you want to disconnect from the current chatroom?'):
                self.parent.disconnect()
            else:
                return
        if isinstance(self.CONNECT_WIN, tk.Toplevel):
            self.CONNECT_WIN.destroy()

        self.CONNECT_WIN = tk.Toplevel()
        ConnectDialog(self.CONNECT_WIN, self.parent)
        self.CONNECT_WIN.focus_set()

    def disconnect_from_room(self, *args):
        self.parent.disconnect()

    def show_about(self):
        if isinstance(self.ABOUT_WIN, tk.Toplevel):
            self.ABOUT_WIN.destroy()

        self.ABOUT_WIN = tk.Toplevel()
        self.ABOUT_WIN.resizable(width=False, height=False)
        self.ABOUT_WIN.geometry("750x500")
        self.ABOUT_WIN.title("About")

        AboutDialog(self.ABOUT_WIN, self.parent)
        self.ABOUT_WIN.focus_set()
