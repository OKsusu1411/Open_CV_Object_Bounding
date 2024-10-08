import socket
import pickle
import numpy as np
import cv2
import argparse

def TCP_Connect(ip, port):
    # 소켓 생성
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(5)

    print("서버가 시작되었습니다. 클라이언트를 기다리는 중...")

    # 클라이언트 연결 수락
    global client_socket
    client_socket, addr = server_socket.accept()
    print(f"클라이언트 {addr} 가 연결되었습니다.")

green = (0,255,0)
thick = 10

IsTrackingDepth = False
trackerDepth = 0
IsTrackingColor = False
trackerColor = 0

# mouse 동작 할당
def on_mouse_tracking_depth(event, x, y, flags, param):
    global IsTrackingDepth
    global trackerDepth
    if event == cv2.EVENT_LBUTTONDOWN:
        IsTrackingDepth=True
        for contour_depth in param[0]:
            if cv2.pointPolygonTest(contour_depth, (x, y), False) >= 0:
                xx, yy, w, h = cv2.boundingRect(contour_depth)
                trackerDepth = cv2.TrackerCSRT_create()
                roi = (xx,yy,w,h)
                trackerDepth.init(param[1],roi)
                break
    if event==cv2.EVENT_RBUTTONDOWN:
        IsTrackingDepth=False
        trackerDepth=0

def on_mouse_tracking_color(event, x, y, flags, param):
    global IsTrackingColor
    global trackerColor
    if event == cv2.EVENT_LBUTTONDOWN:
        IsTrackingColor = True
        contour_color = param[0]
        threshold = 50

        # 영역 내 contour 점들 찾기
        region_contours = []
        for cnt in contour_color:
            for pt in cnt:
                if (x - threshold) <= pt[0][0] <= (x + threshold) and (y - threshold) <= pt[0][1] <= (y + threshold):
                    region_contours.append(pt)

        if region_contours:
            x_min = min(pt[0][0] for pt in region_contours)
            x_max = max(pt[0][0] for pt in region_contours)
            y_min = min(pt[0][1] for pt in region_contours)
            y_max = max(pt[0][1] for pt in region_contours)

            w = x_max - x_min
            h = y_max - y_min
            trackerColor = cv2.TrackerCSRT_create()
            roi_color = (x_min, y_min, w, h)
            trackerColor.init(param[1], roi_color)
    if event==cv2.EVENT_RBUTTONDOWN & cv2.EVENT_FLAG_SHIFTKEY:
        IsTrackingColor=False
        trackerColor=0

