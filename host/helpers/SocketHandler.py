import socket
import sys

class SocketHandler:
    """
    Class for handling byte operations when sending and receiving the data
    """
    @staticmethod
    def encodeBytes(value):
        # Turns integer into string of 4 bytes
        return value.to_bytes(4, byteorder='big')

    @staticmethod
    def read_bytes(socket, count):
        # Reads given amount of bytes from the socket
        buffer = b''
        while count > 0:
            received = socket.recv(count)
            if not received or len(received) == 0:
                pass
            buffer += received
            count -= len(received)
        return buffer

    @staticmethod
    def write_bytes(socket, buffer):
        # Writes given buffer to the socket
        count = len(buffer)
        total_written = 0
        while total_written < count:
            written = socket.send(buffer[total_written:])
            if written == 0:
                raise BrokenPipeError("socket disconnected")
            total_written += written

    @staticmethod
    def read_len(socket):
        # Reads integer from the header in bytes
        value = 0
        count_bytes = 4
        while count_bytes > 0:
            current_byte = SocketHandler.read_bytes(socket, 1)[0]
            value += ((16**(count_bytes-1))*current_byte)
            count_bytes -= 1
        return value
