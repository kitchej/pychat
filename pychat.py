"""
Pychat Client
Written by Joshua Kitchen - 2023
"""
import sys

from client.gui.main_win import MainWin


def main():
    if len(sys.argv) == 1:
        win = MainWin()
    elif len(sys.argv) == 4:
        try:
            port = int(sys.argv[2])
            if port < 1024 or port > 65535:
                print("Port must be between 1024 and 65535")
                return -1
        except ValueError:
            print("Port must be an integer")
            return -2
        win = MainWin((sys.argv[1], port, sys.argv[3]))
    else:
        print("USAGE:\npychat.py\npychat.py <host ip> <host port> <username>")
        return -3

    win.mainloop()


if __name__ == '__main__':
    main()
