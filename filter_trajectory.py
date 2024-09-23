# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.special import comb

# # 读取数据并提取 (x, y) 坐标
# def read_data(file_path):
#     x_values = []
#     y_values = []
#     flag = 1
#     with open(file_path, 'r') as file:
#         for line in file:
#             parts = line.split(':')
#             if len(parts) > 2:
#                 values = parts[-1].strip().split(',')
#                 if len(values) >= 4:
#                     try:
#                         x = float(values[0])
#                         y = float(values[1])
#                         if flag%3 == 1:
#                             x_values.append(x)
#                             y_values.append(y)
#                         flag += 1
#                     except ValueError:
#                         print(f"Invalid data: {values}")
    
#     return np.array(x_values), np.array(y_values)

# # 计算贝塞尔曲线
# def bezier_curve(points, num_points=5):
#     n = len(points) - 1
#     t = np.linspace(0, 1, num_points)
#     curve = np.zeros((num_points, 2))
    
#     for i in range(n + 1):
#         curve += np.outer(comb(n, i) * (t ** i) * ((1 - t) ** (n - i)), points[i])
    
#     return curve

# # 计算切线方向
# def calculate_tangent_direction(bezier_points):
#     # 计算贝塞尔曲线的最后一个点的切线
#     last_point = bezier_points[[-1]]
#     second_last_point = bezier_points[-2:-1]  #大约1s
    
#     tangent_vector = last_point - second_last_point
#     tangent_vector = np.mean(tangent_vector, axis=0)
#     tangent_direction = tangent_vector / np.linalg.norm(tangent_vector)  # 单位向量
#     return tangent_direction

# # 计算平均方向
# def calculate_average_direction(points):
#     vectors = points[1:] - points[0]
#     average_vector = np.mean(vectors, axis=0)
#     average_direction = average_vector / np.linalg.norm(average_vector)  # 单位向量
#     return average_direction

# # 计算夹角
# def calculate_angle_between(v1, v2):
#     cos_theta = np.clip(np.dot(v1, v2), -1.0, 1.0)  # 防止数值误差导致的超出范围
#     angle = np.arccos(cos_theta)  # 弧度
#     return np.degrees(angle)  # 转换为度数

# # 主程序
# file_path = 'world_coor.txt'  # 替换为你的文件路径
# x_values, y_values = read_data(file_path)

# # 用于保存所有夹角的列表
# angles = []

# # 预测和评估
# for i in range(10, len(x_values)):
#     # 拟合前5个点
#     points = np.array([[x_values[j], y_values[j]] for j in range(i-10, i)])
    
#     # 计算贝塞尔曲线
#     bezier_points = bezier_curve(points)
    
#     # 计算切线方向
#     tangent_direction = calculate_tangent_direction(bezier_points)
    
#     # 真实值
#     if i+5 > len(x_values):
#         break
#     actual_next_points = np.array([[x_values[j], y_values[j]] for j in range(i-1, i + 2)])
    
#     # 计算后续五个真实点的平均方向
#     average_direction = calculate_average_direction(actual_next_points)
    
#     # 夹角
#     angle = calculate_angle_between(tangent_direction, average_direction)
#     angles.append(angle)  # 保存夹角
    
#     # 打印结果
#     print(f"Tangent Direction: {tangent_direction}")
#     print(f"Average Direction: {average_direction}")
#     print(f"Angle between Tangent and Average Direction: {angle:.2f} degrees")

#     # 可视化
#     plt.figure(figsize=(12, 8))
#     plt.plot(x_values[:i], y_values[:i], 'o-', label='Original Trajectory', markersize=5, color='blue')
#     plt.plot(bezier_points[:, 0], bezier_points[:, 1], 'r-', label='Bezier Curve', color='red')
#     plt.plot(actual_next_points[:, 0], actual_next_points[:, 1], 'g-', label='Actual Next Points', color='green')
#     plt.quiver(bezier_points[-1, 0], bezier_points[-1, 1], tangent_direction[0], tangent_direction[1], 
#                angles='xy', scale_units='xy', scale=1, color='orange', label='Tangent Direction')
#     plt.quiver(actual_next_points[0, 0], actual_next_points[0, 1], average_direction[0], average_direction[1], 
#                angles='xy', scale_units='xy', scale=1, color='purple', label='Average Direction')
#     plt.title('Trajectory with Bezier Curve and Directions')
#     plt.xlabel('X')
#     plt.ylabel('Y')
#     plt.legend()
#     plt.grid()
#     plt.axis('equal')
#     plt.show()

