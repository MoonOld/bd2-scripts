import cv2
import numpy as np
import time
from pathlib import Path
from win_capture import WindowCapture

class VisionProcessor:
    """
    Handles image processing and situation analysis using OpenCV.
    """
    def __init__(self):
        # Resolve template path relative to this file (NOT the current working directory).
        template_path = Path(__file__).resolve().parent / "templates" / "hooked.png"
        self.__fish_hooked_template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
        if self.__fish_hooked_template is None:
            raise FileNotFoundError(
                f"Failed to load template image. Expected at: {template_path}\n"
                f"Tip: create `fish/templates/` and place `fish_hooked.png` there."
            )
        harvest_template_path = Path(__file__).resolve().parent / "templates" / "harvest.png"
        self.__fish_should_harvest_template = cv2.imread(str(harvest_template_path), cv2.IMREAD_COLOR)
        if self.__fish_should_harvest_template is None:
            raise FileNotFoundError(
                f"Failed to load template image. Expected at: {harvest_template_path}\n"
                f"Tip: create `fish/templates/` and place `harvest.png` there."
            )
        reel_scene_template_path = Path(__file__).resolve().parent / "templates" / "reel.png"
        self.__fish_reel_scene_template = cv2.imread(str(reel_scene_template_path), cv2.IMREAD_COLOR)
        if self.__fish_reel_scene_template is None:
            raise FileNotFoundError(
                f"Failed to load template image. Expected at: {reel_scene_template_path}\n"
                f"Tip: create `fish/templates/` and place `reel_scene.png` there."
            )
        
        self.__capture = WindowCapture()

        # ==========================================
        # 1. 区域设置 (ROI) - 请根据你的实际截图调整
        # 这些是相对于整个模拟器窗口的坐标
        # 比如：只截取画面中下部那个长条
        # ==========================================
        self.roi_y = 740    # 滑条顶部的 Y 坐标
        self.roi_h = 60    # 滑条的高度
        self.roi_x = 580    # 滑条左边的 X 坐标
        self.roi_w = 550    # 滑条的宽度
        # x 584 y 743 x 1100 y 790

        # ==========================================
        # 2. 颜色阈值 (你需要用上面的工具测出来填进去)
        # 格式: np.array([H, S, V])
        # ==========================================
        
        # 假设光标是白色的 (白色通常 S 很低，V 很高)
        self.cursor_lower = np.array([  0,   0, 255]) 
        self.cursor_upper = np.array([1, 1, 255])

        # 假设完美区域是亮黄色的
        self.zone_lower = np.array([15, 50, 50])
        self.zone_upper = np.array([35, 255, 255])
        
        # 点击偏差容忍度 (像素)
        self.hit_threshold = 80

    def capture_screen(self):
        """
        Capture the current screen or simulator window.
        """
        return self.__capture.get_screenshot()
    
    
    def find_center_x(self, img_roi, lower, upper, label="obj"):
        """
        通用方法：输入图片和颜色范围，返回该颜色物体的中心 X 坐标
        """
        # 1. 转 HSV
        hsv = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)
        
        # 2. 提取颜色掩码 (黑白图，目标是白，背景是黑)
        mask = cv2.inRange(hsv, lower, upper)
        
        # 3. 找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 找到最大的轮廓（防止噪点干扰）
            c = max(contours, key=cv2.contourArea)
            
            # 计算矩来找中心点
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                return cx, c # 返回 X坐标 和 轮廓本身(画图用)
        
        return None, None

    def fish_hooked(self):
        """
        Detect if the fish is hooked.
        """
        # 790 239 804 306
        image = self.capture_screen()
        image = image[230:320, 780:810]
        result = cv2.matchTemplate(image, self.__fish_hooked_template, cv2.TM_CCOEFF_NORMED)
        # matchTemplate returns a heatmap; use the max score as the match confidence.
        max_val = float(result.max())
        if max_val > 0.7:
            return True
        else:
            return False

    def on_critical_point(self):
        """
        Detect if the fish is on the critical point.
        """
        # 1. 裁剪 ROI (只看滑条区域，提升速度 10倍)
        # 注意 numpy 切片是 img[y:y+h, x:x+w]
        screen = self.capture_screen()
        roi = screen[self.roi_y : self.roi_y+self.roi_h, 
                              self.roi_x : self.roi_x+self.roi_w]
        
        # 2. 寻找光标位置
        cursor_x, cursor_cnt = self.find_center_x(roi, self.cursor_lower, self.cursor_upper, "Cursor")
        
        # 3. 寻找目标区域位置
        zone_x, zone_cnt = self.find_center_x(roi, self.zone_lower, self.zone_upper, "Zone")

        should_click = False

        # 4. 判断逻辑
        if cursor_x is not None and zone_x is not None:
            # 计算距离
            distance = abs(cursor_x - zone_x)
            
            # 调试输出
            # print(f"Cursor: {cursor_x}, Zone: {zone_x}, Dist: {distance}")
            
            if distance < self.hit_threshold:
                should_click = True

        return should_click
    
    def in_reel_scene(self):
        """
        Detect if the fish is in the reel scene.
        """
        image = self.capture_screen()
        # 538 128 1065 235
        image = image[740:790, 580:1130]
        max_val, _ = self.match_by_edge(image, self.__fish_reel_scene_template)
        return max_val > 0.3

    def fish_should_harvest(self):
        """
        Detect if the fish should be harvested.
        """
        image = self.capture_screen()
        # 538 128 1065 235
        image = image[120:240, 530:1070]
        max_val, _ = self.match_by_edge(image, self.__fish_should_harvest_template)
        return max_val > 0.2

    def match_by_edge(self, screen_img, template_img):
        # 1. 转灰度
        screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
        tpl_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)

        # 2. Canny 边缘检测 (提取线条)
        # 这里的阈值 100, 200 可能需要微调，看你的图标线条清晰度
        screen_edge = cv2.Canny(screen_gray, 100, 200)
        tpl_edge = cv2.Canny(tpl_gray, 100, 200)

        # 3. 匹配线条图
        # 注意：匹配边缘时，TM_CCOEFF_NORMED 通常效果最好
        res = cv2.matchTemplate(screen_edge, tpl_edge, cv2.TM_CCOEFF_NORMED)
        
        # 获取最大匹配值
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        # 调试显示边缘图 (看看是不是提取出了干净的轮廓)
        # cv2.imshow("Screen Edge", screen_edge)
        # cv2.imshow("Template Edge", tpl_edge)
        
        return max_val, max_loc

if __name__ == "__main__":
    vision = VisionProcessor()
    while True:
        now_time = time.time()
        in_reel_scene = vision.in_reel_scene()
        print(f"time: {time.time() - now_time}, in_reel_scene: {in_reel_scene}")

