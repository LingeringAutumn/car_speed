# 车辆速度估算（方法一）：人工点击确定标尺与帧图位置
# 完全交互式：用户点击参考线、点击车辆帧、输入参考帧号与参考数据

import cv2
import numpy as np
import os

# === 用户点击两个参考线点，计算比例尺（像素 -> 米） ===
def get_pixels_per_meter(reference_img_path):
    img = cv2.imread(reference_img_path)
    print("请点击参考线图中两个相邻的 1 米间距白线")
    points = []

    def callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            if len(points) == 2:
                cv2.destroyAllWindows()

    cv2.imshow("点击参考线", img)
    cv2.setMouseCallback("点击参考线", callback)
    cv2.waitKey(0)

    if len(points) != 2:
        raise ValueError("必须点击两个参考线点")

    pixel_dist = abs(points[0][1] - points[1][1])
    print(f"1 米 ≈ {pixel_dist} 像素")
    return pixel_dist

# === 点击图像两个点，获取像素差（垂直方向） ===
def get_pixel_diff_between_frames(image_paths):
    positions = []
    for path in image_paths:
        img = cv2.imread(path)
        print(f"请点击图像 {os.path.basename(path)} 中车头位置")
        clicked = []

        def callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                clicked.append((x, y))
                cv2.destroyAllWindows()

        cv2.imshow("点击车头位置", img)
        cv2.setMouseCallback("点击车头位置", callback)
        cv2.waitKey(0)

        if len(clicked) != 1:
            raise ValueError("你必须点击一个点！")
        positions.append(clicked[0])

    p1, p2 = positions
    pixel_diff = abs(p2[1] - p1[1])  # 垂直方向像素差
    print(f"像素差 = {pixel_diff} px")
    return pixel_diff

# === 根据比例尺估算速度 ===
def estimate_speed_by_scale(pixel_diff, pixels_per_meter, delta_t=0.054):
    k = 1 / pixels_per_meter  # m/px
    speed = k * pixel_diff / delta_t
    return speed

# === 主程序 ===
if __name__ == "__main__":
    folder = "./data/"

    # Step 1: 用户选择参考线图，计算比例尺
    ref_img = os.path.join(folder, "P00075.bmp")
    pixels_per_meter = get_pixels_per_meter(ref_img)

    # Step 2: 让用户输入要使用的两个图像帧号
    frame1 = int(input("请输入第一个帧编号（如20）: "))
    frame2 = int(input("请输入第二个帧编号（如22）: "))
    img1 = os.path.join(folder, f"P{frame1:05d}.bmp")
    img2 = os.path.join(folder, f"P{frame2:05d}.bmp")

    # Step 3: 用户点击车头点，计算像素差
    pixel_diff = get_pixel_diff_between_frames([img1, img2])

    # Step 4: 计算速度
    speed = estimate_speed_by_scale(pixel_diff, pixels_per_meter)
    print(f"方法一（参考线标尺）速度估计：{speed:.2f} m/s ≈ {speed * 3.6:.2f} km/h")
