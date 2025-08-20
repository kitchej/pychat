"""
About Dialog Window
Written by Joshua Kitchen - 2025
"""

import tkinter as tk
from tkinter import font as tk_font
from tkinter import ttk

class AboutDialog:
    def __init__(self, parent, main_win):
        self.parent = parent
        self.main_win = main_win
        self.about_text = """Pychat Client 
        
Copyright (c) 2025 Joshua Kitchen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Credits:

-- Pillow | https://github.com/python-pillow/Pillow --

The Python Imaging Library (PIL) is

    Copyright © 1997-2011 by Secret Labs AB
    Copyright © 1995-2011 by Fredrik Lundh and contributors

Pillow is the friendly PIL fork. It is

    Copyright © 2010 by Jeffrey A. Clark and contributors

Like PIL, Pillow is licensed under the open source MIT-CMU License:

By obtaining, using, and/or copying this software and/or its associated
documentation, you agree that you have read, understood, and will comply
with the following terms and conditions:

Permission to use, copy, modify and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appears in all copies, and that
both that copyright notice and this permission notice appear in supporting
documentation, and that the name of Secret Labs AB or the author not be
used in advertising or publicity pertaining to distribution of the software
without specific, written prior permission.

SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.
IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL,
INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.


-- just_playback | Github: https://github.com/cheofusi/just_playback ---

MIT License
Copyright (c) 2018 YOUR NAME # This is exactly how it reads on the github page
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


-- TCPLib | Github: https://github.com/kitchej/TCPLib --

Copyright (c) 2025 Joshua Kitchen

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the " Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice (including the next paragraph) shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE


-- Bootstrap Icons --

The MIT License (MIT)

Copyright (c) 2019-2024 The Bootstrap Authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


-- Streamline Icons --

Free icons provided by Streamline
https://streamlinehq.com


--- 'Classic' notification sound ---

"The Notification Email" provided by universfield-28281460
https://pixabay.com/sound-effects/the-notification-email-143029/


--- 'Outer Space' notification sound ---

"Notification-140376" provided by universfield-28281460
https://pixabay.com/sound-effects/notification-140376/


--- 'Alert' notification sound ---

"Notification-126507" provided by universfield-28281460
https://pixabay.com/sound-effects/notification-126507/


--- 'Deep Sea' notification sound ---

"message-13716" provided by supremetylewiss-25143503
https://pixabay.com/sound-effects/message-13716/
"""



        self.info_area = tk.Text(self.parent, wrap=tk.WORD, background=self.main_win.widget_bg,
                                foreground=self.main_win.widget_fg, font=('Arial', 12),
                                insertbackground=self.main_win.widget_bg, cursor="arrow")
        self.info_area.insert(tk.END, self.about_text)
        self.info_area.tag_configure("header", justify=tk.CENTER, font=tk_font.Font(family='Arial',
        size=16, weight='bold'))
        self.info_area.tag_configure("sub-header1", font=tk_font.Font(family='Arial', size=14, weight='bold'))
        self.info_area.tag_configure("sub-header2", font=tk_font.Font(family='Arial', size=12, weight='bold'))
        self.info_scroll = ttk.Scrollbar(self.parent, command=self.info_area.yview)
        self.info_area.configure(yscrollcommand=self.info_scroll.set, relief=tk.FLAT, state=tk.DISABLED)
        self.info_area.tag_add("header", "0.0", "0.0+13c")
        self.info_area.tag_add("sub-header1", "23.0", "23.end")
        self.info_area.tag_add("sub-header2", "25.0", "25.end") # pillow
        self.info_area.tag_add("sub-header2", "58.0", "59.end") # just_playback
        self.info_area.tag_add("sub-header2", "62.28", "62.end")  # just_playback no name notice
        self.info_area.tag_add("sub-header2", "80.0", "80.end") # TCPLib
        self.info_area.tag_add("sub-header2", "91.0", "91.end") # Bootstrap
        self.info_area.tag_add("sub-header2", "116.0", "116.end") # Streamline
        self.info_area.tag_add("sub-header2", "122.0", "122.end")  # Classic notification
        self.info_area.tag_add("sub-header2", "128.0", "128.end")  # Outer Space notification
        self.info_area.tag_add("sub-header2", "134.0", "134.end")  # Alert notification
        self.info_area.tag_add("sub-header2", "140.0", "140.end")  # Deep Sea notification

        self.info_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.info_scroll.pack(side=tk.RIGHT, fill=tk.Y, expand=True)


if __name__ == '__main__':
    class DummyWin:
        def __init__(self):
            self.widget_bg = '#ffffff'
            self.widget_fg = '#000000'
    root = tk.Tk()
    dum_win = DummyWin()
    _ = AboutDialog(root, dum_win)

    root.mainloop()