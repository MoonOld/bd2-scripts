# coding: utf-8
import subprocess
import numpy as np
import cv2
import time
class AdbClient:
    def __init__(self):
        # 1. 指向 Windows 里的 adb.exe 路径
        #    (/mnt/d/ 是 WSL 访问 D 盘的入口)
        self.adb_path = "D:\\download\\platform-tools-latest-windows\\platform-tools\\adb.exe" 
        
        # 2. 这里的 IP 写 127.0.0.1 即可
        #    因为这行命令虽然是 WSL 发出的，但实际上是 Windows 系统在执行
        #    对于 Windows 来说，MuMu 就在本机 (Localhost)
        self.device_address = "127.0.0.1:16384"

        self.width = 1600 
        self.height = 900 
        
        self.connect()

    def connect(self):
        # 组装命令: /mnt/c/.../adb.exe connect 127.0.0.1:7555
        cmd = f"{self.adb_path} connect {self.device_address}"
        
        # 执行
        subprocess.run(cmd, shell=True)
        print("尝试连接完成")

    def tap(self, x, y):
        # 点击也是同理
        cmd = f"{self.adb_path} -s {self.device_address} shell input tap {x} {y}"
        subprocess.Popen(cmd, shell=True)
    

    def hold(self, x, y, time):
        cmd = f"{self.adb_path} -s {self.device_address} shell input swipe {x} {y} {x} {y} {time}"
        subprocess.run(cmd, shell=True)
    
    def get_screen_fast(self):
        # 1. 去掉 -p 参数，获取原始数据
        cmd = [self.adb_path, '-s', self.device_address, 'exec-out', 'screencap']
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data = process.stdout.read()
        
        if not raw_data: 
            print("错误: 截屏数据为空")
            return None

        # 2. 解析 Raw Header
        # 安卓 screencap 的原始数据前 12 个字节通常是 [Width, Height, Format]
        # 但有时候会有差异，最稳妥的方法是直接跳过前 12 字节（或 16 字节）
        # 真正的数据大小应该是 width * height * 4 (RGBA)
        expected_size = self.width * self.height * 4
        
        # 如果数据多了，说明有 Header，切掉它
        pixels = raw_data[-expected_size:] 
        
        # 3. 转换为 Numpy 数组
        image = np.frombuffer(pixels, dtype=np.uint8)
        
        # 4. 重塑形状 (Height, Width, 4通道-RGBA)
        image = image.reshape((self.height, self.width, 4))
        
        # 5. 去掉 Alpha 通道 (变回 BGR 用于 OpenCV)
        # 这一步极快，比 imdecode 快得多
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        
        return image
    
if __name__ == "__main__":
    adb = AdbClient()
    timer = time.time()
    adb.get_screen_fast()
    print(f"时间: {time.time() - timer}")