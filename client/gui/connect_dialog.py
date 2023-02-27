import tkinter as tk
from tkinter import messagebox
import threading


class ConnectDialog:
    def __init__(self, parent, main_win):
        self.parent = parent
        self.main_win = main_win

        self.parent.configure(background=self.main_win.app_bg)

        self.connect_info_frame = tk.Frame(self.parent, background=self.main_win.widget_bg)

        self.host_lab = tk.Label(self.connect_info_frame, text="Host: ", background=self.main_win.widget_bg)
        self.host_entry = tk.Entry(self.connect_info_frame)

        self.port_lab = tk.Label(self.connect_info_frame, text="Port: ", background=self.main_win.widget_bg)
        self.port_entry = tk.Entry(self.connect_info_frame)

        self.user_id_lab = tk.Label(self.connect_info_frame, text="Username: ", background=self.main_win.widget_bg)
        self.user_id_entry = tk.Entry(self.connect_info_frame)

        self.connect_button = tk.Button(self.parent, text="Connect", command=self.get_connection_info,
                                        background="#f2f2f2", foreground=self.main_win.widget_fg,
                                        relief=tk.FLAT, highlightcolor="#bfbfbf",
                                        height=2, width=10)

        self.host_lab.grid(row=0, column=0, padx=(10, 0), pady=(10, 0))
        self.host_entry.grid(row=0, column=1, padx=(0, 10), pady=(10, 0))

        self.port_lab.grid(row=1, column=0, padx=(10, 0))
        self.port_entry.grid(row=1, column=1, padx=(0, 10))

        self.user_id_lab.grid(row=2, column=0, padx=(10, 0), pady=(0, 10))
        self.user_id_entry.grid(row=2, column=1, padx=(0, 10), pady=(0, 10))

        self.connect_info_frame.pack(padx=10, pady=10)

        self.connect_button.pack(padx=10, pady=(0, 10))

        self.parent.bind("<Return>", self.get_connection_info)
        self.connect_button.bind("<Enter>", self.on_enter)
        self.connect_button.bind("<Leave>", self.on_leave)

    def on_enter(self, *args):
        self.connect_button['background'] = "#bfbfbf"

    def on_leave(self, *args):
        self.connect_button['background'] = "#f2f2f2"

    def get_connection_info(self, *args):
        host = self.host_entry.get()
        port = self.port_entry.get()
        user_id = self.user_id_entry.get()

        if host == '':
            messagebox.showerror("Error", "Host cannot be empty", parent=self.parent)
            return

        if port == '':
            messagebox.showerror("Error", "Port cannot be empty", parent=self.parent)
            return

        try:
            port = int(port)
            if port < 1024 or port > 65535:
                messagebox.showerror("Port Error", "Port must be between 1024 and 65535", parent=self.parent)
                return
        except ValueError:
            messagebox.showerror("Port Error", "Port must be an integer", parent=self.parent)
            return

        if user_id == '':
            messagebox.showerror("Error", "Username cannot be empty", parent=self.parent)
            return

        self.main_win.clear_chat_box()
        threading.Thread(target=self.main_win.connect, args=[host, port, user_id]).start()
        self.parent.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    c = ConnectDialog(root, None)
    root.mainloop()
