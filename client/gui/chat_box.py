import tkinter as tk
from tkinter import messagebox

class ChatBox(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.parent = parent
        self._available_colors = [
            '#000066', '#0000ff', '#0099cc', '#006666',
            '#006600', '#003300', '#669900', '#e68a00',
            '#ff471a', '#ff8080', '#b30000', '#660000',
            '#e6005c', '#d966ff', '#4d004d', '#8600b3'
        ]

        self._room_members = []
        self._member_colors = {}
        self.chat_box = tk.Text(self, wrap=tk.WORD, background=self.parent.widget_bg,
                                foreground=self.parent.widget_fg, font=self.parent.font, insertbackground=self.parent.widget_bg,
                                state=tk.DISABLED)
        self.chat_scroll = tk.Scrollbar(self, command=self.chat_box.yview, background=self.parent.widget_bg)

        self.chat_box.configure(yscrollcommand=self.chat_scroll.set, relief=tk.FLAT)
        self.chat_box.tag_configure("Center", justify='center')
        for color in self._available_colors:
            self.chat_box.tag_configure(color, foreground=color)


    def pack_widgets(self):
        self.chat_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, self.parent.padx), pady=self.parent.pady)
        self.chat_box.pack(fill=tk.BOTH, expand=True)

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