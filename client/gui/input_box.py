"""
Input box
Written by Joshua Kitchen - 2024
"""
import tkinter as tk

class InputBox(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.parent = parent
        vcmd = (self.register(self._on_key_release), '%P')
        self.user_input = tk.Entry(self, background=self.parent.widget_bg, foreground=self.parent.widget_fg,
                                   font=self.parent.font, insertbackground=self.parent.widget_fg, disabledbackground=self.parent.widget_bg,
                                   relief=tk.FLAT, validate="key", validatecommand=vcmd)
        self.char_count_var = tk.StringVar()
        self.char_count_var.set("0/150")
        self.char_limit_label = tk.Label(self, textvariable=self.char_count_var, background=self.parent.widget_bg,
                                         foreground=self.parent.widget_fg, font=self.parent.font)
        self.send_pic_button = tk.Button(self, text="Pic", command=self.parent.send_pic, background=self.parent.widget_bg,
                                     foreground=self.parent.widget_fg, relief=tk.FLAT, height=2, width=10)
        self.send_button = tk.Button(self, text="Send", command=self.parent.send_msg, background=self.parent.widget_bg,
                                     foreground=self.parent.widget_fg, relief=tk.FLAT, height=2, width=10)
        self.user_input.bind("<Return>", self.parent.send_msg)
        self.send_button.bind("<Enter>", self._on_btn_enter)
        self.send_button.bind("<Leave>", self._on_btn_leave)

    def _on_key_release(self, text):
        if len(text) == 151:
            return False
        else:
            self.char_count_var.set(f"{len(text)}/150")
            return True

    def _on_btn_enter(self, *args):
        self.send_button['background'] = "#bfbfbf"

    def _on_btn_leave(self, *args):
        self.send_button['background'] = self.parent.widget_bg

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
        self.char_limit_label.pack(fill=tk.BOTH, side=tk.RIGHT, pady=(0, self.parent.pady))
        self.user_input.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(self.parent.padx, 0), pady=(0, self.parent.pady))