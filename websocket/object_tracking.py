import pickle
import numpy as np
import cv2
import globals  # 전역 변수를 가져옴

green = (0, 255, 0)
thick = 10

# mouse 동작 할당
def on_mouse_tracking_depth(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        globals.IsTrackingDepth = True
        for contour_depth in param[0]:
            if cv2.pointPolygonTest(contour_depth, (x, y), False) >= 0:
                xx, yy, w, h = cv2.boundingRect(contour_depth)
                globals.trackerDepth = cv2.legacy.TrackerCSRT_create()
                roi = (xx, yy, w, h)
                globals.trackerDepth.init(param[1], roi)
                break
    if event == cv2.EVENT_RBUTTONDOWN:
        globals.IsTrackingDepth = False
        globals.trackerDepth = None

def on_mouse_tracking_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        globals.IsTrackingColor = True
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
            globals.trackerColor = cv2.legacy.TrackerCSRT_create()
            roi_color = (x_min, y_min, w, h)
            globals.trackerColor.init(param[1], roi_color)
    if event == cv2.EVENT_RBUTTONDOWN and flags & cv2.EVENT_FLAG_SHIFTKEY:
        globals.IsTrackingColor = False
        globals.trackerColor = None

class DepthImageBounding:
    def __init__(self, data_depth):
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

        if globals.trackerDepth:
            self.isFound_depth, self.foundBox_depth = globals.trackerDepth.update(self.boundary_image_depth)

            if self.isFound_depth:
                self.found_x1_d = int(self.foundBox_depth[0])
                self.found_y1_d = int(self.foundBox_depth[1])
                self.found_x2_d = int(self.foundBox_depth[0] + self.foundBox_depth[2])
                self.found_y2_d = int(self.foundBox_depth[1] + self.foundBox_depth[3])

                cv2.rectangle(self.boundary_image_depth, (self.found_x1_d, self.found_y1_d), (self.found_x2_d, self.found_y2_d), green, thick)

    def image_out(self):
        # 화면 출력
        cv2.namedWindow('Depth Bounding', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Depth Bounding', self.boundary_image_depth)
        cv2.waitKey(1)
        # 마우스 콜백 설정
        cv2.setMouseCallback('Depth Bounding', on_mouse_tracking_depth, param=(self.contours_depth, self.boundary_image_depth))

class ColorImageBounding:
    def __init__(self, data_color):
        self.data_color = data_color

        # 데이터 역직렬화
        self.image_color = pickle.loads(self.data_color)

        # gray_image_color = cv2.cvtColor(image_color, cv2.COLOR_GRAY2BGR)
        self.blurred_image_color = cv2.GaussianBlur(self.image_color, (3, 3), 0)
        self.canny_image_color = cv2.Canny(self.blurred_image_color, 50, 200)

        # canny image filtering
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        self.closed_image_color = cv2.morphologyEx(self.canny_image_color, cv2.MORPH_CLOSE, self.kernel)

        # 마스크를 사용하여 윤곽선 찾기
        self.contours_color, _ = cv2.findContours(self.canny_image_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 이미지에 countours 초록색 윤곽선 입히기
        cv2.drawContours(self.image_color, self.contours_color, -1, (0, 255, 0), 1)

        if globals.trackerColor:
            self.isFound_color, self.foundBox_color = globals.trackerColor.update(self.image_color)

            if self.isFound_color:
                self.found_x1_c = int(self.foundBox_color[0])
                self.found_y1_c = int(self.foundBox_color[1])
                self.found_x2_c = int(self.foundBox_color[0] + self.foundBox_color[2])
                self.found_y2_c = int(self.foundBox_color[1] + self.foundBox_color[3])

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
        cv2.imshow('Color Bounding', self.image_color)

        # 마우스 콜백 설정
        cv2.setMouseCallback('Color Bounding', on_mouse_tracking_color, param=(self.contours_color, self.image_color))

    def image_out_canny(self):
        # 화면 출력
        cv2.namedWindow('Color Bounding', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Color Bounding', self.canny_image_color)

        # 마우스 콜백 설정
        cv2.setMouseCallback('Color Bounding', on_mouse_tracking_color, param=(self.contours_color, self.image_color))
