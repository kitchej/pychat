import tkinter as tk
from tkinter import messagebox
import threading


class ConnectDialog:
    def __init__(self, parent, main_win):
        self.parent = parent
        self.main_win = main_win

        self.host_lab = tk.Label(self.parent, text="Host: ")
        self.host_entry = tk.Entry(self.parent)

        self.port_lab = tk.Label(self.parent, text="Port: ")
        self.port_entry = tk.Entry(self.parent)

        self.user_id_lab = tk.Label(self.parent, text="Username: ")
        self.user_id_entry = tk.Entry(self.parent)

        self.connect_button = tk.Button(self.parent, text="Connect", command=self.get_connection_info)

        self.host_lab.grid(row=0, column=0)
        self.host_entry.grid(row=0, column=1, padx=5)

        self.port_lab.grid(row=1, column=0)
        self.port_entry.grid(row=1, column=1)

        self.user_id_lab.grid(row=2, column=0)
        self.user_id_entry.grid(row=2, column=1, padx=5)

        self.connect_button.grid(row=3, column=1)

    def get_connection_info(self):
        host = self.host_entry.get()
        port = self.port_entry.get()
        user_id = self.user_id_entry.get()

        if host == '':
            messagebox.showerror("Error", "Host cannot be empty")
            return

        if port == '':
            messagebox.showerror("Error", "Port cannot be empty")
            return

        if user_id == '':
            messagebox.showerror("Error", "Username cannot be empty")
            return

        try:
            port = int(port)
            if port < 1024 or port > 65535:
                messagebox.showerror("Port Error", "Port must be between 1024 and 65535")
                return
        except ValueError:
            messagebox.showerror("Port Error", "Port must be an integer")
            return

        self.main_win.clear_chat_box()
        threading.Thread(target=self.main_win.connect, args=[host, port, user_id]).start()
        self.parent.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    c = ConnectDialog(root, None)
    root.mainloop()