# # 将所有夹角保存到文本文件
# with open('angles_1_2_s3_5.txt', 'w') as f:
#     for angle in angles:
#         f.write(f"{angle:.2f}\n")  # 每个夹角写入一行


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.special import comb


sample = 1 #采样频率
num_points = 5 #用于拟合轨迹曲线的点的个数
num_avg = 2 #用于预测未来朝向的曲线上点的个数，< num_points


# 读取数据并提取 (x, y) 坐标
def read_data(file_path):
    x_values = []
    y_values = []
    flag = 1
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split(':')
            if len(parts) > 2:
                values = parts[-1].strip().split(',')
                if len(values) >= 4:
                    try:
                        x = float(values[0])
                        y = float(values[1])
                        if sample == 1:
                            x_values.append(x)
                            y_values.append(y)
                        else:
                            if flag % sample == 1:
                                x_values.append(x)
                                y_values.append(y)
                            flag += 1
                    except ValueError:
                        print(f"Invalid data: {values}")
    
    return np.array(x_values), np.array(y_values)

# 计算贝塞尔曲线
def bezier_curve(points, num_points=num_points):
    n = len(points) - 1
    t = np.linspace(0, 1, num_points)
    curve = np.zeros((num_points, 2))
    
    for i in range(n + 1):
        curve += np.outer(comb(n, i) * (t ** i) * ((1 - t) ** (n - i)), points[i])
    
    return curve

# 计算切线方向
# def calculate_tangent_direction(bezier_points):
#     last_point = bezier_points[-1]
#     second_last_point = bezier_points[-2]
    
#     tangent_vector = last_point - second_last_point
#     tangent_direction = tangent_vector / np.linalg.norm(tangent_vector)  # 单位向量
#     return tangent_direction


def calculate_tangent_direction(bezier_points, num_avg=num_avg):
    # 计算贝塞尔曲线的最后一个点的切线
    last_point = bezier_points[[-1]]
    second_last_point = bezier_points[-num_avg-1:-1]  #大约1s
    
    tangent_vector = last_point - second_last_point
    tangent_vector = np.mean(tangent_vector, axis=0)
    tangent_direction = tangent_vector / np.linalg.norm(tangent_vector)  # 单位向量
    return tangent_direction

# 计算平均方向
def calculate_average_direction(points):
    vectors = points[1:] - points[:-1]  # 计算相邻点的向量
    average_vector = np.mean(vectors, axis=0)
    average_direction = average_vector / np.linalg.norm(average_vector)  # 单位向量
    return average_direction

def calculate_2points_direction(points):
    vector = points[-1] - points[-2]
    if np.linalg.norm(vector) == 0:
        return [0, 0]
    direction = vector / np.linalg.norm(vector)  # 单位向量
    return direction

# 计算夹角
def calculate_angle(v1, v2):
    # 计算两个向量的模（长度）
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    # 如果遇到零向量，返回 190
    if norm_v1 == 0 or norm_v2 == 0:
        return 190

    # 计算点积
    dot_product = np.dot(v1, v2)

    # 计算夹角，使用np.clip确保由于浮点误差导致cosθ不超出[-1, 1]范围
    cos_theta = np.clip(dot_product / (norm_v1 * norm_v2), -1.0, 1.0)
    
    # 计算夹角，防止由于数值误差产生 NaN
    angle_rad = np.arccos(cos_theta)
    
    # 将弧度转换为角度
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg

# 主程序
file_path = 'NavigationService.g3log.20240914-185212.1325/world_coor.txt'  # 替换为你的文件路径
x_values, y_values = read_data(file_path)

# 打印所有数据
print("X values:", x_values)
print("Y values:", y_values)

# 打印数据范围
print(f"x_values range: {np.min(x_values)} to {np.max(x_values)}")
print(f"y_values range: {np.min(y_values)} to {np.max(y_values)}")

# 创建图形
fig, ax = plt.subplots(figsize=(np.max(x_values)-np.min(x_values)+2, np.max(y_values)-np.min(y_values)+2))
line_original, = ax.plot([], [], 'o-', label='Original Trajectory', markersize=5, color='blue')
line_bezier, = ax.plot([], [], 'r-', label='Bezier Curve', color='red')
line_actual, = ax.plot([], [], 'g-', label='Actual Next Points', color='green')
quiver_tangent = ax.quiver(0, 0, 0, 0, angles='xy', scale_units='xy', scale=1, color='green', label='Tangent Direction')
quiver_average = ax.quiver(0, 0, 0, 0, angles='xy', scale_units='xy', scale=1, color='orange', label='last2cur Direction')

