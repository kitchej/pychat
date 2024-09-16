import tkinter as tk
from just_playback import Playback
import os
import math


class MP3Player(tk.Frame):
    def __init__(self, filepath, text_font, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.filepath = filepath
        self.playback_obj = Playback()
        self.playback_obj.load_file(self.filepath)
        self.play_head_prog = tk.IntVar()
        self.play_head_prog.set(0)
        self.time_remain = tk.StringVar()
        self.total_time = tk.StringVar()
        self.time_remain.set("0:00")
        self.total_time.set(self._parse_time(self.playback_obj.duration))
        self.filename = tk.StringVar()
        self.filename.set(os.path.split(self.filepath)[-1])
        self.font = ('Helvetica', 14)

        self.file_lab = tk.Label(self, textvariable=self.filename, font=text_font)

        self.play_head_frame = tk.Frame(self)
        self.play_head = tk.Scale(self.play_head_frame, orient=tk.HORIZONTAL, from_=0, to=self.playback_obj.duration,
                                  variable=self.play_head_prog, sliderlength=15, showvalue=0)
        self.time_remain_lab = tk.Label(self.play_head_frame, textvariable=self.time_remain)
        self.total_time_lab = tk.Label(self.play_head_frame, textvariable=self.total_time)

        self.controls_frame = tk.Frame(self)
        self.rewind_butt = tk.Button(self.controls_frame, text="◄◄", font=self.font, width=5, command=self.rewind)
        self.stop_butt = tk.Button(self.controls_frame, text="■", font=self.font, width=5, command=self.stop)
        self.pause_butt = tk.Button(self.controls_frame, text="▌▌", font=self.font, width=5, command=self.pause)
        self.play_butt = tk.Button(self.controls_frame, text="►", font=self.font, width=5, command=self.play)
        self.forward_butt = tk.Button(self.controls_frame, text="►►", font=self.font, width=5, command=self.fast_forward)

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

        self.play_head.bind("<ButtonRelease-1>", self.scrub)
        self.play_head.bind("<Button-1>", self._on_slider_press)

    @staticmethod
    def _parse_time(secs):
        if secs < 60:
            minutes = 0
            seconds = math.trunc(secs)
        else:
            minutes = math.trunc(secs/60)
            seconds = math.trunc(secs % 60)
        return f"{minutes}:{seconds:02d}"

    def _advance_playhead(self, *args):
        self.play_head.set(self.playback_obj.curr_pos)
        self.time_remain.set(self._parse_time(self.playback_obj.curr_pos))
        if not self.playback_obj.paused:
            self.master.after(100, self._advance_playhead)

    def _on_slider_press(self, event):
        if event.widget.identify(event.x, event.y) == 'slider':
            self.playback_obj.pause()

    def scrub(self, event):
        if event.widget.identify(event.x, event.y) == 'slider':
            val = self.play_head.get()
            self.playback_obj.seek(val)
            self.play()

    def play(self, *args):
        if self.playback_obj.active:
            self.playback_obj.resume()
        else:
            self.playback_obj.play()
        self.master.after(1000, self._advance_playhead)

    def pause(self, *args):
        self.playback_obj.pause()

    def stop(self, *args):
        self.playback_obj.stop()

    def rewind(self, *args):
        if self.playback_obj.playing:
            self.playback_obj.seek(self.playback_obj.curr_pos - 4)

    def fast_forward(self, *args):
        if self.playback_obj.playing:
            self.playback_obj.seek(self.playback_obj.curr_pos + 4)
