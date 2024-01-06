import errno
import socket
from time import sleep

from receiver.repository.ReceiverRepository import ReceiverRepository
from response_generator.service.ResponseGeneratorServiceImpl import ResponseGeneratorServiceImpl


class ReceiverRepositoryImpl(ReceiverRepository):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        print("ReceiverRepositoryImpl 생성자 호출")

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def receiveCommand(self, clientSocketObject, lock, receiveQueue, finishQueue):
        clientSocket = clientSocketObject.getSocket()
        print(f"receiver: is it exist -> {clientSocket}")
        responseGeneratorService = ResponseGeneratorServiceImpl.getInstance()

        while True:
            try:
                data = clientSocket.recv(2048)

                if not data:
                    clientSocketObject.closeSocket()
                    break

                decodedData = data.decode()
                print(f'수신된 정보: {decodedData}')
                evalData = eval(decodedData)

                receivedProtocolNumber = int(evalData["protocol"])
                print(f'Received Protocol number: {receivedProtocolNumber}')
                receivedData = evalData["data"]
                print(f'Received Data: {receivedData}')

                responseGenerator = responseGeneratorService.findResponseGenerator(receivedProtocolNumber)
                print(f'Response Generator: {responseGenerator}')
                responseObject = responseGenerator(receivedData)
                print(f'Response Object: {responseObject}')
                print(f'Response Object type: {type(responseObject)}')

                receiveQueue.put(responseObject)

                className = responseObject.__class__.__name__

                if className == "ProgramExitResponse":
                    break

            except socket.error as exception:
                if exception.errno == errno.EWOULDBLOCK:
                    pass

            finally:
                sleep(0.5)

        print('Receiver Off')
        finishQueue.put(True)