# 设置图形属性
padding = 1  # 边距
ax.set_xlim(np.min(x_values) - padding, np.max(x_values) + padding)
ax.set_ylim(np.min(y_values) - padding, np.max(y_values) + padding)
ax.set_title('Trajectory with Bezier Curve and Directions')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.legend()
ax.grid()
ax.axis('equal')

angles = []
base_dirs = []
predict_dirs = []

# 调整边距
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

# 更新函数
def update(frame):
    if frame < 10 or frame >= len(x_values):
        return line_original, line_bezier, line_actual, quiver_tangent, quiver_average

    #lastframe2curframe 方向
    lastcur_points = np.array([[x_values[j], y_values[j]] for j in range(frame - 2, frame)])
    last2cur_direction = calculate_2points_direction(lastcur_points)
    base_dirs.append(last2cur_direction)
    print(f"=======base: {frame}")

    
    # 拟合前10个点
    points = np.array([[x_values[j], y_values[j]] for j in range(frame - 10, frame)])
    
    # 计算贝塞尔曲线
    bezier_points = bezier_curve(points)
    
    # 计算切线方向
    tangent_direction = calculate_tangent_direction(bezier_points)
    predict_dirs.append(tangent_direction)
    print(f"========pre: {frame}")
    
    # 真实值
    if frame + 5 > len(x_values):
        return line_original, line_bezier, line_actual, quiver_tangent, quiver_average
    actual_next_points = np.array([[x_values[j], y_values[j]] for j in range(frame - 1, frame + 3)])
    
    # 计算后续五个真实点的平均方向
    average_direction = calculate_average_direction(actual_next_points)

    
    # 夹角
    angle = calculate_angle(tangent_direction, average_direction)
    angles.append(angle)  # 保存夹角

    # 更新数据
    line_original.set_data(x_values[:frame], y_values[:frame])
    line_bezier.set_data(bezier_points[:, 0], bezier_points[:, 1])
    line_actual.set_data(actual_next_points[:, 0], actual_next_points[:, 1])
    
    # 更新箭头
    quiver_tangent.set_offsets(bezier_points[-1])
    quiver_tangent.set_UVC(tangent_direction[0]*2, tangent_direction[1]*2)
    
    # quiver_average.set_offsets(actual_next_points[0])
    # quiver_average.set_UVC(average_direction[0], average_direction[1])

    # quiver_average.set_offsets(lastcur_points[-1])
    # quiver_average.set_UVC(last2cur_direction[0]*2, last2cur_direction[1]*2)
    
    # 强制设置坐标轴范围
    ax.set_xlim(np.min(x_values) - padding, np.max(x_values) + padding)
    ax.set_ylim(np.min(y_values) - padding, np.max(y_values) + padding)
    
    return line_original, line_bezier, line_actual, quiver_tangent, quiver_average

# 创建动画
ani = FuncAnimation(fig, update, frames=len(x_values), blit=True, repeat=False)

# 保存动画
ani.save(f'NavigationService.g3log.20240914-185212.1325/wo_speed/angles_{num_avg}_s{sample}_{num_points}_pre.mp4', writer='ffmpeg', fps=4, dpi=100)  

# 显示动画
# plt.show()

# 将所有夹角保存到文本文件
with open(f'NavigationService.g3log.20240914-185212.1325/wo_speed/angles_{num_avg}_s{sample}_{num_points}.txt', 'w') as f:
    for angle in angles:
        f.write(f"{angle:.2f}\n")  # 每个夹角写入一行




# 保存base结果到txt文件
with open(f"NavigationService.g3log.20240914-185212.1325/wo_speed/angles_{num_avg}_s{sample}_{num_points}_base.txt", "w") as f:
    for i in range(len(base_dirs) - 1):
        v1 = np.array(base_dirs[i])
        v2 = np.array(base_dirs[i + 1])
        
        angle = calculate_angle(v1, v2)
        f.write(f"{angle:.2f}\n")

# 保存base结果到txt文件
with open(f"NavigationService.g3log.20240914-185212.1325/wo_speed/angles_{num_avg}_s{sample}_{num_points}_pre.txt", "w") as f:
    for i in range(len(predict_dirs) - 1):
        v1 = np.array(predict_dirs[i])
        v2 = np.array(predict_dirs[i + 1])
        
        angle = calculate_angle(v1, v2)
        f.write(f"{angle:.2f}\n")