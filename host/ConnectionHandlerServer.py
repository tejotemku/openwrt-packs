import socket, json, threading
from helpers.SocketHandler import SocketHandler
from serializers.JsonSerializer import JsonSerializer


class ConnectionHandlerServer:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__socket = None
        self.__serializer = JsonSerializer()
        self.__connection = None
        self.__mutex_send = threading.Lock()
        self.__mutex_recv = threading.Lock()

    #Creates socket connection
    def start(self):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.settimeout(None)
            self.__socket.bind((self.__host, self.__port))
            while True:
                print("Listening for client (30s)...")
                self.__socket.listen(30)
                self.__connection, addr = self.__socket.accept()
                if addr is not None:
                    break
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
        if self.__connection is None:
            return False, "No socket specified"
        data_serialized = self.__serializer.serialize(data)
        data_bytes = bytes(data_serialized, 'utf8')
        payload_length = len(data_bytes)
        header = SocketHandler.encodeBytes(payload_length)
        try:
            with self.__mutex_send:
                SocketHandler.write_bytes(self.__connection, header)
                SocketHandler.write_bytes(self.__connection, data_bytes)
        except:
            return False
        return True

    def receive(self):
        try:
            with self.__mutex_recv:
                count = SocketHandler.read_len(self.__connection)
                if count == 1:
                    return {}
                bytes = SocketHandler.read_bytes(self.__connection, count)
            payload_str = str(bytes, 'utf8')
            return self.__serializer.deserialize(payload_str)
        except BrokenPipeError:
            raise BrokenPipeError('conn lost')

    def ping(self):
        if self.__connection is None:
            return False
        payload_length = 1
        payload = SocketHandler.encodeBytes(payload_length)
        try:
            with self.__mutex_send:
                SocketHandler.write_bytes(self.__connection, payload)
        except:
            return False
        return True
