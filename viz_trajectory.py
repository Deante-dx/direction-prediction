import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 初始化列表以存储提取的数据
x_values = []
y_values = []

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
                if flag % 2 == 1:
                    x = float(values[0])
                    y = float(values[1])
                    x_values.append(x)
                    y_values.append(y)
                flag += 1

# 创建图形和坐标轴
fig, ax = plt.subplots(figsize=(max(x_values)-min(x_values) + 2, max(y_values)-min(y_values)+2))  # 增加图形的大小
ax.set_title('Trajectory Plot')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.grid()
ax.axis('equal')  # 保持x和y轴比例相同

# 初始化空的散点图
line, = ax.plot([], [], marker='o', linestyle='-', color='b')

# 设置坐标轴的范围
ax.set_xlim(min(x_values)-1, max(x_values)+1)
ax.set_ylim(min(y_values)-1, max(y_values)+1)
print(min(x_values)-1, max(x_values)+1)
print(min(y_values)-1, max(y_values)+1)

# 初始化函数
def init():
    line.set_data([], [])
    return line,

# 更新函数
def update(frame):
    line.set_data(x_values[:frame + 1], y_values[:frame + 1])
    ax.set_xlim(min(x_values)-1, max(x_values)+1)
    ax.set_ylim(min(y_values)-1, max(y_values)+1)
    return line,

# 创建动画
ani = FuncAnimation(fig, update, frames=len(x_values), init_func=init, blit=True, interval=20)

# 显示动画
plt.show()
