import queue
import socket
import struct
import threading
import time
from typing import Any

from PIL import Image

from .cmp import compare_images_binary_old


class RestartServerThread(Exception):
    ...


class ServerThread(threading.Thread):
    def __init__(self, server: socket.socket):
        super().__init__()
        self.server = server
        self.queue = queue.Queue()
        self.STOP = False
        self.blockSize = 16384

    def run(self) -> None:
        while not self.STOP:
            try:

                s, addr = self.server.accept()
                # print(f'accepted connection from {addr}')
                time.sleep(1)
                while True:
                    data2send = self.queue.get(block=True)
                    if data2send == b'STOP':
                        break
                    elif data2send == b'RESTART':
                        s.close()
                        raise RestartServerThread()
                    mv = memoryview(data2send)
                    total = len(data2send)
                    sent = 0
                    # send 1024 bytes each time
                    while sent < total:
                        s.send(mv[sent:min(sent + self.blockSize, total)])
                        # print(f'>>> sent {sent} bytes')
                        sent += self.blockSize
                    s.send(b'END')

                    while b'OK' not in (r := s.recv(1024)):
                        # print(f'received {r} but expected OK')
                        ...
                    # print('<<< received OK')
                s.close()

            except RestartServerThread:
                continue
        # print('server thread stopped')

    def put(self, data: bytes):
        self.queue.put(data)


class FinReceived(Exception):
    ...


class HeartBeatThread(threading.Thread):
    def __init__(self, port: int, serverObj):
        super().__init__()
        self.heart_beat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.heart_beat_socket.bind(('127.0.0.1', port))
        self.heart_beat_socket.listen(1)
        self.heart_beat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.STOP = False
        self.state = False
        self.serverObj = serverObj

    def run(self) -> None:
        # print(f'### listening on {self.heart_beat_socket.getsockname()}: ', end='')
        s, addr = self.heart_beat_socket.accept()
        # print(f'accepted heart beat connection from {addr}')
        time.sleep(1)
        while not self.STOP:
            try:
                heart_beat = s.recv(32)
                if (r := heart_beat.replace(b'\x00', b'')) == b'HEARTBEAT REQ':
                    s.send(b'HEARTBEAT ACK'.rjust(32, b'\x00'))
                    self.state = True
                    # print(f'>>> sent HEARTBEAT ACK to client {":".join([str(s) for s in s.getpeername()])}')
                elif r == b'FIN':
                    raise FinReceived("FIN received")
                elif r == b'':
                    raise FinReceived("FIN received")
                else:
                    # print(f'received {r} but expected HEARTBEAT REQ')
                    ...
            except ConnectionResetError:
                self.state = False
                self.request_restart()
                if self.STOP:
                    break
                s.close()
                # print(f'### heart beat client disconnected')
                # print(f'### listening on {self.heart_beat_socket.getsockname()}: ', end='')
                s, addr = self.heart_beat_socket.accept()
                # print(f'accepted heart beat connection from {addr}')
            except FinReceived:
                self.state = False
                self.request_restart()
                if self.STOP:
                    break
                s.close()
                # print('### received FIN')
                # print(f'### listening on {self.heart_beat_socket.getsockname()}: ', end='')
                s, addr = self.heart_beat_socket.accept()
                # print(f'accepted heart beat connection from {addr}')
            except Exception as e:
                # print(traceback.format_exception(type(e), e, e.__traceback__))
                break
        # close
        self.heart_beat_socket.close()
        # print('### heart beat thread stopped')

    def request_restart(self):
        self.serverObj.restart_listening()


