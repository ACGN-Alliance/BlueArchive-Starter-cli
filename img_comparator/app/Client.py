import socket
import struct
import time

from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QByteArray, QTimer, QThread
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QTcpSocket, QHostAddress


class HeartBeatThread(QThread):
    connected = QtCore.pyqtSignal()
    disconnected = QtCore.pyqtSignal()
    noConnection = QtCore.pyqtSignal()
    connectionStateChanged = QtCore.pyqtSignal(bool)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.socket = None
        self.STOP = False
        self.state = False

    def run(self):
        while not self.STOP:
            if self.socket is None:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            while not self.STOP:
                try:
                    # Check if the server is reachable before connecting
                    result = self.socket.connect_ex(('127.0.0.1', self.port))
                    if result == 0:
                        break
                    else:
                        time.sleep(1)
                        print('### Heartbeat server not started yet')
                        self.noConnection.emit()
                        continue
                except Exception as e:
                    print(e)
                    self.socket.close()
                    self.socket = None
                    break

            while not self.STOP:
                time.sleep(1)
                try:
                    self.socket.sendall(b'HEARTBEAT REQ'.rjust(32, b'\x00'))
                    rv = self.socket.recv(32)
                    if not (r := rv.replace(b'\x00', b'')) == b'HEARTBEAT ACK':
                        raise Exception("Heartbeat error, received: %s" % r)
                    self.changeState(True)
                    print(
                        f'<<< Heartbeat thread received HEARTBEAT ACK from server {":".join([str(s) for s in self.socket.getpeername()])}')
                except socket.error:
                    self.changeState(False)
                    print(
                        f'### Heartbeat server disconnected from {":".join([str(s) for s in self.socket.getpeername()])}')
                    self.socket.close()
                    self.socket = None
                    break
                except Exception as e:
                    print(e)
                    break

        if self.state:
            self.socket.sendall(b'FIN'.rjust(32, b'\x00'))
            self.socket.close()

    def changeState(self, state: bool):
        if state != self.state:
            self.state = state
            if state:
                self.connected.emit()
            else:
                self.disconnected.emit()
            self.connectionStateChanged.emit(state)


class Client(QObject):
    receivedImage = QtCore.pyqtSignal(str, QPixmap)
    receivedText = QtCore.pyqtSignal(str, str)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.dataSocket = None
        self.lastData = QByteArray()

        self.heartBeatThread = HeartBeatThread(self.port + 1)
        self.heartBeatThread.connected.connect(self.onConnected)
        self.heartBeatThread.start()

    def onConnected(self):
        self.dataSocket = QTcpSocket()
        self.dataSocket.readyRead.connect(self.onReadyRead)
        self.dataSocket.connectToHost(QHostAddress.LocalHost, self.port)
        self.dataSocket.waitForConnected()
        print(f'### connected to data server {self.dataSocket.peerAddress().toString()}')

    def onDisconnected(self):
        QTimer.singleShot(1000, self.onConnected)

    def __onDisconnected(self):
        if self.dataSocket is not None:
            self.dataSocket.close()
            self.dataSocket = None
        print('### disconnected from data server')
        self.lastData.clear()

    def onReadyRead(self):
        packet = self.dataSocket.readAll()
        if packet.size() >= 3 and packet[-3:] == b'END':
            self.lastData.append(packet.data()[:-3])
            print(f'<<< received END, received {self.lastData.size()} bytes')
            self.receiveAny(self.lastData.data())
            self.dataSocket.write(b'OK')
            self.lastData.clear()
        elif packet.size() < 3 and b'END' in self.lastData.data()[-3:] + packet.data():
            self.lastData.append(packet.data()[:-3])
            print(f'<<< received END, received {self.lastData.size()} bytes')
            self.receiveAny(self.lastData.data())
            self.dataSocket.write(b'OK')
            self.lastData.clear()
        else:
            self.lastData.append(packet.data())

    def receiveImage(self, data: bytes):
        name, w, h, mode = struct.unpack('32s2i8s', data[:48])
        name = name.decode('utf-8').replace('\x00', '')
        mode = mode.decode('utf-8').replace('\x00', '')
        image = Image.frombytes(mode, (w, h), data)

        self.receivedImage.emit(name, image.toqpixmap())

    def receiveText(self, data: bytes):
        key = struct.unpack('32s', data[32:64])[0]
        value = data[64:]
        key = key.decode('utf-8').replace('\x00', '')
        value = value.decode('utf-8').replace('\x00', '')

        self.receivedText.emit(key, value)

    def receiveAny(self, data: bytes):
        name = data[:32]
        name = name.decode('utf-8').replace('\x00', '')
        if "Image" in name:
            return self.receiveImage(data)
        elif "text" in name:
            return self.receiveText(data)

    def stop(self):
        self.heartBeatThread.STOP = True
        if not self.heartBeatThread.state:
            self.heartBeatThread.terminate()
        else:
            self.heartBeatThread.wait()
        self.__onDisconnected()

    @property
    def connected(self):
        return self.heartBeatThread.connected

    @property
    def disconnected(self):
        return self.heartBeatThread.disconnected

    @property
    def noConnection(self):
        return self.heartBeatThread.noConnection
