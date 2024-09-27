#include <SFML/Graphics.hpp>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <regex>
#include <cmath>
#include <set>

template <typename T>
T clamp(T value, T min, T max) {
    return (value < min) ? min : (value > max) ? max : value;
}

class BezierPredictor {
    /*
    # H:[(x,y), (x,y), ...] 需要被拟合的轨迹点
    # B:[(x,y), (x,y), ...] 被过滤的轨迹点
    # DIR:[x_norm,y_norm] 估计的方向
    # h: int类型 H中的元素个数
    # m: bezier曲线上点的个数
    # n: bezier曲线上用于求DIR的点的个数
    #SPE: 过滤原地噪声点的速度阈值
    #ANG: 过滤原地噪声点的朝向夹角阈值

    return:
    {DIR, signal}
    DIR: (x, y) 表示朝向的单位向量
    signal: 0  正常返回并且改变了上一次的朝向
            1  正常返回但和上一次的朝向相同
            -1 用于拟合的点小于h
    */

    public:
        BezierPredictor(int h, int m, int n, double spe, double ang)
            : h(h), m(m), n(n), SPE(spe), ANG(ang) {}

        std::pair<std::vector<double>, int> bezier_DIR_predict(std::vector<std::pair<double, double>>& H, 
                                                            std::vector<std::pair<double, double>>& B, 
                                                            std::vector<double> DIR = {}) {
            if (H.size() < h) {
                std::cout << "Needs " << (h - H.size()) << " more points!" << std::endl;
                return {DIR, -1}; // Return signal -1 if not enough points
            } else if (H.size() > h) {
                H.erase(H.begin()); // Remove the first element
            }

            // 创建一个 vector 来保存 H 去重后的点
            std::vector<std::pair<double, double>> H_unique;
            for (const auto& point : H) {
                // 只添加不在 H_unique 中的点
                if (std::find(H_unique.begin(), H_unique.end(), point) == H_unique.end()) {
                    H_unique.push_back(point);
                }
            }

            // 创建一个新的容器来保存 H - B 的结果
            std::vector<std::pair<double, double>> H_B;
            // 使用 std::copy_if 将不在 B 中的点复制到 H_B
            std::copy_if(H_unique.begin(), H_unique.end(), std::back_inserter(H_B), [&](const std::pair<double, double>& point) {
                return std::find(B.begin(), B.end(), point) == B.end(); // 只保留不在 B 中的点
            });


            bool Zero = std::all_of(DIR.begin(), DIR.end(), [](double value) {
                return value == 0.0; // 检查每个值是否为 0
            });
            if (Zero) {  //如果无上一次估计的结果
                std::cout << "===============B_H:" << H_B.size() << std::endl;
                auto bezier_points = bezier_curve(H_B);
                DIR = calculate_tangent_direction(bezier_points);
                std::cout << "Direction: (" << DIR[0] << ", " << DIR[1] << ")" << std::endl;
                return {DIR, 0}; // Return signal 0 for success 

            } else {
                auto [DIR_base, SPE_base] = calculate_2points_direction_speed(H);
                double ANG_base = calculate_angle(DIR, DIR_base);

                if (ANG_base > ANG && SPE_base < SPE) {
                    if (SPE_base != 0) B.push_back(H.back());
                    std::cout << "Direction: (" << DIR[0] << ", " << DIR[1] << ")" << "(not modify)" << std::endl;
                    return {DIR, 1}; // Return signal 0 for success, but not modify DIR
                }
                else {
                    auto bezier_points = bezier_curve(H_B);
                    DIR = calculate_tangent_direction(bezier_points);
                    std::cout << "Direction: (" << DIR[0] << ", " << DIR[1] << ")" << std::endl;
                    return {DIR, 0}; // Return signal 0 for success 
                }
                
            }

            
        }

    private:
        int h, m, n;
        double SPE, ANG;

