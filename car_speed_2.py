# 仅依赖车长和像素长度比例估速，无需参考线图

import cv2
import numpy as np
import os

# === 获取车身在图像中所占的像素高度（点击3次车头+3次车尾） ===
def get_car_pixel_length(image_path, num_clicks=3):
    img = cv2.imread(image_path)
    print(f"请点击图中车头位置（共点击 {num_clicks} 次）")
    head_clicks, tail_clicks = [], []

    def head_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            head_clicks.append((x, y))
            print(f"车头点击：({x}, {y})")
            if len(head_clicks) == num_clicks:
                cv2.destroyAllWindows()

    cv2.imshow("点击车头位置", img)
    cv2.setMouseCallback("点击车头位置", head_callback)
    cv2.waitKey(0)

    if len(head_clicks) != num_clicks:
        raise ValueError("必须点击车头 {} 次！".format(num_clicks))

    print(f"请点击图中车尾位置（共点击 {num_clicks} 次）")

    def tail_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            tail_clicks.append((x, y))
            print(f"车尾点击：({x}, {y})")
            if len(tail_clicks) == num_clicks:
                cv2.destroyAllWindows()

    cv2.imshow("点击车尾位置", img)
    cv2.setMouseCallback("点击车尾位置", tail_callback)
    cv2.waitKey(0)

    if len(tail_clicks) != num_clicks:
        raise ValueError("必须点击车尾 {} 次！".format(num_clicks))

    head_y = np.mean([p[1] for p in head_clicks])
    tail_y = np.mean([p[1] for p in tail_clicks])
    pixel_height = abs(head_y - tail_y)

    print(f"车身像素高度 ≈ {pixel_height:.2f} px")
    return pixel_height

# === 点击两个帧中车头位置（各点击3次） ===
def get_pixel_diff_between_frames(image_paths, num_clicks=3):
    y_coords = []
    for path in image_paths:
        img = cv2.imread(path)
        print(f"请在图像 {os.path.basename(path)} 中点击车头位置（共点击 {num_clicks} 次）")
        clicks = []

        def callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                clicks.append((x, y))
                print(f"点击：({x}, {y})")
                if len(clicks) == num_clicks:
                    cv2.destroyAllWindows()

        cv2.imshow("点击车头位置", img)
        cv2.setMouseCallback("点击车头位置", callback)
        cv2.waitKey(0)

        if len(clicks) != num_clicks:
            raise ValueError("必须点击 {} 次".format(num_clicks))

        y_mean = np.mean([p[1] for p in clicks])
        print(f"图像 {os.path.basename(path)} 平均 Y 坐标：{y_mean:.2f}")
        y_coords.append(y_mean)

    pixel_diff = abs(y_coords[1] - y_coords[0])
    print(f"车头像素位移差 = {pixel_diff:.2f} px")
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
    print(f"\n方法二（车长估比 + 三次点击取平均）速度估计：{speed:.2f} m/s ≈ {speed * 3.6:.2f} km/h")
