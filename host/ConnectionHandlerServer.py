import socket
import json
from helpers.SocketHandler import SocketHandler
from serializers.JsonSerializer import JsonSerializer

class ConnectionHandlerServer:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__socket = None
        self.__serializer = JsonSerializer()
        self.__connection = None

    #Creates socket connection
    def start(self):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.settimeout(None)
            self.__socket.bind((self.__host, self.__port))
            self.__socket.listen(30)
            self.__connection, addr = self.__socket.accept()
        except:
            return False, 'No address'
        return True, addr

    def get_connection(self):
        return self.__connection

    #Closes socket connection
    def close(self):
        if self.__socket is not None:
            try:
                self.__socket.close()
                self.__socket = None
            except:
                return False
            return True
        return False

    def send(self, data):
        if self.__socket is None:
            return False, "No socket specified"
        data_serialized = self.__serializer.serialize(data)
        data_bytes = bytes(data_serialized, 'utf8')
        payload_length = len(data_bytes)
        header = SocketHandler.encodeBytes(payload_length)
        try:
            SocketHandler.write_bytes(self.__socket, header)
            SocketHandler.write_bytes(self.__socket, data_bytes)
        except:
            return False
        return True

    def receive(self):
        try:
            print("recv")
            count = SocketHandler.read_len(self.__connection)
            print(count)
            bytes = SocketHandler.read_bytes(self.__connection, count)
            print(bytes)
            payload_str = str(bytes, 'utf8')
            return self.__serializer.deserialize(payload_str)
        except BrokenPipeError:
            raise BrokenPipeError('conn lost')
