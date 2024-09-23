import numpy as np
import matplotlib.pyplot as plt

# 读取角度数据
def read_angles(file_path):
    angles = []
    with open(file_path, 'r') as f:
        for line in f:
            try:
                angle = float(line.strip())
                angles.append(angle)
            except ValueError:
                print(f"Invalid data in {file_path}: {line.strip()}")
    return angles

# 主程序
file_paths = ['NavigationService.g3log.20240914-185212.1325/wo_speed/angles_2_s1_5_pre.txt', 'NavigationService.g3log.20240914-185212.1325/w_speed/angles_2_s1_5_pre.txt']  # 添加更多文件路径

# 存储所有文件的角度数据
all_angles = []

# 读取每个文件的角度数据
for file_path in file_paths:
    angles = read_angles(file_path)
    all_angles.append(angles)

# 创建 x 轴数据（假设所有文件的夹角数量相同）
x_values = np.arange(1, len(all_angles[0]) + 1)

# 可视化
plt.figure(figsize=(20, 6))

labels = ['wo_speed_s1', 'w_speed_s1']
# 为每个文件的角度数据绘制曲线
for i, angles in enumerate(all_angles):
    # plt.plot(x_values, angles, label=f'{i + 1}', marker='o', markersize=2)
    plt.plot(x_values, angles, label=labels[i], marker='o', markersize=2)


plt.title('Comparison of Angles from Multiple Files')
plt.xlabel('Index')
plt.ylabel('Angle (degrees)')
plt.legend()
plt.grid()
plt.xticks(x_values)  # 设置 x 轴刻度
plt.show()
