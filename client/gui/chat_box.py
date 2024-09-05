"""
Chat box
Written by Joshua Kitchen - 2024
"""


import tkinter as tk
import tkinter.ttk as ttk

class ChatBox(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.parent = parent

        self.chat_box = tk.Text(self, wrap=tk.WORD, background=self.parent.widget_bg,
                                foreground=self.parent.widget_fg, font=self.parent.font, insertbackground=self.parent.widget_bg,
                                state=tk.DISABLED, cursor="arrow")
        self.chat_scroll = ttk.Scrollbar(self, command=self.chat_box.yview)  #, background=self.parent.widget_bg

        self.chat_box.configure(yscrollcommand=self.chat_scroll.set, relief=tk.FLAT)
        self.chat_box.tag_configure("Center", justify='center')
        for color in self.parent.available_colors:
            self.chat_box.tag_configure(color, foreground=color)

    def update_font(self):
        self.chat_box.configure(font=(self.parent.font_family, self.parent.font_size))

    def pack_widgets(self):
        self.chat_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, self.parent.padx), pady=self.parent.pady)
        self.chat_box.pack(fill=tk.BOTH, expand=True)

    def write_to_chat_box(self, text, tag=None, newline=True):
        self.chat_box.configure(state=tk.NORMAL)
        if newline:
            text = f"{text}\n"
        self.chat_box.insert(tk.END, text, tag)
        self.chat_box.see(tk.END)
        self.chat_box.configure(state=tk.DISABLED)

    def get_chat_contents(self):
        return self.chat_box.get(0.0, tk.END)

    def clear_chat_box(self, *args):
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.delete(0.0, tk.END)
        self.chat_box.configure(state=tk.DISABLED)