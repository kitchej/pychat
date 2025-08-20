"""
Input box
Written by Joshua Kitchen - 2024
"""
import tkinter as tk

from PIL import ImageTk, Image
from client.gui.tooltip import CreateToolTip


class InputBox(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.parent = parent
        self.max_char = 150

        self.picture_icon = ImageTk.PhotoImage(image=Image.open("client/icons/picture_streamline.png").resize((48, 48)))
        self.sound_icon = ImageTk.PhotoImage(image=Image.open("client/icons/sound_streamline.png").resize((48, 48)))
        self.send_icon = ImageTk.PhotoImage(image=Image.open("client/icons/send_streamline.png").resize((48, 48)))

        vcmd = (self.register(self._on_key_release), '%P')
        self.user_input = tk.Entry(self, background=self.parent.widget_bg, foreground=self.parent.widget_fg,
                                   font=self.parent.font, insertbackground=self.parent.widget_fg, disabledbackground=self.parent.widget_bg,
                                   relief=tk.FLAT, validate="key", validatecommand=vcmd)
        self.char_count_var = tk.StringVar()
        self.char_count_var.set(f"0/{self.max_char}")
        self.char_limit_label = tk.Label(self, textvariable=self.char_count_var, background=self.parent.widget_bg,
                                         foreground=self.parent.widget_fg, font=self.parent.font)


        self.send_pic_button = tk.Button(self, image=self.picture_icon, command=self.parent.send_image_msg, background=self.parent.widget_bg,
                                         foreground=self.parent.widget_fg, relief=tk.FLAT)
        self.send_mp3_button = tk.Button(self, image=self.sound_icon, command=self.parent.send_sound_msg, background=self.parent.widget_bg,
                                         foreground=self.parent.widget_fg, relief=tk.FLAT)
        self.send_button = tk.Button(self, image=self.send_icon, command=self.parent.send_msg, background=self.parent.widget_bg,
                                     foreground=self.parent.widget_fg, relief=tk.FLAT)
        self.send_picture_context = CreateToolTip(self.send_pic_button, "Send a picture message", self.parent.widget_bg)
        self.send_mp3_context = CreateToolTip(self.send_mp3_button, "Send an MP3 file", self.parent.widget_bg)
        self.send_context = CreateToolTip(self.send_button, "Send message", self.parent.widget_bg)

        self.user_input.bind("<Return>", self.parent.send_msg)

    def _on_key_release(self, text):
        if len(text) == self.max_char + 1:
            return False
        else:
            self.char_count_var.set(f"{len(text)}/{self.max_char}")
            return True

    def update_font(self):
        self.user_input.configure(font=(self.parent.font_family, self.parent.font_size))
        self.char_limit_label.configure(font=(self.parent.font_family, self.parent.font_size))

    def get_input(self):
        text = self.user_input.get()
        self.user_input.delete(0, tk.END)
        return text

    def pack_widgets(self):
        self.send_button.pack(fill=tk.X, side=tk.RIGHT, pady=(0, self.parent.pady), padx=(5, 5))
        self.send_pic_button.pack(fill=tk.X, side=tk.RIGHT, pady=(0, self.parent.pady), padx=(5, 5))
        self.send_mp3_button.pack(fill=tk.X, side=tk.RIGHT, pady=(0, self.parent.pady), padx=(5, 5))
        self.char_limit_label.pack(fill=tk.BOTH, side=tk.RIGHT, pady=(0, self.parent.pady))
        self.user_input.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(self.parent.padx, 0), pady=(0, self.parent.pady))