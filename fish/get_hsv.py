import cv2
import numpy as np
from pathlib import Path
# 把这里的路径换成你截下来的那张包含滑条的游戏截图
image_path = Path(__file__).resolve().parent / "templates" / "reel_in_step.png"
image_path = str(image_path)    
def pick_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = image_hsv[y, x]
        # H:0-179, S:0-255, V:0-255
        print(f"点击坐标: {x},{y}")
        print(f"HSV值: {pixel}")
        print(f"建议范围: Lower=[{max(0, pixel[0]-10)}, 50, 50], Upper=[{min(179, pixel[0]+10)}, 255, 255]")
        print("-" * 20)

img = cv2.imread(image_path)
if img is None:
    print("找不到图片，请检查路径")
    exit()

# 转换为 HSV
image_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

cv2.imshow("Click Control - Press ESC to exit", img)
cv2.setMouseCallback("Click Control - Press ESC to exit", pick_color)
cv2.waitKey(0)
cv2.destroyAllWindows()