import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
import socket

class ClientThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.interval = 1
        self.running = True

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(('127.0.0.1', 12345))
            while self.running:
                data = "Hello, Server"
                client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
                client_socket.sendall(data.encode())

                # Receive new interval from server
                new_interval_data = client_socket.recv(1024).decode()
                self.interval = int(new_interval_data)
                self.message_received.emit(f"New interval received: {self.interval}")

                time.sleep(self.interval)

    def stop(self):
        self.running = False


class ClientGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.client_thread = ClientThread()
        self.client_thread.message_received.connect(self.update_text_edit)
        self.client_thread.start()

    def initUI(self):
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Client')

        self.layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        self.layout.addWidget(self.text_edit)

        self.setLayout(self.layout)

    def update_text_edit(self, message):
        self.text_edit.append(message)

    def closeEvent(self, event):
        self.client_thread.stop()
        self.client_thread.wait()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_gui = ClientGUI()
    client_gui.show()
    sys.exit(app.exec_())
