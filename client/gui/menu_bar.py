import tkinter as tk
from tkinter import filedialog, colorchooser
from pathlib import Path

from gui.connect_dialog import ConnectDialog


class MainMenu(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self)
        self.parent = parent

        self.file_menu = tk.Menu(self.parent, tearoff=0)
        self.edit_menu = tk.Menu(self.parent, tearoff=0)
        self.connect_menu = tk.Menu(self.parent, tearoff=0)

        self.file_menu.add_command(label="Clear chat", command=self.clear_chat)
        self.file_menu.add_command(label="Archive chat", command=self.archive_chat)

        self.edit_menu.add_command(label="Copy", command=self.copy)
        self.edit_menu.add_command(label="Cut", command=self.cut)
        self.edit_menu.add_command(label="Paste", command=self.paste)
        self.edit_menu.add_command(label="Change accent color", command=self.change_accent)

        self.connect_menu.add_command(label="Connect to chatroom", command=self.connect_to_room)
        self.connect_menu.add_command(label="Disconnect from chatroom", command=self.disconnect_from_room)

        self.add_cascade(menu=self.file_menu, label="File")
        self.add_cascade(menu=self.edit_menu, label="Edit")
        self.add_cascade(menu=self.connect_menu, label="Connect")

    def archive_chat(self):
        chat_text = self.parent.chat_box.get(0.0, tk.END)
        chosen_filepath = filedialog.asksaveasfilename(filetypes=[('All', '*'), ('.txt', '*.txt')],
                                                       initialdir=Path.home())
        if chosen_filepath == ():
            return

        with open(chosen_filepath, 'a+') as file:
            file.write(chat_text)

    def clear_chat(self):
        self.parent.chat_box.delete(0.0, tk.END)

    def copy(self):
        widget = self.parent.focus_get()
        if widget is self.parent.chat_box or widget is self.parent.user_input:
            widget.event_generate('<<Copy>>')

    def cut(self):
        widget = self.parent.focus_get()
        if widget is self.parent.user_input:
            widget.event_generate('<<Cut>>')

    def paste(self):
        widget = self.parent.focus_get()
        if widget is self.parent.user_input:
            widget.event_generate('<<Paste>>')

    def change_accent(self):
        color = colorchooser.askcolor()
        if color is None:
            return
        self.parent.chat_frame.configure(background=color[1])
        self.parent.input_frame.configure(background=color[1])

    def connect_to_room(self):
        if self.parent.tcp_client.is_connecting is True:
            return
        if self.parent.tcp_client.soc is not None:
            self.parent.tcp_client.soc.close()
        w = tk.Toplevel()
        c = ConnectDialog(w, self.parent)

    def disconnect_from_room(self):
        if self.parent.tcp_client.soc is not None:
            self.parent.tcp_client.soc.close()
            self.parent.chat_box.insert(tk.END, f"Disconnected from {self.parent.tcp_client.host}")
            self.parent.title(f"Pychat")
            self.parent.parent.tcp_client.soc = None
            self.parent.parent.tcp_client.host = None
            self.parent.parent.tcp_client.port = None
