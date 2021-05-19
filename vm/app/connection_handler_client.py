import socket
import json

#Checks wheather the argument is in a json format
def is_json(json_data):
    try:
        data = json.loads(json_data)
    except ValueError as e:
        return False
    return True

class ConnectionHandlerClient:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__socket = None

    #Creates socket connection
    def connect(self):
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.connect((self.__host, self.__port))
            return self.ping()
        except:
            return False

    #Closes socket connection
    def close(self):
        if self.__socket != None:
            try:
                self.__socket.close()
            except:
                return False
            return True
        return False

    #Returns (bool, str) whether data was sent and additional information
    def send(self, data):
        if self.__socket == None:
            return False, "No socket specified"
        if not is_json(data):
            return False, "Data is not a json"
        try:
            self.__socket.sendall(data.encode('utf-8'))
            recv_conf = self.__socket.recv(1024)
        except:
            return False, ""
        if is_json(recv_conf.decode('utf-8')):
            confirmation = json.loads(recv_conf.decode('utf-8'))
        else:
            return False, "Received non-json from the server"
        if confirmation["received"] != "OK"
            return False, "No confirmation"
        return True, "OK"

    #Returns whether ping was successful
    def ping(self):
        ping_data = {
            "conn_test": "test"
        }
        code, msg = self.send(json.dumps(ping_data))
        if code:
            return True
        else:
            return False