class DepthImageBounding:
    def __init__(self,data_depth):
        self.data_depth = data_depth

        # 데이터 역직렬화
        self.image_depth = pickle.loads(self.data_depth)

        # 특정 거리 이하의 장애물 감지 (예: 1미터 이내)
        self.obstacle_mask = (self.image_depth > 0) & (self.image_depth < 2000)

        # 마스크를 사용하여 윤곽선 찾기
        self.contours_depth, _ = cv2.findContours(self.obstacle_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        self.boundary_image_depth = cv2.cvtColor(self.obstacle_mask.astype(np.uint8) * 255, cv2.COLOR_GRAY2BGR)

        # 이미지에 countours 초록색 윤곽선 입히기
        cv2.drawContours(self.boundary_image_depth, self.contours_depth, -1, (0, 255, 0), 2)

        if(trackerDepth!=0):
            self.isFound_depth, self.foundBox_depth = trackerDepth.update(self.boundary_image_depth)

            if (self.isFound_depth):
                self.found_x1_d = int(self.foundBox_depth[0])
                self.found_y1_d = int(self.foundBox_depth[1])
                self.found_x2_d = int(self.foundBox_depth[0]+self.foundBox_depth[2])
                self.found_y2_d = int(self.foundBox_depth[1]+self.foundBox_depth[3])

                cv2.rectangle(self.boundary_image_depth, (self.found_x1_d, self.found_y1_d), (self.found_x2_d, self.found_y2_d), green, thick)

    def image_out(self):
        # 화면 출력
        cv2.namedWindow('Depth Bounding', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Depth Bounding', self.boundary_image_depth)

        # 마우스 콜백 설정
        cv2.setMouseCallback('Depth Bounding', on_mouse_tracking_depth, param=(self.contours_depth,self.boundary_image_depth))


class ColorImageBounding:
    def __init__(self,data_color):
        self.data_color = data_color
        
        # 데이터 역직렬화
        self.image_color = pickle.loads(self.data_color)
        self.iiii = pickle.loads(self.data_color)
        # gray_image_color = cv2.cvtColor(image_color, cv2.COLOR_GRAY2BGR)
        self.blurred_image_color = cv2.GaussianBlur(self.image_color, (3, 3), 0)
        self.canny_image_color = cv2.Canny(self.blurred_image_color,50,200)

        # canny image filtering
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
        self.closed_image_color = cv2.morphologyEx(self.canny_image_color, cv2.MORPH_CLOSE, self.kernel)
        
        # 마스크를 사용하여 윤곽선 찾기
        self.contours_color, _ = cv2.findContours(self.canny_image_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 이미지에 countours 초록색 윤곽선 입히기
        cv2.drawContours(self.image_color, self.contours_color, -1, (0, 255, 0), 1)

        if(trackerColor!=0):
            self.isFound_color, self.foundBox_color = trackerColor.update(self.image_color)

            if (self.isFound_color):
                self.found_x1_c = int(self.foundBox_color[0])
                self.found_y1_c = int(self.foundBox_color[1])
                self.found_x2_c = int(self.foundBox_color[0]+self.foundBox_color[2])
                self.found_y2_c = int(self.foundBox_color[1]+self.foundBox_color[3])

                cv2.rectangle(self.image_color, (self.found_x1_c, self.found_y1_c), (self.found_x2_c, self.found_y2_c), green, thick)

    # Canny edge detection customizing
    def auto_canny(image, sigma=0.33):
        image = cv2.GaussianBlur(image, (3, 3), 0)
        
        # compute the median of the single channel pixel intensities
        v = np.median(image)
        
        # apply automatic Canny edge detection using the computed median
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv2.Canny(image, lower, upper)
        
        # return the edged image
        return edged

    def image_out(self):
        # 화면 출력
        cv2.namedWindow('Color Bounding', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Color Bounding', self.iiii)

        # 마우스 콜백 설정
        cv2.setMouseCallback('Color Bounding', on_mouse_tracking_color, param=(self.contours_color,self.image_color))   
    
    def image_out_canny(self):
        # 화면 출력
        cv2.namedWindow('Color Bounding', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Color Bounding', self.canny_image_color)

        # 마우스 콜백 설정
        cv2.setMouseCallback('Color Bounding', on_mouse_tracking_color, param=(self.contours_color,self.image_color))    
def main():
    parser = argparse.ArgumentParser(description="TCP/IP Connection")
    parser.add_argument('--host', type = str, default = '127.0.0.1')
    parser.add_argument('--port', type = int, default = '9999')
    args = parser.parse_args()
    TCP_Connect(args.host, args.port)

    try:
        while True:
            # depth 데이터 길이 정보 수신
            data_len_depth = client_socket.recv(4)
            if not data_len_depth:
                break
            data_len_depth = int.from_bytes(data_len_depth, byteorder='big')

            # depth 데이터 수신
            data_depth = b""
            while len(data_depth) < data_len_depth:
                packet_depth = client_socket.recv((data_len_depth - len(data_depth)))
                if not packet_depth:
                    break
                data_depth += packet_depth
            
            # RGB 데이터 길이 정보 수신
            data_len_color = client_socket.recv(4)
            if not data_len_color:
                break
            data_len_color = int.from_bytes(data_len_color, byteorder='big')

            # RGB 데이터 수신
            data_color = b""
            while len(data_color) < data_len_color:
                packet = client_socket.recv((data_len_color - len(data_color)))
                if not packet:
                    break
                data_color += packet

            # Class 생성
            Depthimagebounding = DepthImageBounding(data_depth)
            Colorimagebounding = ColorImageBounding(data_color)

            # image 출력
            Colorimagebounding.image_out()

            # colormap_dim_depth = boundary_image_depth.shape
            # colormap_dim_color = canny_image_color.shape

            # # if colormap_dim_depth != colormap_dim_color:
            # #     resized_image_color = cv2.resize(canny_image_color, dsize=(colormap_dim_depth[1], colormap_dim_depth[0]), interpolation=cv2.INTER_AREA)
            # #     images = np.hstack((resized_image_color, boundary_image_depth))
            # # else:
            # #     images = np.hstack((canny_image_color, boundary_image_depth))

            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        client_socket.close()
        server_socket.close()
        cv2.destroyAllWindows()
        
if __name__=="__main__":
    main()