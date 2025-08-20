"""
Custom MP3 player widget for tkinter
Written by Joshua Kitchen - 2024
"""

import tkinter as tk
import os
import math

from just_playback import Playback
from PIL import Image, ImageTk


class MP3Player(tk.Frame):
    def __init__(self, text_font, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.playback_obj = Playback()
        self.icon_size = (50, 38)
        self.timer_font = ('Helvetica', 14)
        self.time_remain = tk.StringVar()
        self.time_remain.set("0:00")
        self.total_time = tk.StringVar()
        self.total_time.set("0:00")
        self.filename = tk.StringVar()
        self.filename.set("")
        self.controls_disabled = True
        self.playhead_update_interval = 500 # in milliseconds

        self.rewind_icon = ImageTk.PhotoImage(image=Image.open("client/icons/rewind_bootstrap.png").resize(self.icon_size))
        self.stop_icon = ImageTk.PhotoImage(image=Image.open("client/icons/stop_bootstrap.png").resize(self.icon_size))
        self.play_icon = ImageTk.PhotoImage(image=Image.open("client/icons/play_bootstrap.png").resize(self.icon_size))
        self.pause_icon = ImageTk.PhotoImage(image=Image.open("client/icons/pause_bootstrap.png").resize(self.icon_size))
        self.fast_forward_icon = ImageTk.PhotoImage(image=Image.open("client/icons/fast_forward_bootstrap.png").resize(self.icon_size))

        self.file_lab = tk.Label(self, textvariable=self.filename, font=text_font)
        self.playhead_frame = tk.Frame(self)
        self.playhead = tk.Scale(self.playhead_frame, orient=tk.HORIZONTAL, sliderlength=15, showvalue=0,
                                 state=tk.DISABLED, takefocus=0)
        self.time_remain_lab = tk.Label(self.playhead_frame, textvariable=self.time_remain, font=text_font)
        self.total_time_lab = tk.Label(self.playhead_frame, textvariable=self.total_time, font=text_font)
        self.controls_frame = tk.Frame(self)
        self.rewind_butt = tk.Button(self.controls_frame, image=self.rewind_icon, command=self.rewind, state=tk.DISABLED)
        self.stop_butt = tk.Button(self.controls_frame, image=self.stop_icon, command=self.stop, state=tk.DISABLED)
        self.play_butt = tk.Button(self.controls_frame, image=self.play_icon, command=self.play, state=tk.DISABLED)
        self.pause_butt = tk.Button(self.controls_frame, image=self.pause_icon, command=self.pause, state=tk.DISABLED)
        self.forward_butt = tk.Button(self.controls_frame, image=self.fast_forward_icon, command=self.fast_forward, state=tk.DISABLED)

        self.file_lab.pack(expand=tk.TRUE)
        self.playhead_frame.pack(fill=tk.BOTH, expand=tk.TRUE, pady=1)
        self.time_remain_lab.pack(side=tk.LEFT)
        self.playhead.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH)
        self.total_time_lab.pack(side=tk.LEFT)
        self.controls_frame.pack(fill=tk.BOTH, expand=tk.TRUE, pady=(1, 0))
        self.rewind_butt.pack(side=tk.LEFT, padx=(0, 1))
        self.stop_butt.pack(side=tk.LEFT, padx=1)
        self.play_butt.pack(side=tk.LEFT, padx=1)
        self.pause_butt.pack(side=tk.LEFT, padx=1)
        self.forward_butt.pack(side=tk.LEFT, padx=(1, 0))

    @staticmethod
    def _parse_time(secs):
        if secs < 60:
            return f"0:{math.trunc(secs):02d}"
        else:
            return f"{math.trunc(secs / 60)}:{math.trunc(secs % 60):02d}"

    def _toggle_controls(self):
        if self.controls_disabled:
            self.rewind_butt.configure(state=tk.NORMAL)
            self.stop_butt.configure(state=tk.NORMAL)
            self.pause_butt.configure(state=tk.NORMAL)
            self.play_butt.configure(state=tk.NORMAL)
            self.forward_butt.configure(state=tk.NORMAL)
            self.playhead.configure(state=tk.NORMAL)
            self.playhead.bind("<ButtonRelease-1>", self._on_slider_release)
            self.playhead.bind("<Button-1>", self._on_slider_press)
            self.controls_disabled = False
        else:
            self.rewind_butt.configure(state=tk.DISABLED)
            self.stop_butt.configure(state=tk.DISABLED)
            self.pause_butt.configure(state=tk.DISABLED)
            self.play_butt.configure(state=tk.DISABLED)
            self.forward_butt.configure(state=tk.DISABLED)
            self.playhead.configure(state=tk.DISABLED, takefocus=0)
            self.playhead.bind("<ButtonRelease-1>", '')
            self.playhead.bind("<Button-1>", '')
            self.controls_disabled = True

    def _advance_playhead(self, *args):
        self.playhead.set(self.playback_obj.curr_pos)
        self.time_remain.set(self._parse_time(self.playback_obj.curr_pos))
        if not self.playback_obj.paused:
            self.master.after(self.playhead_update_interval, self._advance_playhead)

    def _on_slider_press(self, event):
        if event.widget.identify(event.x, event.y) == 'slider':
            self.playback_obj.pause()
        if event.widget.identify(event.x, event.y) == 'trough1' or event.widget.identify(event.x, event.y) == 'trough2':
            return "break"

    def _on_slider_release(self, event):
        if event.widget.identify(event.x, event.y) == 'trough1' or event.widget.identify(event.x, event.y) == 'trough2':
            return "break"
        self.play()
        val = self.playhead.get()
        self.playback_obj.seek(val)

    def load(self, filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Could not load {filepath}")
        self.playback_obj.load_file(filepath)
        self.filename.set(os.path.split(filepath)[-1])
        self.total_time.set(self._parse_time(self.playback_obj.duration))
        self.playhead.configure(from_=0, to=self.playback_obj.duration)
        self._toggle_controls()

    def reset_state(self):
        if self.controls_disabled:
            return
        if self.playback_obj.playing:
            self.playback_obj.stop()
        self.filename.set("")
        self.total_time.set("0:00")
        self.time_remain.set("0:00")
        self.playhead.set(0)
        self._toggle_controls()

    def play(self):
        if self.playback_obj.active:
            self.playback_obj.resume()
        else:
            self.playback_obj.play()
        self.master.after(self.playhead_update_interval, self._advance_playhead)

    def pause(self):
        self.playback_obj.pause()

    def stop(self):
        self.playback_obj.stop()
        self.time_remain.set("0:00")
        self.playhead.set(0)

    def rewind(self):
        if self.playback_obj.playing:
            self.playback_obj.seek(self.playback_obj.curr_pos - 4)

    def fast_forward(self):
        if self.playback_obj.playing:
            self.playback_obj.seek(self.playback_obj.curr_pos + 4)


if __name__ == '__main__':
    from tkinter import filedialog
    main_win = tk.Tk()
    player = MP3Player(('Helvetica', 12), master=main_win)
    butt_frame = tk.Frame(main_win)
    butt = tk.Button(butt_frame, text="Load", command=lambda x=player: x.load(filedialog.askopenfilename(filetypes=[(".mp3", "*.mp3")])))
    butt2 = tk.Button(butt_frame, text="Reset", command=player.reset_state)
    butt_frame.pack()
    butt.pack(side=tk.LEFT)
    butt2.pack(side=tk.LEFT)
    player.pack()
    main_win.mainloop()