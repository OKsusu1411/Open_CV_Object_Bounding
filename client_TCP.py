import socket

HOST = '127.0.0.1'
PORT = 9999      

# 주소 체계(address family)로 IPv4, 소켓 타입으로 TCP 사용합니다. 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def send_data(sending):
    try:
        while True:
            # 메시지를 전송합니다.
            client_socket.sendall(sending.encode())

            # 메시지를 수신합니다.
            data = client_socket.recv(1024)
            print('Received', repr(data.decode()))
    finally:
        # 소켓을 닫습니다.
        client_socket.close()

def main():
    sending=input()
    send_data(sending)

if __name__=="__main__":
    main()
