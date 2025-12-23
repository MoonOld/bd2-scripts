import time
import cv2
import mss
import numpy as np
import win32gui

class WindowCapture:
    def __init__(self, window_title="MuMu安卓设备"):
        self.window_title = window_title
        self.monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}
        self.sct = mss.mss()
        
        # 初始化时寻找一次窗口
        self.update_window_region()

    def update_window_region(self):
        hwnd = win32gui.FindWindow(None, self.window_title)
        if not hwnd:
            return False

        # 1. 获取客户区的大小 (只有宽和高，左上角永远是 0,0)
        # client_rect = (0, 0, width, height)
        client_rect = win32gui.GetClientRect(hwnd)
        
        # 2. 将客户区的 (0,0) 坐标转换为屏幕的绝对坐标
        # 这样就自动跳过了标题栏的高度
        client_point = win32gui.ClientToScreen(hwnd, (0, 0))
        
        # 3. 更新 monitor
        self.monitor = {
            "left": client_point[0],   # 屏幕绝对 X
            "top": client_point[1],    # 屏幕绝对 Y
            "width": client_rect[2],   # 纯内容的宽
            "height": client_rect[3]   # 纯内容的高
        }
        
        
        # --- 针对 MuMu 的额外微调 (可选) ---
        # 如果你发现 MuMu 底部还有个黑条或者侧边有工具栏，
        # 你可以在这里手动减去。例如底部工具栏通常高 40px
        '''
        下面的像素可能要调整，不同桌面分辨率和缩放可能会有变化
        '''
        self.monitor["top"] += 50 # 可能会随着分辨率变化 
        self.monitor["height"] = 900
        print(self.monitor)

        
        return True

    def get_screenshot(self):
        """
        核心截图方法
        返回: OpenCV 格式的图片 (BGR)
        """
        # 1. 截图 (mss 返回的是原生的 BGRA 格式，非常快)
        img_raw = self.sct.grab(self.monitor)
        
        # 2. 转为 Numpy 数组
        img = np.array(img_raw)
        
        # 3. 极速转换: 去掉 Alpha 通道 (BGRA -> BGR)
        # 这一步比 cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) 还要快
        # 直接切片，只取前3个通道
        img = img[:, :, :3]
        
        return img

# ====================
# 使用示例
# ====================
if __name__ == "__main__":
    # 确保你的模拟器名字叫这个，MuMu12 通常叫 "MuMu模拟器12" 或者就是 "MuMu模拟器"
    # 你可以把鼠标放在任务栏图标上，看看浮出来的字是什么
    capturer = WindowCapture() 

    print("开始截图，按 'q' 退出...")
    
    # 帧率计算器
    fps_time = time.time()
    counter = 0

    import time

    for i in range(30):
        start_time = time.time()
        frame = capturer.get_screenshot()
        elapsed = (time.time() - start_time) * 1000  # ms

        if frame is None or frame.size == 0:
            print("窗口可能已最小化...")
            time.sleep(1)
            continue

        print(f"第{i+1}次截图用时: {elapsed:.2f} ms")
        time.sleep(0.1)  # 可以加一点间隔
