# 车辆速度估算（方法二）：仅依赖车长和像素长度比例估速，无需参考线图

import cv2
import numpy as np
import os

# === 获取车身在图像中所占的像素高度 ===
def get_car_pixel_length(image_path):
    img = cv2.imread(image_path)
    print("请点击图中车头和车尾位置（顺序不限）")
    points = []

    def callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            if len(points) == 2:
                cv2.destroyAllWindows()

    cv2.imshow("点击车头车尾", img)
    cv2.setMouseCallback("点击车头车尾", callback)
    cv2.waitKey(0)

    if len(points) != 2:
        raise ValueError("必须点击两个点")

    pixel_length = abs(points[0][1] - points[1][1])
    print(f"车身像素高度 = {pixel_length} px")
    return pixel_length

# === 点击两帧中车辆的前沿位置 ===
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
            raise ValueError("必须点击一个点")
        positions.append(clicked[0])

    p1, p2 = positions
    pixel_diff = abs(p2[1] - p1[1])
    print(f"车头像素位移差 = {pixel_diff} px")
    return pixel_diff

# === 根据车长比例估算速度 ===
def estimate_speed_from_car_length(pixel_diff, car_length_m, car_pixel_height, delta_t=0.054):
    k = car_length_m / car_pixel_height  # 米/像素
    speed = k * pixel_diff / delta_t
    return speed

# === 主程序 ===
if __name__ == "__main__":
    folder = "./data/"

    # Step 1: 用户选择参考车的帧图（如 P00001.bmp）
    ref_frame = input("请输入车身参考图像帧号（如1）: ")
    ref_img = os.path.join(folder, f"P{int(ref_frame):05d}.bmp")

    # Step 2: 用户点击车头车尾获取像素高度
    car_pixel_height = get_car_pixel_length(ref_img)

    # Step 3: 用户输入真实车长（米）
    car_length_m = float(input("请输入该车实际车长（单位：米）: "))

    # Step 4: 用户输入两个用于估速的帧编号
    frame1 = int(input("请输入第一帧编号: "))
    frame2 = int(input("请输入第二帧编号: "))
    img1 = os.path.join(folder, f"P{frame1:05d}.bmp")
    img2 = os.path.join(folder, f"P{frame2:05d}.bmp")

    # Step 5: 用户点击两个车头位置
    pixel_diff = get_pixel_diff_between_frames([img1, img2])

    # Step 6: 估算速度
    speed = estimate_speed_from_car_length(pixel_diff, car_length_m, car_pixel_height)
    print(f"方法二（车长估比）速度估计：{speed:.2f} m/s ≈ {speed * 3.6:.2f} km/h")