class ImageComparatorServer:
    globalInstance = None

    def __init__(self, port: int):
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', port))
        self.server.listen(1)
        # print(f'listening on {port=}')

        self.restartServerThread = threading.Event()

        self.serverThread = ServerThread(self.server)
        self.heartBeatThread = HeartBeatThread(port + 1, self)
        self.serverThread.start()
        self.heartBeatThread.start()

    def stop(self):
        self.stop_thread()
        self.server.close()

    def stop_thread(self):
        self.serverThread.put(b'STOP')
        self.heartBeatThread.STOP = True
        self.serverThread.join()
        self.heartBeatThread.join()

    def restart_listening(self):
        self.serverThread.put(b'RESTART')

    def send_bytes(self, data: bytes):
        self.serverThread.put(data)

    def send(self, name, data: bytes):
        # name 32Bytes + data
        if self.heartBeatThread.state:
            self.send_bytes(struct.pack('32s', name.encode('utf-8')) + data)
        else:
            # print('### cannot send data because client disconnected, passed')
            ...

    def send_srcImage(self, data: Image.Image | Any):
        self.send_image('srcImage', data)

    def pack_image(self, name, data: Image.Image | Any):
        w, h = data.size
        mode = data.mode
        return struct.pack('32s2i8s', name.encode('utf-8'), w, h, mode.encode('utf-8')) + data.tobytes()

    def send_dstImage(self, data: Image.Image | Any):
        self.send_image('dstImage', data)

    def send_diffImage(self, data: Image.Image | Any):
        self.send_image('diffImage', data)

    def send_image(self, name, data: Image.Image | Any):
        if not isinstance(data, Image.Image):
            data = Image.fromarray(data)
        w, h = data.size
        mode = data.mode
        self.send(name, struct.pack('2i8s', w, h, mode.encode('utf-8')) + data.tobytes())

    def send_text(self, key, value):
        self.send('text', struct.pack('32s', key.encode('utf-8')) + value.encode('utf-8'))

    def receive_image(self, data: bytes) -> tuple[str, Image.Image]:
        name, w, h, mode = struct.unpack('32s2i8s', data[:48])
        name = name.decode('utf-8').replace('\x00', '')
        mode = mode.decode('utf-8').replace('\x00', '')
        # print(name, w, h, mode)
        data = Image.frombytes(mode, (w, h), data)
        return name, data

    def receive_text(self, data: bytes) -> tuple[str, str]:
        key, value = struct.unpack('32s', data[:32])
        key = key.decode('utf-8').replace('\x00', '')
        value = value.decode('utf-8').replace('\x00', '')
        return key, value

    def send_all(self, dstImage: Image.Image, srcImage: Image.Image, diffImage: Image.Image):
        dst = self.pack_image('dstImage', dstImage)
        src = self.pack_image('srcImage', srcImage)
        diff = self.pack_image('diffImage', diffImage)
        # construct head
        head = struct.pack('3i', len(dst), len(src), len(diff))
        self.send_bytes(head + dst + src + diff)

    def received_all(self, data: bytes):
        dst_len, src_len, diff_len = struct.unpack('3i', data[:12])
        dst = data[12:12 + dst_len]
        src = data[12 + dst_len:12 + dst_len + src_len]
        diff = data[12 + dst_len + src_len:12 + dst_len + src_len + diff_len]
        return self.receive_image(dst), self.receive_image(src), self.receive_image(diff)

    def received_any(self, data: bytes):
        name = data[:32]
        name = name.decode('utf-8').replace('\x00', '')
        if "Image" in name:
            return self.receive_image(data)
        elif "text" in name:
            return self.receive_text(data)

    @staticmethod
    def get_global_instance() -> 'ImageComparatorServer':
        if ImageComparatorServer.globalInstance is None:
            ImageComparatorServer.globalInstance = ImageComparatorServer(65534)
            print("Image Comparator服务端已启动")
        return ImageComparatorServer.globalInstance

if __name__ == '__main__':

    server = ImageComparatorServer(65534)
    while True:
        if input("按任意键继续") == 'q':
            break
        # print("服务端开始计算")
        srcImage = Image.open(r'../data/16_9/no_mail.png')
        dstImage = Image.open(r'../data/16_9/no_mail.png')
        dstImage.resize(srcImage.size)
        srcImage.convert('RGB')
        dstImage.convert('RGB')
        now_confidence, diffImage, thresh = compare_images_binary_old(dstImage, srcImage)
        # print("服务端计算完成,准备传送数据")
        server.send_srcImage(srcImage)
        server.send_dstImage(dstImage)
        server.send_diffImage(diffImage)
        server.send_text('similarity', f'{now_confidence:.2f}')
        server.send_text('thresh', f'{thresh}')
        # print("服务端传送数据完成")
    server.stop()
