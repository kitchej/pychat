"""
Client for Pychat
Written by Joshua Kitchen - 2023

NOTES:
    - Only ipv4 is supported (for now)
    - NULL is used to mark the end of a message.
    - Normal messages sent between clients have this format: [sender]\n[message]\0
        - Since a newline is used as a delimiter, it is important to ensure that any newlines are stripped from messages
        before transmission.
    - Informational messages always have INFO as the sender. These messages are processed differently by the client.
        - Informational messages have this format: INFO\n[header]:[message]\0
"""
import sys

from gui.main_win import MainWin


def main():
    if len(sys.argv) == 1:
        win = MainWin()
    elif len(sys.argv) == 4:
        try:
            port = int(sys.argv[2])
            if port < 1024 or port > 65535:
                print("Port must be between 1024 and 65535")
                return - 1
        except ValueError:
            print("Port must be an integer")
            return -2
        win = MainWin((sys.argv[1], sys.argv[2], sys.argv[3]))
    else:
        print("USAGE:\npychat.py\npycaht.py <host ip> <host port> <username>")
        return -3

    win.mainloop()


if __name__ == '__main__':
    main()
