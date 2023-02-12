import time
import socket
from threading import Thread
from modules.event import Event
from commands.socket_commands import SocketCommands


class ClientSocketService:
    ON_CLIENT_CONNECT_EVENT = "OnClientConnect"
    ON_CLIENT_SEND_EVENT = "OnClientSend"
    ON_CLIENT_RECEIVE_EVENT = "OnClientReceive"
    ON_CLIENT_DISCONNECT_EVENT = "OnClientDisconnect"
    ON_CLIENT_EXCEPTION_EVENT = "OnClientException"

    def __init__(self):
        self.__header_size = 4
        self.__maximum_message_size = 1024 * 16
        self.__handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False
        self.is_authenticated = False
        self.enable_reconnect = True
        self.end_point = str()
        self.event = Event()

    def connect(self, host, port):
        self.end_point = "{}:{}".format(host, port)
        Thread(target=self.__attempt_to_connect, args=(host, port)).start()

    def __attempt_to_connect(self, host, port):
        while self.enable_reconnect:
            if not self.is_connected:
                try:
                    self.__handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.__handler.connect((host, port))
                    self.is_connected = True
                    self.__start_receiver()
                    self.event.trigger(self.ON_CLIENT_CONNECT_EVENT, self.end_point)
                    self.send(SocketCommands.HAND_SHAKE_COMMAND, "SmartBus")
                except Exception as e:
                    self.event.trigger(self.ON_CLIENT_EXCEPTION_EVENT, e)
            time.sleep(1)

    def __start_receiver(self):
        Thread(target=self.__receiver).start()

    def __receiver(self):
        try:
            if self.is_connected:
                header_bytes = self.__handler.recv(self.__header_size)
                message_size = int.from_bytes(header_bytes, byteorder="little")
                if message_size >= self.__maximum_message_size:
                    self.disconnect()
                else:
                    message = str(self.__handler.recv(message_size), 'utf-8')

                    if "|" not in message:
                        raise Exception("Invalid Message Format")

                    message_parts = message.split("|")
                    command = message_parts[0]
                    content = message_parts[1]

                    if not self.is_authenticated:
                        if not command == SocketCommands.ACKNOWLEDGE_COMMAND:
                            raise Exception("client authentication failed. Invalid authentication command")
                        self.is_authenticated = True
                    else:
                        self.event.trigger(self.ON_CLIENT_RECEIVE_EVENT, self.end_point, command, content)
                    self.__receiver()
        except Exception as e:
            self.event.trigger(self.ON_CLIENT_EXCEPTION_EVENT, e)
            self.disconnect()

    def send(self, command, content):
        try:
            if self.is_connected:
                message = "{}|{}".format(command, content)
                message_bytes = bytes(message, 'utf-8')
                header = len(message_bytes).to_bytes(4, byteorder="little")
                packet = header + message_bytes
                self.__handler.send(packet)
                self.event.trigger(self.ON_CLIENT_SEND_EVENT, self.end_point, command, content)
        except Exception as e:
            self.event.trigger(self.ON_CLIENT_EXCEPTION_EVENT, e)
            self.disconnect()

    def disconnect(self):
        if self.is_connected:
            self.is_connected = False
            self.is_authenticated = False
            self.__handler.shutdown(2)
            self.__handler.close()
            self.event.trigger(self.ON_CLIENT_DISCONNECT_EVENT, self.end_point)