        std::vector<std::pair<double, double>> bezier_curve(const std::vector<std::pair<double, double>>& points) {
            int n = points.size() - 1;
            std::vector<std::pair<double, double>> curve(m);
            std::vector<double> t(m);
            
            for (int i = 0; i < m; ++i) {
                t[i] = static_cast<double>(i) / (m - 1);
            }

            for (int i = 0; i <= n; ++i) {
                double binom = comb(n, i);
                for (int j = 0; j < m; ++j) {
                    double coeff = binom * pow(t[j], i) * pow(1 - t[j], n - i);
                    curve[j].first += coeff * points[i].first;
                    curve[j].second += coeff * points[i].second;
                }
            }

            return curve;
        }

        double comb(int n, int k) {
            if (k > n) return 0;
            if (k == 0 || k == n) return 1;
            double res = 1;
            for (int i = 0; i < k; ++i) {
                res *= (n - i);
                res /= (i + 1);
            }
            return res;
        }

        std::vector<double> calculate_tangent_direction(const std::vector<std::pair<double, double>>& bezier_points) {
            auto last_point = bezier_points.back();
            auto second_last_point = bezier_points[bezier_points.size() - 2];

            std::vector<double> tangent_vector = { last_point.first - second_last_point.first, 
                                                    last_point.second - second_last_point.second };
            double norm = std::sqrt(tangent_vector[0] * tangent_vector[0] + tangent_vector[1] * tangent_vector[1]);
            if (norm == 0) return {0, 0}; // Avoid division by zero
            return { tangent_vector[0] / norm, tangent_vector[1] / norm }; // Unit vector
        }

        std::pair<std::vector<double>, double> calculate_2points_direction_speed(const std::vector<std::pair<double, double>>& points) {
            auto vector = std::vector<double>{ points.back().first - points[points.size() - 2].first,
                                                points.back().second - points[points.size() - 2].second };
            double speed = std::sqrt(vector[0] * vector[0] + vector[1] * vector[1]);
            if (speed == 0) return { {0, 0}, 0 };
            return { { vector[0] / speed, vector[1] / speed }, speed }; // Unit vector and speed
        }

        double calculate_angle(const std::vector<double>& v1, const std::vector<double>& v2) {
            double norm_v1 = std::sqrt(v1[0] * v1[0] + v1[1] * v1[1]);
            double norm_v2 = std::sqrt(v2[0] * v2[0] + v2[1] * v2[1]);

            if (norm_v1 == 0 || norm_v2 == 0) return 190; // Return 190 for zero vector

            double dot_product = v1[0] * v2[0] + v1[1] * v2[1];
            double cos_theta = clamp(dot_product / (norm_v1 * norm_v2), -1.0, 1.0);
            double angle_rad = std::acos(cos_theta);
            return angle_rad * (180.0 / M_PI); // Convert to degrees
        }
};


// 函数用于从文件中读取 (x, y) 数据
std::vector<std::pair<double, double>> read_xy_from_file(const std::string& filename) {
    std::vector<std::pair<double, double>> xy_data;
    std::ifstream file(filename);
    std::string line;
    std::regex regex(R"(:\s*([\d.-]+),([\d.-]+))");

    while (std::getline(file, line)) {
        std::smatch match;
        if (std::regex_search(line, match, regex)) {
            double x = std::stod(match[1].str());
            double y = std::stod(match[2].str());
            xy_data.emplace_back(x, y);
        }
    }

    return xy_data;
}


void drawThickLine(sf::RenderWindow& window, sf::Vector2f start, sf::Vector2f end, float thickness, sf::Color color) {
    sf::RectangleShape line;
    
    // 计算线段的方向
    sf::Vector2f direction = end - start;
    float length = std::sqrt(direction.x * direction.x + direction.y * direction.y);
    if (length == 0) return; // 避免除以零

    // 设置矩形的大小
    line.setSize(sf::Vector2f(length, thickness));
    
    // 计算角度并设置旋转
    float angle = std::atan2(direction.y, direction.x) * 180 / 3.14159f;
    line.setRotation(angle);
    
    // 设置位置
    line.setPosition(start);
    
    // 设置颜色
    line.setFillColor(color);
    
    // 绘制矩形
    window.draw(line);
}



