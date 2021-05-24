import socket, json, threading
from helpers.SocketHandler import SocketHandler
from serializers.JsonSerializer import JsonSerializer

class ConnectionHandlerClient:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__socket = None
        self.__serializer = JsonSerializer()
        self.__mutex_send = threading.Lock()
        self.__mutex_recv = threading.Lock()

    def connect(self):
        # Creates socket connection
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect((self.__host, self.__port))
        except:
            return False
        return True

    def close(self):
        # Closes socket connection
        if self.__socket is not None:
            try:
                self.__socket.close()
                self.__socket = None
            except:
                return False
            return True
        return False

    def send(self, data):
        # Sends data to the server
        if self.__socket is None:
            return False, "No socket specified"
        data_serialized = self.__serializer.serialize(data)
        data_bytes = bytes(data_serialized, 'utf8')
        payload_length = len(data_bytes)
        header = SocketHandler.encodeBytes(payload_length)
        try:
            with self.__mutex_send:
                SocketHandler.write_bytes(self.__socket, header)
                SocketHandler.write_bytes(self.__socket, data_bytes)
        except:
            return False
        return True

    def ping(self):
        # Sends loose header to check the connection with the server
        if self.__socket is None:
            return False
        payload_length = 1 # to recognize ping easily
        payload = SocketHandler.encodeBytes(payload_length)
        try:
            with self.__mutex_send:
                SocketHandler.write_bytes(self.__socket, payload)
        except:
            return False
        return True
