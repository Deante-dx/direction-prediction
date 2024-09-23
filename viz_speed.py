# import matplotlib.pyplot as plt
# import numpy as np
# import math

# # 初始化列表以存储提取的数据
# x_values = []
# y_values = []
# vx_values = []
# vy_values = []
# speeds = []
# angles = []

# # 读取文件并提取数据
# with open('world_coor.txt', 'r') as file:
#     for line in file:
#         # 分割行数据
#         parts = line.split(':')
#         if len(parts) > 2:
#             # 提取最后一部分并分割为数值
#             values = parts[-1].strip().split(',')
#             if len(values) >= 4:
#                 x = float(values[0])
#                 y = float(values[1])
#                 vx = float(values[2])
#                 vy = float(values[3])
#                 x_values.append(x)
#                 y_values.append(y)
#                 vx_values.append(vx)
#                 vy_values.append(vy)

# # 计算速度模长
# for vx, vy in zip(vx_values, vy_values):
#     speed = math.sqrt(vx**2 + vy**2)
#     speeds.append(speed)

# # 计算速度方向夹角变化
# for i in range(1, len(vx_values)):
#     v1 = np.array([vx_values[i-1], vy_values[i-1]])
#     v2 = np.array([vx_values[i], vy_values[i]])
    
#     # 计算点积和模长
#     dot_product = np.dot(v1, v2)
#     magnitude_v1 = np.linalg.norm(v1)
#     magnitude_v2 = np.linalg.norm(v2)
    
#     # 计算夹角（弧度）
#     if magnitude_v1 != 0 and magnitude_v2 != 0:
#         cos_theta = dot_product / (magnitude_v1 * magnitude_v2)
#         cos_theta = np.clip(cos_theta, -1.0, 1.0)  # 防止数值误差导致的超出范围
#         angle = np.arccos(cos_theta)  # 角度
#         angles.append(np.degrees(angle))  # 转换为度数
#     else:
#         angles.append(0.0)  # 如果有零速度矢量，角度设置为0

# # 绘制速度模长随时间变化
# plt.figure(figsize=(30, 6))
# plt.plot(speeds, marker='o', linestyle='-', color='b', markersize=1)
# plt.title('Speed Magnitude over Time')
# plt.xlabel('Time Step')
# plt.ylabel('Speed Magnitude')
# plt.grid()
# plt.show()

# # 绘制速度方向夹角随时间变化
# plt.figure(figsize=(30, 6))
# plt.plot(angles, marker='o', linestyle='-', color='r', markersize=1)
# plt.title('Change in Velocity Direction Angle over Time')
# plt.xlabel('Time Step')
# plt.ylabel('Angle Change (degrees)')
# plt.grid()
# plt.show()

import matplotlib.pyplot as plt
import numpy as np
import math

# 初始化列表以存储提取的数据
x_values = []
y_values = []
vx_values = []
vy_values = []
speeds = []
angles = []

# 读取文件并提取数据
flag = 1
with open('NavigationService.g3log.20240914-185212.1325/world_coor.txt', 'r') as file:
    for line in file:
        # 分割行数据
        parts = line.split(':')
        if len(parts) > 2:
            # 提取最后一部分并分割为数值
            values = parts[-1].strip().split(',')
            if len(values) >= 4:
                x = float(values[0])
                y = float(values[1])
                vx = float(values[2])
                vy = float(values[3])
                x_values.append(x)
                y_values.append(y)
                vx_values.append(vx)
                vy_values.append(vy)
                # if flag % 2 == 1:
                #     x_values.append(x)
                #     y_values.append(y)
                #     vx_values.append(vx)
                #     vy_values.append(vy)
                # flag += 1

# 计算速度模长
for vx, vy in zip(vx_values, vy_values):
    speed = math.sqrt(vx**2 + vy**2)
    speeds.append(speed)

# 计算速度方向夹角变化
for i in range(1, len(vx_values)):
    v1 = np.array([vx_values[i-1], vy_values[i-1]])
    v2 = np.array([vx_values[i], vy_values[i]])
    
    # 计算点积和模长
    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)
    
    # 计算夹角（弧度）
    if magnitude_v1 != 0 and magnitude_v2 != 0:
        cos_theta = dot_product / (magnitude_v1 * magnitude_v2)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)  # 防止数值误差导致的超出范围
        angle = np.arccos(cos_theta)  # 角度
        angles.append(np.degrees(angle))  # 转换为度数
    else:
        angles.append(0.0)  # 如果有零速度矢量，角度设置为0

# 创建图形对象和主轴
fig, ax1 = plt.subplots(figsize=(30, 8))

# 在主轴上绘制速度模长
color = 'tab:blue'
ax1.set_xlabel('Time Step')
ax1.set_ylabel('Speed Magnitude', color=color)
ax1.plot(speeds, marker='o', linestyle='-', color=color, markersize=2, label='Speed Magnitude')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid()

# 创建次轴用于绘制速度方向变化的角度
ax2 = ax1.twinx()  # 共享同一x轴
color = 'tab:red'
ax2.set_ylabel('Angle Change (degrees)', color=color)
ax2.plot(angles, marker='o', linestyle='-', color=color, markersize=2, label='Angle Change')
ax2.tick_params(axis='y', labelcolor=color)

# 添加图例
fig.tight_layout()  # 自动调整布局以避免重叠
plt.title('Speed Magnitude and Angle Change Over Time')

# 显示图像
plt.show()
