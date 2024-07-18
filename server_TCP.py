import socket

HOST = "127.0.0.1"
PORT = 9999        

# 주소 체계(address family)로 IPv4, 소켓 타입으로 TCP 사용합니다. 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# WinError 10048 에러 해결를 위해 필요합니다.
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
server_socket.bind((HOST, PORT))

# 서버가 클라이언트의 접속을 허용하도록 합니다.
server_socket.listen()

# accept 함수에서 대기하다가 클라이언트가 접속하면 새로운 소켓을 리턴합니다.
client_socket, addr = server_socket.accept()

# 접속한 클라이언트의 주소입니다.
print('Connected by', addr)

def send_data(sending):
    while True:
        data = client_socket.recv(1024)

        # 빈 문자열을 수신하면 루프를 중지합니다.
        if not data:
            break
        
        # 수신받은 문자열을 출력합니다.
        print('Received from', addr, data.decode())

        client_socket.sendall(sending)

    # 소켓을 닫습니다.
    client_socket.close()
    server_socket.close()

def main():
    sending = input()
    send_data(sending)

if __name__=="__main__":
    main()