std::vector<double> calculateUnitDirectionVector(const std::pair<double, double>& point_last, const std::pair<double, double>& point_cur) {
    double directionX = point_cur.first - point_last.first;
    double directionY = point_cur.second - point_last.second;

    // 检查两个点是否重合
    if (directionX == 0 && directionY == 0) {
        return {0, 0}; // 返回 (0, 0) 如果两个点重合
    }

    // 计算方向向量的长度
    double length = std::sqrt(directionX * directionX + directionY * directionY);
    
    // 返回单位方向向量
    return {directionX / length, directionY / length};
}


int main() {
    std::string filename = "/home/dx/direction_prediction/Phil/NavigationService.g3log.20240920-164941.2616/world_coor.txt"; // 替换为您的文件名
    std::vector<std::pair<double, double>> xy_data = read_xy_from_file(filename);

    BezierPredictor predictor(10, 5, 2, 0.05, 90);
    std::vector<std::pair<double, double>> H; // 存储输入点
    std::vector<std::pair<double, double>> B; // 存储过滤点
    std::vector<double> DIR = {0, 0}; // 存储方向
    std::vector<double> Last2Cur; // base方案估计的方向

    // 用于存储所有读取的点
    std::vector<std::pair<double, double>> all_points;

    // SFML 窗口设置
    sf::RenderWindow window(sf::VideoMode(800, 600), "Bezier Direction Visualization");
    window.setFramerateLimit(6);

    // 计算数据范围
    double minX = std::numeric_limits<double>::max();
    double maxX = std::numeric_limits<double>::min();
    double minY = std::numeric_limits<double>::max();
    double maxY = std::numeric_limits<double>::min();

    for (const auto& point : xy_data) {
        minX = std::min(minX, point.first);
        maxX = std::max(maxX, point.first);
        minY = std::min(minY, point.second);
        maxY = std::max(maxY, point.second);
    }

    // 计算缩放因子和偏移量
    double scaleX = 800 / (maxX - minX);
    double scaleY = 600 / (maxY - minY);
    double scale = std::min(scaleX, scaleY); // 保持比例

    double offsetX = -minX * scale;
    double offsetY = -minY * scale;

    // 主循环
    while (window.isOpen()) {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed)
                window.close();
        }

        window.clear(sf::Color::White);

        // 绘制所有读取的点的轨迹
        for (size_t i = 1; i < all_points.size(); ++i) {
            sf::Vertex line[] = {
                sf::Vertex(sf::Vector2f((all_points[i - 1].first * scale) + offsetX, (all_points[i - 1].second * scale) + offsetY), sf::Color::Blue),
                sf::Vertex(sf::Vector2f((all_points[i].first * scale) + offsetX, (all_points[i].second * scale) + offsetY), sf::Color::Blue)
            };
            window.draw(line, 2, sf::Lines);
        }

        if (!H.empty()) {
            auto [direction, signal] = predictor.bezier_DIR_predict(H, B, DIR);
            DIR = direction;
            if (signal == 0 || signal == 1) {
                // 绘制方向向量
                sf::Vector2f start((all_points.back().first * scale) + offsetX, (all_points.back().second * scale) + offsetY);
                sf::Vector2f end(start.x + direction[0] * 20, start.y + direction[1] * 20);
                drawThickLine(window, start, end, 2.0, sf::Color::Red);
            }

            Last2Cur = calculateUnitDirectionVector(all_points[all_points.size() - 2], all_points.back());
            sf::Vector2f start((all_points.back().first * scale) + offsetX, (all_points.back().second * scale) + offsetY);
            sf::Vector2f end(start.x + Last2Cur[0] * 20, start.y + Last2Cur[1] * 20);
            drawThickLine(window, start, end, 2.0, sf::Color::Black);

        }

        window.display();

        // 读取下一个点
        if (!xy_data.empty()) {
            // 将新读取的点添加到 all_points 中
            all_points.push_back(xy_data.front());
            H.push_back(xy_data.front());
            xy_data.erase(xy_data.begin());
        }
    }

    return 0;
}
