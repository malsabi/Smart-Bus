from commands.app_commands import AppCommands
from husky_lens.husky_driver import HuskyDriver
from services.client_socket_service import ClientSocketService


def on_client_connect(end_point):
    print("Client [{}] Connected Successfully".format(end_point))


def on_client_send(end_point, command, content):
    print("Client [{}] Sent Message [{}:{}]".format(end_point, command, content))


def on_client_receive(end_point, command, content):
    print("Client [{}] Received Message [{}:{}]".format(end_point, command, content))
    if command == AppCommands.OPEN_HUSKY_LENS_COMMAND:
        huskyDriver.open()
        if huskyDriver.is_opened:
            clientSocket.send(AppCommands.LOG_MESSAGE_COMMAND, "Successfully opened the husky lens serial port")
        else:
            clientSocket.send(AppCommands.LOG_MESSAGE_COMMAND, "Failed to open husky lens serial port")
    elif command == AppCommands.CLOSE_HUSKY_LENS_COMMAND:
        huskyDriver.close()
        clientSocket.send(AppCommands.LOG_MESSAGE_COMMAND, "Successfully closed the husky lens serial port")
    elif command == AppCommands.START_WORKER_COMMAND:
        huskyDriver.start_worker()
        if huskyDriver.is_worker_running:
            clientSocket.send(AppCommands.LOG_MESSAGE_COMMAND, "Successfully started husky lens worker")
        else:
            clientSocket.send(AppCommands.LOG_MESSAGE_COMMAND, "Failed to start husky lens worker")
    elif command == AppCommands.STOP_WORKER_COMMAND:
        huskyDriver.stop_worker()
        clientSocket.send(AppCommands.LOG_MESSAGE_COMMAND, "Successfully stopped husky lens worker")
    else:
        clientSocket.send(AppCommands.LOG_MESSAGE_COMMAND, "Invalid command name")


def on_client_disconnect(end_point):
    huskyDriver.close()
    huskyDriver.stop_worker()
    print("Client [{}] Disconnected Successfully".format(end_point))


def on_client_exception(ex):
    print("Exception in Client: {}".format(ex))


def on_detected_image(image_info):
    print(image_info)
    clientSocket.send(AppCommands.DETECTED_IMAGE_COMMAND, image_info)


if __name__ == '__main__':
    huskyDriver = HuskyDriver()
    huskyDriver.event.add_handler(HuskyDriver.ON_DETECTED_IMAGE_EVENT, on_detected_image)
    clientSocket = ClientSocketService()
    clientSocket.event.add_handler(ClientSocketService.ON_CLIENT_CONNECT_EVENT, on_client_connect)
    clientSocket.event.add_handler(ClientSocketService.ON_CLIENT_SEND_EVENT, on_client_send)
    clientSocket.event.add_handler(ClientSocketService.ON_CLIENT_RECEIVE_EVENT, on_client_receive)
    clientSocket.event.add_handler(ClientSocketService.ON_CLIENT_DISCONNECT_EVENT, on_client_disconnect)
    clientSocket.event.add_handler(ClientSocketService.ON_CLIENT_EXCEPTION_EVENT, on_client_exception)
    clientSocket.connect("127.0.0.1", 1669)
