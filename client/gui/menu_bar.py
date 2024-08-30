"""
Menu Bar
Written by Joshua Kitchen - 2023
"""

import tkinter as tk
from tkinter import filedialog, colorchooser
from pathlib import Path

from client.gui.connect_dialog import ConnectDialog


class MenuBar(tk.Menu):
    def __init__(self, parent, parent_font, notification_sound):
        tk.Menu.__init__(self)
        self.parent = parent
        self.file_menu = tk.Menu(self.parent, tearoff=0)
        self.edit_menu = tk.Menu(self.parent, tearoff=0)
        self.connect_menu = tk.Menu(self.parent, tearoff=0)
        self.options_menu = tk.Menu(self.parent, tearoff=0)
        self.font_menu = tk.Menu(self.parent, tearoff=0)
        self.sound_menu = tk.Menu(self.parent, tearoff=0)

        self.file_menu.add_command(label="Clear chat", command=self.parent._clear_chat_box, accelerator="Ctrl+Del")
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
        self.options_menu.add_cascade(label="Change font", menu=self.font_menu)
        self.options_menu.add_cascade(label="Change Notification Sound", menu=self.sound_menu)
        self.options_menu.add_command(label="Change background color", command=self.change_bg)

        self.font_radio_var = tk.IntVar()
        self.notification_radio_var = tk.IntVar()

        for i, font in enumerate(self.parent.fonts):
            self.font_menu.add_radiobutton(label=font, var=self.font_radio_var, value=i,
                                           command=lambda f=font: self.parent.change_font(f))
            if font == parent_font:
                self.font_radio_var.set(i)

        for i, sound in enumerate(self.parent.notification_sounds):
            self.sound_menu.add_radiobutton(label=sound[1], var=self.notification_radio_var, value=i,
                                            command=lambda f=sound[0]: self.parent.set_notification_sound(f))
            if sound[0] == notification_sound:
                self.notification_radio_var.set(i)

        self.add_cascade(menu=self.file_menu, label="File")
        self.add_cascade(menu=self.edit_menu, label="Edit")
        self.add_cascade(menu=self.options_menu, label="Options")
        self.add_cascade(menu=self.connect_menu, label="Connect")

    def archive_chat(self, *args):
        chat_text = self.parent.chat_box.get(0.0, tk.END)
        chosen_filepath = filedialog.asksaveasfilename(filetypes=[('All', '*'), ('.txt', '*.txt')],
                                                       initialdir=Path.home())
        if chosen_filepath == () or chosen_filepath == '':
            return
        with open(chosen_filepath, 'a+') as file:
            file.write(chat_text)

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
        self.parent.disconnect()
        window = tk.Toplevel()
        ConnectDialog(window, self.parent)

    def disconnect_from_room(self, *args):
        self.parent.disconnect()
