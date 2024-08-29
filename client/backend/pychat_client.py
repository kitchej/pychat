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

from TCPLib.auto_tcp_client import AutoTCPClient
import backend.log_util as log_util
import backend.exceptions as excpt
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_util.add_file_handler(logger, ".client_log", logging.DEBUG, "pychat-client-file-handler")
log_util.add_stream_handler(logger, logging.DEBUG, "pychat-client-stream-handler")


class PychatClient(AutoTCPClient):
    def __init__(self, window, host, port, timeout, user_id):
        AutoTCPClient.__init__(self, host, port, user_id, timeout=timeout)
        self.window = window

    def init_connection(self):
        result = self.start()
        if isinstance(result, Exception):
            return result
        elif not result:
            return Exception()
        self.send(bytes(self.id(), "utf-8"))
        server_response = self.pop_msg(block=True)
        server_response = bytearray.decode(server_response.data, "utf-8")
        logger.debug(f"Server Response={server_response}")
        if server_response == "USERNAME TAKEN":
            self.stop()
            return excpt.UserIDTaken()
        elif server_response == "USERNAME TOO LONG":
            self.stop()
            return excpt.UserIdTooLong()
        elif server_response == "SERVER IS FULL":
            self.stop()
            return excpt.ServerFull()
        elif server_response[0:13] == "INFO\nMEMBERS:":
            self.window.create_member_list(server_response[14:-1])
            return True
        else:
            self.stop()
            return Exception()


if __name__ == '__main__':
    import time
    client = PychatClient(None, "127.0.0.1", 5000, None, "user1", logging.DEBUG, ".client_log")
    client.init_connection()
    time.sleep(0.1)
    client.stop(warn=True)

