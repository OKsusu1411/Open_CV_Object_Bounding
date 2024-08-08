import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
import socket

class ServerThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.new_interval = 1

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('0.0.0.0', 12345))
            server_socket.listen()
            print("Server listening on port 12345")

            self.client_socket, addr = server_socket.accept()
            print(f'Connected by {addr}')

            with self.client_socket:
                while True:
                    data_length_bytes = self.client_socket.recv(4)
                    if not data_length_bytes:
                        break

                    data_length = int.from_bytes(data_length_bytes, byteorder='big')
                    data = self.client_socket.recv(data_length).decode()
                    if not data:
                        break

                    self.message_received.emit(f"Received data: {data}")

                    # Send new interval to client
                    self.client_socket.sendall(str(self.new_interval).encode())

    def change_interval(self, new_interval):
        self.new_interval = new_interval


class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.server_thread = ServerThread()
        self.server_thread.message_received.connect(self.update_text_edit)
        self.server_thread.start()

    def initUI(self):
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Server')

        self.layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        self.layout.addWidget(self.text_edit)

        self.button = QPushButton('Change Interval', self)
        self.button.clicked.connect(self.change_interval)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def update_text_edit(self, message):
        self.text_edit.append(message)

    def change_interval(self):
        self.server_thread.change_interval(2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    server_gui = ServerGUI()
    server_gui.show()
    sys.exit(app.exec_())
