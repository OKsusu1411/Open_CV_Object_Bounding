import socket
import pickle
import numpy as np
import cv2

# 서버 정보
SERVER_IP = '10.210.61.88'
SERVER_PORT = 9998

# 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)

print("서버가 시작되었습니다. 클라이언트를 기다리는 중...")

# 클라이언트 연결 수락
client_socket, addr = server_socket.accept()
print(f"클라이언트 {addr} 가 연결되었습니다.")

selected_ids = set()
previous_contours = {}
next_id = 0

green = (0,255,0)
thick =15

# def on_mouse(event, x, y, flags, param):
    
#     if event == cv2.EVENT_LBUTTONDOWN:
#         for contour in param:
#             if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
#                 M = cv2.moments(contour)
#                 if M['m00'] != 0:
#                     cx = int(M['m10'] / M['m00'])
#                     cy = int(M['m01'] / M['m00'])
#                     print(f"Contour clicked at: ({cx}, {cy})")
#                 break

IsTracking = False
tracker = 0
def on_mouse_tracking(event, x, y, flags, param):
    global IsTracking
    global tracker
    if event == cv2.EVENT_LBUTTONDOWN:
        IsTracking=True
        for contour in param[0]:
            if cv2.pointPolygonTest(contour, (x, y), False) >= 0:
                x, y, w, h = cv2.boundingRect(contour)
                tracker = cv2.TrackerCSRT_create()
                roi = (x,y,w,h)
                tracker.init(param[1],roi);
                break

try:
    while True:
        # 데이터 길이 정보 수신
        data_len = client_socket.recv(4)
        if not data_len:
            break
        data_len = int.from_bytes(data_len, byteorder='big')

        # 데이터 수신
        data = b""
        while len(data) < data_len:
            packet = client_socket.recv(data_len - len(data))
            if not packet:
                break
            data += packet

        # 데이터 역직렬화
        depth_image = pickle.loads(data)

        # 특정 거리 이하의 장애물 감지 (예: 1미터 이내)
        obstacle_mask = (depth_image > 0) & (depth_image < 3000)

        # 마스크를 사용하여 윤곽선 찾기
        contours, _ = cv2.findContours(obstacle_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 원본 이미지에 윤곽선을 그리기
        display_image = cv2.cvtColor(obstacle_mask.astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)
        #cv2.drawContours(display_image, contours, -1, (0, 255, 0), 2)

        if(tracker!=0):
            isFound, foundBox = tracker.update(display_image)

            if (isFound):
                found_x1= int(foundBox[0])
                found_y1= int(foundBox[1])
                found_x2= int(foundBox[0]+foundBox[2])
                found_y2= int(foundBox[1]+foundBox[3])

                cv2.rectangle(display_image, (found_x1, found_y1), (found_x2, found_y2), green, thick)

            # 마우스 콜백 설정
            cv2.imshow('Obstacles', display_image)
        else:
            # 원본 이미지에 윤곽선을 그리기
            cv2.drawContours(display_image, contours, -1, (0, 255, 0), 2)

            # 마우스 콜백 설정
            cv2.imshow('Obstacles', display_image)


        cv2.setMouseCallback('Obstacles', on_mouse_tracking, param=(contours,display_image))

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    client_socket.close()
    server_socket.close()
    cv2.destroyAllWindows()
