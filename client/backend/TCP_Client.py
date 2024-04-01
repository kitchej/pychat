"""
TCP client
Written by Joshua Kitchen - 2023

All messages are sent in this format:
    "[header]\n[message]\0"

The INFO header is used when the server and the client need to pass along information. Messages with this header include
an additional header within the message indicating what kind of information was sent. The header and the message are
delimited by a colon. Possible INFO messages are:
- JOINED:<user id>
- LEFT:<user id>
- MEMBERS:<list of connected users>
- LEAVING:<no message body>
- KICKED:<no message body>
- SERVERMSG:<message>

If the header is neither of the above options, then the message is treated as a chat message and broadcast to all
connected clients
"""
import logging
import threading

from TCPLib.active_client import ActiveTcpClient
import log_util
logger = logging.getLogger()


class TCPClient:
    def __init__(self, window, host, port, timeout, user_id, log_level, log_path):
        self.client = ActiveTcpClient(host, port, user_id, timeout=timeout)
        self.window = window
        logger.setLevel(log_level)
        log_util.add_file_handler(logger, log_path, log_level, "pychat-client-file-handler")
        log_util.add_stream_handler(logger, log_level, "pychat-client-stream-handler")

    def _receive_loop(self):
        pass

    def init_connection(self):
        self.client.start()
        self.client.send(bytes(self.client.id(), "utf-8"))
        server_response = self.client.pop_msg(block=True)
        if server_response.data == b"USERNAME TAKEN":
            self.client.stop()
            return False
        elif server_response.data == b"USERNAME AVAILABLE":
            # Client is receiving parts of other messages, causing this elif statement to fail
            threading.Thread(target=self._receive_loop).start()
            return True
        else:
            self.client.stop()
            return False


if __name__ == '__main__':
    client = TCPClient(None, "127.0.0.1", 5000, None, "user1", logging.DEBUG, ".client_log")
    client.init_connection()

