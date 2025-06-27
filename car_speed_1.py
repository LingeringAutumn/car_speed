# 人工点击参考线确定标尺，交互式速度估计

import cv2
import numpy as np
import os

# === 用户点击三对参考线点，计算比例尺（像素 -> 米） ===
def get_pixels_per_meter(reference_img_path):
    img = cv2.imread(reference_img_path)
    print("请点击参考线图中 3 对相邻的白线（共点击 6 次）")
    points = []

    def callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            print(f"点击：({x}, {y})")
            if len(points) == 6:
                cv2.destroyAllWindows()

    cv2.imshow("点击参考线", img)
    cv2.setMouseCallback("点击参考线", callback)
    cv2.waitKey(0)

    if len(points) != 6:
        raise ValueError("必须点击 6 个参考线点！")

    # 每两点一组，计算 3 个像素距离
    distances = [abs(points[i][1] - points[i + 1][1]) for i in range(0, 6, 2)]
    pixels_per_meter = np.mean(distances)
    print(f"三组像素距离：{distances}")
    print(f"1 米 ≈ {pixels_per_meter:.2f} 像素（取平均）")
    return pixels_per_meter

# === 点击图像两个点，获取像素差（垂直方向） ===
def get_pixel_diff_between_frames(image_paths, num_clicks=3):
    positions = []
    for path in image_paths:
        img = cv2.imread(path)
        print(f"请点击图像 {os.path.basename(path)} 中车头位置（共点击 {num_clicks} 次）")
        clicked = []

        def callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                clicked.append((x, y))
                print(f"点击：({x}, {y})")
                if len(clicked) == num_clicks:
                    cv2.destroyAllWindows()

        cv2.imshow("点击车头位置", img)
        cv2.setMouseCallback("点击车头位置", callback)
        cv2.waitKey(0)

        if len(clicked) != num_clicks:
            raise ValueError("必须点击 {} 次".format(num_clicks))
        y_mean = np.mean([p[1] for p in clicked])
        print(f"{os.path.basename(path)} 平均 Y = {y_mean:.2f}")
        positions.append(y_mean)

    pixel_diff = abs(positions[1] - positions[0])
    print(f"车头像素位移差 = {pixel_diff:.2f} px")
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

    # Step 2: 输入两个帧编号
    frame1 = int(input("请输入第一个帧编号（如20）: "))
    frame2 = int(input("请输入第二个帧编号（如22）: "))
    img1 = os.path.join(folder, f"P{frame1:05d}.bmp")
    img2 = os.path.join(folder, f"P{frame2:05d}.bmp")

    # Step 3: 点击车头点，计算像素差（3次取平均）
    pixel_diff = get_pixel_diff_between_frames([img1, img2])

    # Step 4: 估算速度
    speed = estimate_speed_by_scale(pixel_diff, pixels_per_meter)
    print(f"\n方法一（三次标尺 + 三次车头点击）速度估计：{speed:.2f} m/s ≈ {speed * 3.6:.2f} km/h")
