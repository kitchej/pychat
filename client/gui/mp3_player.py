"""
MP3 Player
Written by Joshua Kitchen - 2024
"""

import tkinter as tk
from just_playback import Playback
import os
import math


class MP3Player(tk.Frame):
    def __init__(self, text_font, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.playback_obj = Playback()
        self.time_remain = tk.StringVar()
        self.time_remain.set("0:00")
        self.total_time = tk.StringVar()
        self.total_time.set("0:00")
        self.filename = tk.StringVar()
        self.filename.set("")
        self.font = ('Helvetica', 14)
        self.controls_disabled = True
        self.play_head_poll = 500

        self.file_lab = tk.Label(self, textvariable=self.filename, font=text_font)
        self.play_head_frame = tk.Frame(self)
        self.play_head = tk.Scale(self.play_head_frame, orient=tk.HORIZONTAL, sliderlength=15, showvalue=0,
                                  state=tk.DISABLED, takefocus=0)
        self.time_remain_lab = tk.Label(self.play_head_frame, textvariable=self.time_remain, font=text_font)
        self.total_time_lab = tk.Label(self.play_head_frame, textvariable=self.total_time, font=text_font)
        self.controls_frame = tk.Frame(self)
        self.rewind_butt = tk.Button(self.controls_frame, text="◄◄", font=self.font, width=5, command=self.rewind, state=tk.DISABLED)
        self.stop_butt = tk.Button(self.controls_frame, text="■", font=self.font, width=5, command=self.stop, state=tk.DISABLED)
        self.pause_butt = tk.Button(self.controls_frame, text="▌▌", font=self.font, width=5, command=self.pause, state=tk.DISABLED)
        self.play_butt = tk.Button(self.controls_frame, text="►", font=self.font, width=5, command=self.play, state=tk.DISABLED)
        self.forward_butt = tk.Button(self.controls_frame, text="►►", font=self.font, width=5, command=self.fast_forward, state=tk.DISABLED)
        self.file_lab.pack(expand=tk.TRUE)
        self.play_head_frame.pack(fill=tk.BOTH, expand=tk.TRUE, pady=1)
        self.time_remain_lab.pack(side=tk.LEFT)
        self.play_head.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.BOTH)
        self.total_time_lab.pack(side=tk.LEFT)
        self.controls_frame.pack(fill=tk.BOTH, expand=tk.TRUE, pady=(1, 0))
        self.rewind_butt.pack(side=tk.LEFT, padx=(0, 1))
        self.stop_butt.pack(side=tk.LEFT, padx=1)
        self.pause_butt.pack(side=tk.LEFT, padx=1)
        self.play_butt.pack(side=tk.LEFT, padx=1)
        self.forward_butt.pack(side=tk.LEFT, padx=(1, 0))
        self.rewind_butt.configure(state=tk.DISABLED)
        self.stop_butt.configure(state=tk.DISABLED)
        self.pause_butt.configure(state=tk.DISABLED)
        self.play_butt.configure(state=tk.DISABLED)
        self.forward_butt.configure(state=tk.DISABLED)

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
            self.play_head.configure(state=tk.NORMAL)
            self.play_head.bind("<ButtonRelease-1>", self._on_slider_release)
            self.play_head.bind("<Button-1>", self._on_slider_press)
            self.controls_disabled = False
        else:
            self.rewind_butt.configure(state=tk.DISABLED)
            self.stop_butt.configure(state=tk.DISABLED)
            self.pause_butt.configure(state=tk.DISABLED)
            self.play_butt.configure(state=tk.DISABLED)
            self.forward_butt.configure(state=tk.DISABLED)
            self.play_head.configure(state=tk.DISABLED, takefocus=0)
            self.play_head.bind("<ButtonRelease-1>", '')
            self.play_head.bind("<Button-1>", '')
            self.controls_disabled = True

    def _advance_playhead(self, *args):
        self.play_head.set(self.playback_obj.curr_pos)
        self.time_remain.set(self._parse_time(self.playback_obj.curr_pos))
        if not self.playback_obj.paused:
            self.master.after(self.play_head_poll, self._advance_playhead)

    def _on_slider_press(self, event):
        if event.widget.identify(event.x, event.y) == 'slider':
            self.playback_obj.pause()
        if event.widget.identify(event.x, event.y) == 'trough1' or event.widget.identify(event.x, event.y) == 'trough2':
            return "break"

    def _on_slider_release(self, event):
        if event.widget.identify(event.x, event.y) == 'trough1':
            return "break"
        elif event.widget.identify(event.x, event.y) == 'trough2':
            return "break"
        self.play()
        val = self.play_head.get()
        self.playback_obj.seek(val)

    def load(self, filepath):
        if not os.path.exists(filepath):
            return
        self.playback_obj.load_file(filepath)
        self.filename.set(os.path.split(filepath)[-1])
        self.total_time.set(self._parse_time(self.playback_obj.duration))
        self.play_head.configure(from_=0, to=self.playback_obj.duration)
        self._toggle_controls()

    def reset_state(self):
        if self.controls_disabled:
            return
        if self.playback_obj.playing:
            self.playback_obj.stop()
        self.filename.set("")
        self.total_time.set("0:00")
        self.time_remain.set("0:00")
        self.play_head.set(0)
        self._toggle_controls()

    def play(self):
        if self.playback_obj.active:
            self.playback_obj.resume()
        else:
            self.playback_obj.play()
        self.master.after(self.play_head_poll, self._advance_playhead)

    def pause(self):
        self.playback_obj.pause()

    def stop(self):
        self.playback_obj.stop()
        self.time_remain.set("0:00")
        self.play_head.set(0)

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