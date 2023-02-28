import tkinter as tk
from tkinter import filedialog, colorchooser
from pathlib import Path

from gui.connect_dialog import ConnectDialog


class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self)
        self.parent = parent

        self.file_menu = tk.Menu(self.parent, tearoff=0)
        self.edit_menu = tk.Menu(self.parent, tearoff=0)
        self.connect_menu = tk.Menu(self.parent, tearoff=0)
        self.format_menu = tk.Menu(self.parent, tearoff=0)

        self.file_menu.add_command(label="Clear chat", command=self.parent.clear_chat_box, accelerator="Ctrl+Del")
        self.file_menu.add_command(label="Archive chat", command=self.archive_chat, accelerator="Ctrl+S")

        self.edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")

        self.connect_menu.add_command(label="Connect to new chatroom", command=self.connect_to_room,
                                      accelerator="Ctrl+N")
        self.connect_menu.add_command(label="Disconnect from chatroom", command=self.disconnect_from_room,
                                      accelerator="Ctrl+End")

        self.format_menu.add_command(label="Increase font size", command=self.parent.increase_font_size,
                                     accelerator="Ctrl+Up Arrow")
        self.format_menu.add_command(label="Decrease font size", command=self.parent.decrease_font_size,
                                     accelerator="Ctrl+Down Arrow")

        self.font_menu = tk.Menu(self.parent, tearoff=0)
        for font in self.parent.fonts:
            self.font_menu.add_command(label=font, command=lambda f=font: self.parent.change_font(f))
        self.format_menu.add_cascade(label="Change font", menu=self.font_menu)
        self.format_menu.add_command(label="Change background color", command=self.change_bg)

        self.add_cascade(menu=self.file_menu, label="File")
        self.add_cascade(menu=self.edit_menu, label="Edit")
        self.add_cascade(menu=self.format_menu, label="Format")
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

    def cut(self, *args):
        widget = self.parent.focus_get()
        if widget is self.parent.user_input:
            widget.event_generate('<<Cut>>')

    def paste(self, *args):
        widget = self.parent.focus_get()
        if widget is self.parent.user_input:
            widget.event_generate('<<Paste>>')

    def change_bg(self):
        color = colorchooser.askcolor()
        if color is None:
            return
        self.parent.app_bg = color[1]
        self.parent.chat_area_frame.configure(background=self.parent.app_bg)
        self.parent.input_frame.configure(background=self.parent.app_bg)

    def connect_to_room(self, *args):
        result = self.parent.disconnect()
        if result is True or result is None:
            w = tk.Toplevel()
            c = ConnectDialog(w, self.parent)

    def disconnect_from_room(self, *args):
        self.parent.disconnect()
